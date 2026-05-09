"""qubots-leaderboard HuggingFace Space.

A read-only Gradio frontend over the leaderboard.json that the GitHub
Actions workflow at github.com/leonidas1312/qubots-leaderboard regenerates
on every PR/push/cron run.

Single source of truth is the GitHub repo; this Space fetches the latest
JSON at startup and on demand. To submit a solver, open a PR on the
GitHub repo (link in the header).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


GITHUB_REPO = "leonidas1312/qubots-leaderboard"
LEADERBOARD_JSON_URL = (
    f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/leaderboard.json"
)
GITHUB_REPO_URL = f"https://github.com/{GITHUB_REPO}"
QUBOTS_REPO_URL = "https://github.com/leonidas1312/qubots"


# ---------- data loading -----------------------------------------------------


def _empty_state(error: str | None = None) -> dict[str, Any]:
    return {
        "suite_name": "qubots-flagship",
        "suite_description": "(leaderboard data unavailable)",
        "generated_at": "",
        "benchmarks": [],
        "submissions": [],
        "results": [],
        "_error": error,
    }


def fetch_leaderboard() -> dict[str, Any]:
    try:
        request = urllib.request.Request(
            LEADERBOARD_JSON_URL,
            headers={"Cache-Control": "no-cache"},
        )
        with urllib.request.urlopen(request, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        return _empty_state(error=f"{type(exc).__name__}: {exc}")


# ---------- DataFrame builders ----------------------------------------------


def _format_value(v: float) -> float:
    return float(round(v, 6))


def _link_submitter(submitter: str) -> str:
    return f"[@{submitter}](https://github.com/{submitter})"


def header_markdown(report: dict[str, Any]) -> str:
    err = report.get("_error")
    if err:
        return (
            f"# qubots leaderboard\n\n"
            f"⚠️ **Could not load leaderboard data.** "
            f"`{err}`\n\nTry the Refresh button, or check the source repo."
        )

    n_subs = len(report.get("submissions", []))
    n_benches = len(report.get("benchmarks", []))
    suite = report.get("suite_name", "qubots-flagship")
    desc = report.get("suite_description", "")

    generated = report.get("generated_at", "")
    if generated:
        try:
            ts = datetime.fromisoformat(generated.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            age_hours = (now - ts.astimezone(timezone.utc)).total_seconds() / 3600
            if age_hours < 1:
                age = "just now"
            elif age_hours < 24:
                age = f"{int(age_hours)}h ago"
            else:
                age = f"{int(age_hours/24)}d ago"
            generated_str = f"Generated {age} ({generated})"
        except ValueError:
            generated_str = f"Generated {generated}"
    else:
        generated_str = ""

    return (
        f"# 🏆 qubots leaderboard — `{suite}`\n\n"
        f"_{desc}_\n\n"
        f"**{n_subs}** submission(s) × **{n_benches}** benchmark(s). {generated_str}\n\n"
        f"📦 [Source repo]({GITHUB_REPO_URL}) · "
        f"🤖 [Powered by qubots]({QUBOTS_REPO_URL}) · "
        f"➕ [Submit your solver]({GITHUB_REPO_URL}/blob/main/CONTRIBUTING.md)"
    )


def summary_dataframe(report: dict[str, Any]) -> pd.DataFrame:
    benchmarks = report.get("benchmarks", [])
    submissions = report.get("submissions", [])
    results = report.get("results", [])
    if not benchmarks or not submissions:
        return pd.DataFrame()

    counts: dict[str, dict[str, int]] = {}
    for sub in submissions:
        counts[sub["submission_id"]] = {"#1": 0, "#2": 0, "#3": 0}

    for bench in benchmarks:
        rows = [r for r in results if r["benchmark_name"] == bench]
        ranked = sorted(
            rows,
            key=lambda r: (r["mean_best_value"], r["mean_runtime_seconds"], r["submission_id"]),
        )
        for index, row in enumerate(ranked):
            sid = row["submission_id"]
            if index == 0:
                counts[sid]["#1"] += 1
            elif index == 1:
                counts[sid]["#2"] += 1
            elif index == 2:
                counts[sid]["#3"] += 1

    table_rows = []
    for sub in submissions:
        sid = sub["submission_id"]
        counts_for = counts.get(sid, {"#1": 0, "#2": 0, "#3": 0})
        table_rows.append(
            {
                "Submission": sub["display_name"],
                "Submitter": _link_submitter(sub["submitter"]),
                "🥇 #1": counts_for["#1"],
                "🥈 #2": counts_for["#2"],
                "🥉 #3": counts_for["#3"],
                "Total": counts_for["#1"] + counts_for["#2"] + counts_for["#3"],
            }
        )

    df = pd.DataFrame(table_rows)
    if df.empty:
        return df
    return df.sort_values(
        ["🥇 #1", "🥈 #2", "🥉 #3", "Submission"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)


def benchmark_dataframe(report: dict[str, Any], bench_name: str) -> pd.DataFrame:
    if not bench_name:
        return pd.DataFrame()

    rows = [r for r in report.get("results", []) if r["benchmark_name"] == bench_name]
    if not rows:
        return pd.DataFrame()

    ranked = sorted(
        rows,
        key=lambda r: (r["mean_best_value"], r["mean_runtime_seconds"], r["submission_id"]),
    )

    table_rows = []
    for index, row in enumerate(ranked, start=1):
        table_rows.append(
            {
                "Rank": index,
                "Submission": row["display_name"],
                "Submitter": _link_submitter(row["submitter"]),
                "Mean best value": _format_value(row["mean_best_value"]),
                "Mean runtime (s)": _format_value(row["mean_runtime_seconds"]),
                "Success rate": f"{row['success_rate']:.0%}",
                "Runs": row["num_runs"],
            }
        )
    return pd.DataFrame(table_rows)


def submissions_dataframe(report: dict[str, Any]) -> pd.DataFrame:
    rows = []
    for sub in report.get("submissions", []):
        params = sub.get("parameters", {}) or {}
        params_str = ", ".join(f"{k}={v}" for k, v in params.items()) if params else "—"
        rows.append(
            {
                "Display name": sub["display_name"],
                "Submitter": _link_submitter(sub["submitter"]),
                "Spec": f"`{sub['spec']}`",
                "Parameters": params_str,
            }
        )
    return pd.DataFrame(rows)


def runtime_value_plot(report: dict[str, Any], bench_name: str) -> go.Figure:
    rows = [r for r in report.get("results", []) if r["benchmark_name"] == bench_name]
    if not rows:
        fig = go.Figure()
        fig.update_layout(title="(no data)")
        return fig

    df = pd.DataFrame(
        [
            {
                "Submission": r["display_name"],
                "Submitter": r["submitter"],
                "Mean best value": _format_value(r["mean_best_value"]),
                "Mean runtime (s)": _format_value(r["mean_runtime_seconds"]),
                "Success rate": r["success_rate"],
            }
            for r in rows
        ]
    )

    fig = px.scatter(
        df,
        x="Mean runtime (s)",
        y="Mean best value",
        color="Submission",
        hover_data=["Submitter", "Success rate"],
        title=f"{bench_name}: best value vs. runtime (lower-left is better)",
    )
    fig.update_traces(marker=dict(size=14, line=dict(width=1, color="DarkSlateGrey")))
    fig.update_layout(
        legend=dict(title="", yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig


# ---------- Gradio app -------------------------------------------------------


def build_app() -> gr.Blocks:
    initial_state = fetch_leaderboard()
    initial_benches = initial_state.get("benchmarks", []) or [""]

    with gr.Blocks(
        theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="purple"),
        title="qubots leaderboard",
    ) as demo:
        state = gr.State(initial_state)

        header = gr.Markdown(header_markdown(initial_state))

        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh from GitHub", size="sm", scale=0)

        with gr.Tabs():
            with gr.Tab("📊 Summary"):
                gr.Markdown(
                    "_Podium count across all benchmarks. "
                    "Sort the columns to see who dominates where._"
                )
                summary_table = gr.DataFrame(
                    value=summary_dataframe(initial_state),
                    interactive=False,
                    wrap=True,
                    datatype=["str", "markdown", "number", "number", "number", "number"],
                )

            with gr.Tab("🏁 Per benchmark"):
                bench_selector = gr.Dropdown(
                    choices=initial_benches,
                    value=initial_benches[0] if initial_benches else None,
                    label="Benchmark",
                    interactive=True,
                )
                bench_table = gr.DataFrame(
                    value=benchmark_dataframe(
                        initial_state,
                        initial_benches[0] if initial_benches else "",
                    ),
                    interactive=False,
                    wrap=True,
                    datatype=["number", "str", "markdown", "number", "number", "str", "number"],
                )
                bench_plot = gr.Plot(
                    value=runtime_value_plot(
                        initial_state,
                        initial_benches[0] if initial_benches else "",
                    )
                )

            with gr.Tab("📜 Submissions"):
                gr.Markdown(
                    "_Each row is one entry in the leaderboard. "
                    "`spec` pins to a github SHA so re-running the leaderboard "
                    "today or in a year produces identical solver code._"
                )
                submissions_table = gr.DataFrame(
                    value=submissions_dataframe(initial_state),
                    interactive=False,
                    wrap=True,
                    datatype=["str", "markdown", "markdown", "str"],
                )

            with gr.Tab("ℹ️ About"):
                gr.Markdown(
                    f"""
### What is qubots?

[qubots]({QUBOTS_REPO_URL}) is a Python framework for **pluggable optimization
problems and solvers**. Every problem and every solver is a small
git-resolvable repo with a `qubots.yaml` manifest. Compose them locally,
benchmark them, share them.

### What is this leaderboard?

It runs every solver in [submissions/]({GITHUB_REPO_URL}/tree/main/submissions)
against every benchmark in [benchmarks/]({GITHUB_REPO_URL}/tree/main/benchmarks)
and ranks them. The ranking is reproducible — each submission pins to a
40-character commit SHA, and the GitHub Actions workflow re-runs on every PR,
push to main, and weekly cron.

### How do I submit my solver?

Open a PR on the [GitHub repo]({GITHUB_REPO_URL}) adding one YAML file under
`submissions/<your-username>/<solver>.yaml`. The PR template walks you through
it. Full guide: [CONTRIBUTING.md]({GITHUB_REPO_URL}/blob/main/CONTRIBUTING.md).

### How is the score computed?

Per qubots convention, lower `best_value` is better (max-sense problems are
internally negated by the structured solvers). For each benchmark, submissions
are ranked by `mean_best_value`, with ties broken by `mean_runtime_seconds`.
The Summary tab counts podium finishes (#1 / #2 / #3) across every benchmark.
"""
                )

        # Refresh wiring
        def _on_refresh() -> tuple[Any, ...]:
            new_state = fetch_leaderboard()
            new_benches = new_state.get("benchmarks", []) or [""]
            first_bench = new_benches[0] if new_benches else ""
            return (
                new_state,
                header_markdown(new_state),
                summary_dataframe(new_state),
                gr.Dropdown(choices=new_benches, value=first_bench),
                benchmark_dataframe(new_state, first_bench),
                runtime_value_plot(new_state, first_bench),
                submissions_dataframe(new_state),
            )

        refresh_btn.click(
            fn=_on_refresh,
            outputs=[
                state,
                header,
                summary_table,
                bench_selector,
                bench_table,
                bench_plot,
                submissions_table,
            ],
        )

        # Per-benchmark wiring
        def _on_bench_change(report: dict[str, Any], bench: str) -> tuple[Any, ...]:
            return benchmark_dataframe(report, bench), runtime_value_plot(report, bench)

        bench_selector.change(
            fn=_on_bench_change,
            inputs=[state, bench_selector],
            outputs=[bench_table, bench_plot],
        )

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch()

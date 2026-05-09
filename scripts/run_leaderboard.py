"""CI driver: run the flagship suite against every submission and emit
LEADERBOARD.md + leaderboard.json at the repo root.

Designed to be invoked by .github/workflows/benchmark.yml. Can also be run
locally:

    python scripts/run_leaderboard.py

Or, equivalently, via the qubots CLI:

    qubots leaderboard --suite benchmarks/flagship.yaml \\
                       --submissions submissions/ \\
                       --out LEADERBOARD.md --json leaderboard.json \\
                       --trust-remote-code
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--suite",
        default="benchmarks/flagship.yaml",
        help="Path to the leaderboard suite YAML.",
    )
    parser.add_argument(
        "--submissions",
        default="submissions",
        help="Directory of submission YAMLs (recursive).",
    )
    parser.add_argument(
        "--out",
        default="LEADERBOARD.md",
        help="Output path for the markdown leaderboard.",
    )
    parser.add_argument(
        "--json",
        default="leaderboard.json",
        dest="json_path",
        help="Output path for the JSON leaderboard.",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=1,
        help="Runs per dataset instance.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility.",
    )
    parser.add_argument(
        "--no-trust-remote",
        action="store_true",
        help="Refuse to load remote github: submission specs (CI only).",
    )
    args = parser.parse_args()

    if not args.no_trust_remote:
        # Submissions point at github: specs by design; CI installs the
        # declared dependencies into an isolated venv before invoking
        # this script (see .github/workflows/benchmark.yml). The trust
        # decision is therefore explicit in the workflow, not silent.
        os.environ.setdefault("QUBOTS_TRUST_REMOTE_CODE", "1")

    try:
        from qubots.leaderboard import (
            load_submissions_from_dir,
            load_suite,
            run_leaderboard,
            write_report,
        )
    except ImportError as exc:
        print("[FAIL] qubots is not installed in this environment.", file=sys.stderr)
        print("Install with: pip install qubots[highs,cpsat]", file=sys.stderr)
        raise SystemExit(2) from exc

    suite_path = Path(args.suite).resolve()
    submissions_path = Path(args.submissions).resolve()
    out_path = Path(args.out).resolve()
    json_path = Path(args.json_path).resolve()

    if not suite_path.exists():
        print(f"[FAIL] Suite not found: {suite_path}", file=sys.stderr)
        return 1
    if not submissions_path.exists():
        print(f"[FAIL] Submissions not found: {submissions_path}", file=sys.stderr)
        return 1

    suite = load_suite(suite_path)
    submissions = load_submissions_from_dir(submissions_path)
    if not submissions:
        print(f"[FAIL] No submissions found under {submissions_path}", file=sys.stderr)
        return 1

    print(
        f"Running {len(submissions)} submission(s) × "
        f"{len(suite.benchmarks)} benchmark(s) ..."
    )
    report = run_leaderboard(
        suite,
        submissions,
        repeats=args.repeats,
        seed=args.seed,
    )

    written_json, written_md = write_report(
        report, json_path=json_path, markdown_path=out_path
    )
    if written_md:
        print(f"Markdown written: {written_md}")
    if written_json:
        print(f"JSON written:     {written_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

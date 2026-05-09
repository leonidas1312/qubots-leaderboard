---
title: qubots leaderboard
emoji: 🏆
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 5.0.1
app_file: app.py
pinned: false
license: mit
short_description: Reproducible benchmarks for pluggable optimization solvers
---

# qubots leaderboard

Live frontend for the [qubots-leaderboard](https://github.com/leonidas1312/qubots-leaderboard)
repo. Reads the `leaderboard.json` produced by the GitHub Actions runner and
renders sortable tables and a runtime/value scatter plot.

To **submit your solver**, open a PR on the
[GitHub repo](https://github.com/leonidas1312/qubots-leaderboard) — see
[CONTRIBUTING.md](https://github.com/leonidas1312/qubots-leaderboard/blob/main/CONTRIBUTING.md).

This Space is auto-synced from the `space/` subdirectory of the GitHub repo on
every push to `main` (workflow: `.github/workflows/sync_space.yml`). Don't edit
files in this Space directly — they will be overwritten on the next sync.

# Contributing to qubots-leaderboard

There are three ways to contribute:

1. **Submit a solver** — your optimizer competes on the existing benchmark suite.
2. **Submit a benchmark** — add a new problem dataset for everyone to compete on.
3. **Improve the infrastructure** — CI, scoring, docs.

## 1. Submit a solver

### Prerequisites

Your solver must be a valid [qubots](https://github.com/leonidas1312/qubots) optimizer component:

- A public GitHub repo (any owner)
- Contains a `qubots.yaml` with `type: optimizer`, `entrypoint: qubot.py:YourClass`, and a `requirements:` list of pip specs your solver needs (e.g. `["highspy>=1.7"]`)
- The entrypoint class subclasses `BaseOptimizer` and implements `optimize(problem) -> Result`

If you don't have a component yet:

```bash
pip install qubots
qubots new optimizer --name my_solver --flavor blackbox   # or --flavor milp
# edit qubot.py to wire in your real solver
qubots validate my_solver
git init my_solver && cd my_solver && git add . && git commit -m "init"
# push to GitHub
```

### Steps

1. **Pin a commit**: in your solver's repo, run `git rev-parse HEAD` to get the full 40-char SHA. The leaderboard pins to a SHA, not a branch — branches can move silently.

2. **Add one file** under `submissions/<your-github-username>/<solver-name>.yaml`:

   ```yaml
   qubots_submission_schema_version: 1
   spec: github:your-username/your-repo@a1b2c3d4...:path/inside/repo
   submitter: your-username
   display_name: "My Solver (default config)"
   parameters:        # optional: per-submission optimizer params
     time_limit_seconds: 30
   ```

   - `spec` follows the `github:owner/repo@<full-sha>:<subdir>` format. The subdir is optional; omit it if your `qubots.yaml` is at the repo root.
   - `display_name` is what shows up on the leaderboard. Keep it short and version-y (e.g. `"HiGHS v1.7 (default)"`, `"My ALNS, 60s budget"`).
   - You can submit multiple entries with different parameter configurations as long as `display_name` differs.

3. **Open a PR**. CI runs automatically:
   - Validates your YAML and resolves the spec.
   - Creates an isolated venv, installs `qubots` + your solver's declared `requirements:`.
   - Runs `qubots leaderboard --suite benchmarks/flagship.yaml --submissions <your-yaml>`.
   - Posts the results as a comment.

4. **A maintainer reviews** (typically <72 hours). On merge, CI re-runs the full leaderboard and commits updated results to `main`.

### What gets rejected

- Specs that don't resolve, validate, or instantiate.
- Solvers that don't subclass `BaseOptimizer` or don't implement `optimize`.
- Dependency lists that pull in commercial-license-required solvers without an explicit opt-in flag.
- Solvers that try to detect the benchmark instance and short-circuit (you'll be permanently banned).
- Anything that breaks the harness or the runner.

## 2. Submit a benchmark

A benchmark is a qubots **dataset YAML** + the data files it references.

1. Add your dataset under `benchmarks/instances/<your-benchmark>.yaml` (and any `.mps` / `.csv` / etc. it points at).
2. Edit `benchmarks/flagship.yaml` to include it:

   ```yaml
   benchmarks:
     - name: your_benchmark
       dataset: instances/your-benchmark.yaml
   ```

3. Open a PR. The bar:
   - Dataset is meaningful (a published instance, a clearly-defined toy, or a real business case with synthetic data). No "random graph with 5 nodes" filler.
   - Tractable for at least one of the existing solvers — leaderboards with all submissions timing out are noise.
   - Clear license. Public-domain or permissively-licensed data preferred.

The flagship suite stays small on purpose — adding a new benchmark requires raising the bar, not just appending. Maintainers may suggest your benchmark belongs in a *secondary* suite instead.

## 3. Improve the infrastructure

PRs welcome on workflows, scoring formulas, and docs. Architectural changes (e.g. new score columns, suite stratification, badge generation) — please open a discussion first.

## Code of conduct

Be excellent to each other. Bad-faith submissions, harassment of contributors, or attempts to game the rankings result in a ban.

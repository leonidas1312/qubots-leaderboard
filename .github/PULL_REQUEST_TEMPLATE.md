<!--
Thank you for contributing! Please pick a section below and delete the others.
-->

## New solver submission

- **Solver name (display_name):**
- **Submission file:** `submissions/<your-username>/<solver>.yaml`
- **Spec (github:owner/repo@<sha>:subdir):**
- **Declared `requirements:` in the upstream `qubots.yaml`:**
- **One-line description of the approach** (e.g. "ALNS with 60s budget", "HiGHS with custom presolve"):

Checklist:
- [ ] My component repo passes `qubots validate <spec> --trust-remote-code` locally.
- [ ] I pinned to a full 40-character SHA (not a branch / tag).
- [ ] My `requirements:` list is minimal and free of commercial-license-required deps.
- [ ] I'm not detecting benchmark instances or short-circuiting them.

---

## New benchmark submission

- **Benchmark name:**
- **Dataset YAML:** `benchmarks/instances/<name>.yaml`
- **Source / reference (paper, repo, dataset URL):**
- **License of the data:**

Checklist:
- [ ] At least one existing solver in the leaderboard runs to completion on this benchmark.
- [ ] The data file (if any) is under 1 MB or hosted externally with a stable URL.
- [ ] I added an entry to `benchmarks/flagship.yaml` (or a secondary suite YAML).

---

## Infrastructure / docs

What does this PR change and why?

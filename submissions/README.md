# submissions/

One YAML per submission, organized by submitter.

```
submissions/
  <submitter>/
    <solver-name>.yaml
```

To submit your own solver, see [CONTRIBUTING.md](../CONTRIBUTING.md).

## Schema

```yaml
qubots_submission_schema_version: 1
spec: github:owner/repo@<full-sha>:subdir   # or a local path during dev
submitter: your-github-username
display_name: "Solver Name (config note)"
parameters:
  time_limit_seconds: 30
```

- `spec` pins to a full 40-char SHA in production. Branch / tag refs are
  accepted but discouraged because upstream can move them silently.
- `display_name` is what shows up on the leaderboard. Keep it short.
- `parameters` are passed to the optimizer at runtime. Use this to
  submit several configurations of the same solver under different
  display names.

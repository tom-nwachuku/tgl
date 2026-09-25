# Release checklist

Run at the end of every Attack Mode Ship phase.

- [ ] Every slice reviewed against the spec; implementations quote their spec lines
- [ ] Red-team verification record written: what was actually seen, what broke
- [ ] Tests green (or a written note saying why not, and what covers the gap)
- [ ] No hardcoded user identity, no secrets, no debug scaffolding left behind
- [ ] LEDGER.md updated: shipped version, one honest paragraph on what was learned
- [ ] Human sign-off on the release recorded (date, version)

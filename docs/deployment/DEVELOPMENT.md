# IBVAP Engineering & Development Guidelines

All team members and AI coding agents working on this repository must adhere to the following rules:

---

## Core Engineering Rules

1. **Never commit secrets**: Do not commit API keys, passwords, private tokens, or credentials. Use `.env.example` for placeholders.
2. **Never directly push to `main`**: All changes must go through feature branches and pull requests.
3. **Use focused feature branches**: Name branches according to component and feature (e.g., `feature/ai-yolo-detection`, `feature/backend-events-api`).
4. **Keep commits focused and atomic**: Commit logical units of work with clear commit messages.
5. **Pull before starting work**: Keep your branch up to date with `main` to minimize merge conflicts.
6. **Open a PR before merging**: Code reviews or sanity checks must be performed before merging into `main`.
7. **Respect section ownership**: Do not modify another team's module without coordination with the section lead.
8. **Keep interfaces documented**: Any change to API schemas or data structures must be updated in `docs/api/api-contract.md`.
9. **Write tests for important logic**: Unit test core domain logic (point-in-polygon, SHA-256 calculation, state transitions).
10. **Do not add dependencies without justification**: Avoid adding bloat or unneeded packages to `requirements.txt` or `package.json`.
11. **Do not claim performance/accuracy without measurements**: Always validate numbers (FPS, latency, precision) with reproducible benchmarks recorded in `docs/testing/benchmark-results.md`.
12. **Preserve working code**: Test thoroughly before opening pull requests to ensure core MVP pipeline remains unbroken.

# IBVAP — Guidelines & Protocols for AI Coding Agents

All AI coding assistants (including Antigravity, Claude Code, OpenAI Codex, or human pair programmers) working on this repository MUST strictly follow the directives in this document.

---

## 1. Primary Rule & Source of Truth

> **`PROJECT.md` is the SINGLE MASTER SOURCE OF TRUTH.**
> Before modifying any architecture, schema, or module code, you MUST read `PROJECT.md` to confirm the scope of the SIH Internal-Round MVP.

---

## 2. Golden Principles for AI Agents

1. **Phase-Gated Execution**: Implement ONLY the requested phase. Do NOT automatically proceed to future phases without user instruction.
2. **Inspect Before Modifying**: Use code search and file viewing tools to inspect existing interfaces before writing new code.
3. **Preserve Working Interfaces**: Do not break existing data contracts (`NormalizedDetection`, `Track`, `EventPayload`).
4. **Never Guess or Fabricate Numbers**: Never fabricate benchmark figures (FPS, latency, precision, hash speed). Report only empirically measured results.
5. **No Scope Creep**: Do NOT add blockchain, Kubernetes, cloud microservices, ANPR, or face recognition to the MVP unless explicitly commanded.
6. **No Silent Failure Suppression**: Do not mask errors with empty `try/except: pass` blocks or return dummy fallback data.
7. **Empirical Verification**: Run tests or verification scripts after making changes to confirm functionality.

---

## 3. Step-by-Step Task Protocol

When asked to work on a task:
1. **Identify Target Phase**: Map the user's request to one of the 11 development phases in `TASKS.md` (e.g., Phase 1 Camera Ingestion, Phase 5 Event Engine).
2. **Check Dependencies**: Verify that prerequisite phases are complete and verified.
3. **Execute Minimal Edit**: Write clean, modular code satisfying the explicit requirement.
4. **Verify Implementation**: Execute unit tests or CLI sanity scripts.
5. **Report & Stop**: Summarize changes, share test results, update relevant documentation, and STOP execution.

# Quality gate checklist

For a human or LLM finishing a quality-gate adoption after `quality-gate/install`.
Work top to bottom. Do not skip an item and do not weaken a test to pass it.

## 1. Contract shape

The six steps, as `python3 gate.py ...`, Make targets, or an equivalent the project already has:

- [ ] `install` refuses a missing lockfile and installs frozen with lifecycle scripts denied
- [ ] `verify` checks module integrity, diff hygiene and pinned tool versions
- [ ] `test` runs the complete native suite (backend, production typecheck, frontend)
- [ ] `build` produces the real production artifacts
- [ ] `test-e2e` builds once and runs the established browser suites
- [ ] No step was excluded or `|| true`'d to manufacture green

## 2. Safety properties

- [ ] `api` / `ui` / `dev` commands never delete the local database
- [ ] All services bind `127.0.0.1` with strict ports and fail when occupied
- [ ] Synthetic database, uploads and runtime directories only; no household config or provider credentials
- [ ] `envDir: false` in every Vite config; Bun routes use `--no-env-file`
- [ ] The env-isolation regression (planted sentinel, ambient `.env*` immunity, declared runtime, real-failure self-check) is adapted and green
- [ ] Browser runner owns service startup/shutdown; owned services close

## 3. Smoke

- [ ] Start documented dev services on synthetic data
- [ ] One ordinary journey, refresh, entity visible
- [ ] Normal stop, restart, identical persisted state
- [ ] All owned processes exit and ports free afterwards

## 4. Acceptance

- [ ] Fresh checkout (no copied `node_modules`, build output or runtime state)
- [ ] `install && test-e2e-install && verify && test && test-e2e` clean: no unexpected failure, no new skip, no missing tracked input, no ambient leakage
- [ ] The smoke passes
- [ ] One bounded independent review of the exact diff and results
- [ ] The trust claim names its exact scope (for example "local macOS development"); unclaimed platforms/services are listed as unclaimed, non-blocking

## 5. Afterwards

- [ ] The qualifying candidate is an ordinary reviewed Git commit
- [ ] Evidence is preserved; nothing was deleted to look clean
- [ ] No further acceptance rounds are invented; product development proceeds

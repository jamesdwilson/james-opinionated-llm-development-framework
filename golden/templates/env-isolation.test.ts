// Golden environment-isolation regression (template).
//
// Installed by golden/adopt.sh. Adapt the marked lines to this project, then
// keep this test green in the normal frontend test run.
//
// What it must prove for this project:
//   1. A sentinel planted in the parent environment does NOT leak into the
//      test worker (the Makefile/test runner must use an explicit child env).
//   2. .env, .env.local, .env.test and .env.test.local files cannot alter the
//      controlled test result (Vite `envDir: false`, Bun `--no-env-file`).
//   3. The intended runtime is the one actually executing the tests.
//   4. A deliberately failing assertion really fails (the suite is not masked).
//
// If any of these cannot be made true yet, keep the test and fix the wiring,
// not the assertion.

import { describe, it, expect } from 'vitest'

describe('golden environment isolation', () => {
  it('does not leak the planted parent sentinel into the worker', () => {
    // The parent runner plants GOLDEN_PARENT_SENTINEL before spawning workers.
    // TODO: add the sentinel to the parent invocation in the Makefile/scripts.
    expect(process.env.GOLDEN_PARENT_SENTINEL).toBeUndefined()
  })

  it('does not expose ambient env-file values', () => {
    // TODO: create throwaway .env* fixtures with a known key in a focused
    // fixture test, or assert here that a known ambient key is absent.
    expect(import.meta.env.VITE_AMBIENT_LEAK_PROBE).toBeUndefined()
  })

  it('runs under the declared runtime', () => {
    // Kept's lesson: Bun-owned Vitest workers and Node-owned Playwright are
    // different runtimes. Assert the one this project declares.
    // TODO: pick exactly one of these and delete the other.
    expect(typeof (globalThis as { Bun?: unknown }).Bun).not.toBe('undefined') // Bun-owned route
    // expect(process.versions.node).toBeTruthy() // Node-owned route
  })

  it('propagates real failures (self-check)', () => {
    // Temporarily flip this to expect(true).toBe(false) and confirm the suite
    // goes red, then restore. A suite that cannot fail proves nothing.
    expect(true).toBe(true)
  })
})

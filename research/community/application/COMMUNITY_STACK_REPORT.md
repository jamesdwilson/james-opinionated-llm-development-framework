# Practitioner evidence for a less-first Bun/TypeScript stack

Research date: 2026-11-08. “Less-first” means minimizing concepts, files and dependencies while retaining the checks needed to ship correctly. This is a targeted qualitative review, not a representative survey. Source identifiers resolve in [SOURCES.json](SOURCES.json); the structured findings are in [COMMUNITY_STACK_REPORT.json](COMMUNITY_STACK_REPORT.json).

## Recommendation

For a new, predominantly forms/lists/content application, start with **Bun + Hono + server-rendered HTML**, add **HTMX for fragment interactions**, and use **Preact islands only for substantial client state**. Add **Hono RPC only to JSON endpoints consumed by those islands or other TypeScript clients**. This is the researcher's architectural recommendation, supported by the evidence below; it is not a community vote.

**Elysia 1.4 + Eden is an alternative server/contract pair**, especially when schema-led APIs and inferred errors dominate the application. Do not layer it over Hono. Keep a working Elysia system unless a measured problem justifies migration. For a new commitment specifically to 1.4, account for its security-only maintenance policy; do not silently substitute Elysia 2 or use v2 examples. [Elysia 1.4.30 release, E02](https://github.com/elysiajs/elysia/releases/tag/1.4.30)

A Bun-only runtime does not require avoiding Web APIs or every external development tool. It does require testing the actual production artifact on the pinned Bun release. “No Node runtime” and “no TypeScript compiler package” are different constraints.

The evidence supports potential reductions in duplicated client/server code and UI machinery. **It does not establish fewer LLM repair turns, fewer contract mistakes, or higher LLM productivity for this exact combination.** One substantive firsthand report points the other way.

## What practitioners recommend, and how strongly

| Pattern | What was actually reported | Interpretation |
|---|---|---|
| Minimal Hono/Bun server | April 2024 HN participants describe easy setup, server JSX and small APIs; one describes time spent integrating PDFKit and hesitation about production. | Useful historical DX evidence, not Bun 1.4 reliability evidence. [H01](https://news.ycombinator.com/item?id=40047212) |
| Elysia's integrated typing | In March 2026 feedback, users value inferred values/errors but also describe adapters, duplicated schemas and missing integrations. | There is enthusiasm and friction in the same community thread; neither proves consensus. [E03](https://github.com/elysiajs/elysia/discussions/1776) |
| Split growing RPC clients | An engineer reports IDE issues disappearing after modularizing AppType. A synthetic test separately measures lower compiler cost. | Concrete reason to preserve modularity instead of minimizing file count at any cost. [H03](https://zenn.dev/chot/articles/1d44bb3d5f1504) |
| HTML for ordinary interactions; islands for rich state | PhotoQuest's developer describes Preact for widgets that became unwieldy in Alpine attributes. | Supports the boundary pattern, but uses Spring/Thymeleaf and does not validate Bun integration. [T02](https://tschuehly.de/preact-islands-in-spring-boot-with-htmx-when-alpinejs-isnt-enough-anymore/) |
| Rich client framework when UX demands it | Gumroad's Helper team found conditional forms and workflow interactions easier in React/Next.js. | Avoid turning minimalism into a restriction on product behavior; not proof HTMX cannot do it. [T01](https://htmx.org/essays/why-gumroad-didnt-choose-htmx/) |

Reddit adds preference reports for Elysia's DX and differing views on Hono's organization/docs, plus mixed Bun production experiences. Exact versions and dates are often missing. These are background anecdotes, not votes or reliability measurements. [R01](https://www.reddit.com/r/bun/comments/1bzhn17/hono_vs_elysia/), [R02](https://www.reddit.com/r/node/comments/1phxcnu/is_anyone_here_actually_running_bun_in_production/)

## Version-specific findings

**Bun 1.4.x has meaningful patch boundaries.** The official 1.4 release is dated August 20, 2026; 1.4.4, dated October 22, was the newest 1.4.x release found. Use 1.4.4 as an evaluation candidate, not an untested compatibility guarantee. [B01](https://bun.com/blog/bun-v1.4), [B06](https://bun.com/blog/release-notes/bun-v1.4.4)

Scrydon's August 21 report describes a successful Bun 1.4.0 staging upgrade across nine services, with average CPU down 49.9% and working-set memory down 60.4%. Its matched windows were only 42 minutes; traffic changed and causal isolation was incomplete. The useful transferable practice is aligning the runtime, types, CI and container pins. These are early staging observations, not a general performance promise. [B02](https://scrydon.com/insights/2026/08/21/bun-1-4-at-scrydon/)

A September 4 reproduction identifies **Bun 1.4.1 + Elysia 1.4.29/1.4.30** emitting an invalid bundle through a naming collision. Builds succeeded but output failed to parse; 1.4.0 was reported good. Bun 1.4.2 release notes document the correction. This is evidence to smoke-test built output, not evidence that current Bun necessarily has that defect. [B03](https://github.com/oven-sh/bun/issues/41351), [B04](https://bun.com/blog/release-notes/bun-v1.4.2)

Elysia 1.4 introduced Standard Schema support, reducing the need to rewrite an existing validation vocabulary merely to use the framework. Its 1.4.30 release states that 1.4.x will receive security updates only. Those facts materially affect new adoption and documentation pinning. [E01](https://elysiajs.com/blog/elysia-14), [E02](https://github.com/elysiajs/elysia/releases/tag/1.4.30)

Eden's release list records publication under **@elysia** in 1.4.10; older examples use **@elysiajs**. Do not assume that identical-looking version numbers imply identical registry availability or peer ranges. Direct registry retrieval failed here, so neither the exact dependency graph nor a complete compatible version matrix was established. [E09](https://github.com/elysiajs/eden/releases)

## Recurring complaints and concrete failures

**Inference complexity is a recurring theme across separate reports and both framework pairs.** Hono 4.9.2 on an unspecified Bun version had a reported compiled-client inference failure in a monorepo. The issue is closed, but the reviewed text did not establish the fix. In a separate August 2026 experiment, Hono 4.12.32 / TypeScript 7.0.2 module clients reduced cold compiler command medians by 8.1–12.0% for a synthetic 1,000-endpoint API. That experiment ran under Node/pnpm, not Bun; it measured compiler work, not agent productivity. [H02](https://github.com/honojs/hono/issues/4361), [H03](https://zenn.dev/chot/articles/1d44bb3d5f1504)

Elysia 1.4.6 has a dated report of guard-wrapped routes working at runtime while Eden's types become missing or any. The report includes a minimal reproduction; a fixed release was not verified here. This illustrates why compiling successfully is insufficient if inference has degraded to any. [E04](https://github.com/elysiajs/eden/issues/212)

**Client wrappers can change error behavior.** With Elysia 1.4.22 and Eden 1.4.6, one user reports custom ky exceptions being captured into a result instead of reaching an error boundary, unlike Eden 1.4.5. Eden 1.4.7 references the repair. Treat this as historical, version-specific evidence for testing HTTP failures and network failures separately. [E05](https://github.com/elysiajs/eden/issues/246), [E06](https://github.com/elysiajs/eden/releases/tag/1.4.7)

**“Less UI code” can become more integration glue.** Gumroad describes difficulty with complex forms/workflows; the PhotoQuest account chooses islands for rich state. In the related Reddit thread, the author explicitly acknowledges that the published example does not handle islands introduced by swaps. These are two distinct projects, with the blog and Reddit follow-up counted as one project. [T01](https://htmx.org/essays/why-gumroad-didnt-choose-htmx/), [T02](https://tschuehly.de/preact-islands-in-spring-boot-with-htmx-when-alpinejs-isnt-enough-anymore/), [T03](https://www.reddit.com/r/htmx/comments/1r8yc1l/preact_islands_in_spring_boot_with_htmx_when/)

There is insufficient evidence to rank current Hono versus Elysia production defect rates. GitHub issues over-sample failures; community threads over-sample enthusiasts and frustrated users. Old Bun 1.3 anecdotes are not current 1.4 bug findings.

## What is redundant or overkill

These are architecture judgments drawn from the documented capabilities, not measured community consensus.

| Combination | Recommendation and exception |
|---|---|
| Hono + Elysia for the same application boundary | Choose one. Mounting both can help a migration, but adds two routing, lifecycle and typing models. |
| Hono RPC or Eden + a second RPC layer + handwritten DTOs for the same private TS endpoint | Choose one contract authority. Keep OpenAPI/code generation where independent or non-TS consumers need it. |
| HTMX fragment requests forced through a JSON RPC client | Unnecessary translation. HTML fragments and typed JSON have different consumers and contracts. |
| HTMX + Preact + Alpine + another reactive DOM system on the same subtree | Assign one owner to each subtree/state domain. Small native behavior may need no library. |
| Preact + hono/jsx/dom for the same widget | Choose a browser renderer. Server Hono JSX plus isolated Preact widgets is a separate, legitimate arrangement. |
| Whole-app SPA routing and query caching for a few interactive islands | Defer until navigation or shared client data needs it. A rich editor may justify a larger client application. |
| Multiple schema libraries describing identical wire objects | Reuse one schema vocabulary where feasible; Elysia 1.4 Standard Schema support helps. Do not erase meaningful input/output distinctions. |
| Elaborate monorepo/build orchestration for one deployable | Start with one package and focused modules; introduce declaration/build boundaries when editor/compiler measurements justify them. |

Hono RPC and Eden provide alternatives for typed HTTP access; neither is needed for a page that simply posts a form and receives HTML. [H04](https://hono.dev/docs/guides/rpc), [E08](https://elysiajs.com/eden/installation), [T04](https://htmx.org/docs/)

## Useful configuration and implementation tips

**Hono contracts.** Enable strict mode on both sides; keep Hono versions aligned; export the inferred route type and import it type-only. Preserve inferred route composition. Use explicit status variants. Global error handlers are not automatically reflected in RPC types; current documentation provides explicit global-response typing. For growing APIs, split clients or precompile declarations; use project references for separate TS projects. Check helpers against your pinned Hono version. [H04](https://hono.dev/docs/guides/rpc)

**Elysia/Eden contracts.** Keep matching Elysia versions, strict mode and method chaining; check aliases across project boundaries. Decide deliberately whether date strings should become Date objects and whether HTTP errors should throw. Current documented options are **parseDate** and **throwHttpError**, both singular; defaults are true and false respectively. Avoid copying the plural spellings in older discussions. [E08](https://elysiajs.com/eden/installation), [E07](https://elysiajs.com/eden/treaty/config)

**Two JSX runtimes need explicit boundaries.** Hono server templates use jsxImportSource hono/jsx; the reviewed Preact v10 guide uses preact. Use per-file pragmas or separate configurations rather than treating their VNodes and hooks as interchangeable. Prefer a small browser mount module with typed serialized props; keep server secrets out of browser imports. The latter boundary is a design recommendation, not a measured report. [H05](https://hono.dev/docs/guides/jsx), [T06](https://preactjs.com/guide/v10/typescript/)

**Island lifecycle is part of the implementation.** Initialize widgets in newly swapped fragments, avoid duplicate mounts, and unmount/clean effects before HTMX removes their roots. The reviewed HTMX API documents afterSwap and beforeCleanupElement; Preact documents render/hydrate/lifecycle APIs. Pin the HTMX major and verify these hooks rather than mixing examples across majors. Do not let HTMX replace nodes that Preact still owns. [T05](https://htmx.org/events/), [T07](https://preactjs.com/guide/v10/api-reference/)

**Typed JSON is not a complete web contract.** Maintain runtime validation at trust boundaries, authorization, HTML escaping and CSRF protection as appropriate. Type-only imports do not validate a deployed response; mismatched deployments, serialization and any casts can defeat static assumptions. HTMX contracts include URLs, field names, selectors, fragment roots and status behavior; RPC inference does not automatically check them. Add browser/integration checks for these boundaries.

Suggested acceptance cases, not executed in this research: invalid input; unauthorized access; success/error status narrowing; date serialization; network timeout; renamed route rejected by client checking; unexpected any; fragment validation errors; history/back navigation; island insertion/removal; and starting the actual bundled or compiled server. These target the observed failure classes rather than maximizing test count.

## What may replace existing pieces, and what should stay

No existing project was inspected, so these are conditional replacement candidates.

| Candidate | What it may replace | What to retain or verify |
|---|---|---|
| Bun runtime, package manager, build and test tools | Separate tools performing equivalent basic jobs | Keep plugins, test environments and orchestration until equivalent behavior is demonstrated; pin lockfile/runtime. [B01](https://bun.com/blog/bun-v1.4) |
| bun check, added in 1.4.3 | A separate no-emit type-check command/package for suitable projects | It does not emit .d.ts or provide a language server. Hono declaration precompilation can still need a compiler. [B05](https://bun.com/blog/release-notes/bun-v1.4.3) |
| bun fmt, added in 1.4.4 | A standalone formatter where output/configuration match | Keep useful lint rules; formatting is not semantic linting. [B06](https://bun.com/blog/release-notes/bun-v1.4.4) |
| Server HTML + HTMX | Client routing/fetch/state plumbing for server-owned workflows | Keep browser checks and explicit error/history behavior. [T04](https://htmx.org/docs/) |
| Hono RPC or Eden | Handwritten internal typed fetch wrappers and duplicated DTO maintenance | Keep runtime schemas, serialization tests and deploy compatibility. |
| hono/jsx/dom | Preact for modest widgets without ecosystem requirements | It has partially compatible hooks; do not assume React/Preact library compatibility. [H06](https://hono.dev/docs/guides/jsx-dom) |
| Preact islands | Large attribute-driven Alpine logic or a whole SPA for isolated complex widgets | Keep HTMX for surrounding server-owned interactions, with ownership/lifecycle boundaries. [T02](https://tschuehly.de/preact-islands-in-spring-boot-with-htmx-when-alpinejs-isnt-enough-anymore/) |

Keep TypeScript checking, boundary validation, a reproducible lockfile, focused integration tests, operational logging and established deployment behavior. Keep useful modules: fewer files is not automatically easier reasoning. Keep Preact when real client state or library integration warrants it. Keep a working Elysia/Eden pair rather than migrating for benchmark fashion.

## Does this support LLM productivity?

| Proposed benefit | Evidence found | Verdict |
|---|---|---|
| Fewer files | A maintainer summary attributes OpenUnited's migration a reduction from 588 to 163 files, with before/after repositories linked. | Structural precedent, secondary account; not independently recounted, not this stack and not an agent experiment. [L03](https://htmx.org/essays/another-real-world-react-to-htmx-port/) |
| Fewer dependencies | A summary of Contexte's practitioner talk reports JS dependencies falling from 255 to 9. | Suggestive for content applications; not proof of LLM benefit. [L02](https://htmx.org/essays/a-real-world-react-to-htmx-port/) |
| Fewer concepts | HTML workflows can remove client cache/router machinery; mixed island lifecycles add concepts back. | Plausible design mechanism, no controlled concept-count evidence found. |
| Fewer repair turns | No matched agent-run logs located for Bun 1.4 + either framework + HTMX/Preact. | Unsupported. |
| Fewer contract mistakes | Inference can flag shape changes, but reports also show missing/any types and error-semantic regressions. | Useful mechanism; no comparative defect count established. |
| Better overall LLM throughput | bobjordan reports LLM difficulty with HTMX/Alpine glue and greater productivity with Go/React and typed hooks. | Counterexample to a universal simplicity claim; models, tasks and languages were uncontrolled. [L01](https://news.ycombinator.com/item?id=46315756) |

PhotoQuest's author discloses agent-assisted drafting; a Reddit commenter reports an agent-assisted framework conversion. Neither measures development throughput or correctness. Do not confuse “an app uses LLMs” with “LLMs built the app more efficiently.” [T02](https://tschuehly.de/preact-islands-in-spring-boot-with-htmx-when-alpinejs-isnt-enough-anymore/), [T03](https://www.reddit.com/r/htmx/comments/1r8yc1l/preact_islands_in_spring_boot_with_htmx_when/)

A useful future evaluation would hold model/version, prompt, task, time budget and acceptance tests constant across a CRUD flow, a contract change and a rich-state widget. Record completion, files read/changed, dependencies introduced, repair turns, type errors, browser failures and escaped contract mistakes. Give agents pinned-version documentation and one working pattern. No such experiment was run here.

## Method, coverage and limitations

Searched public Reddit, HN, GitHub issues/releases/discussions and practitioner engineering blogs, then opened selected original pages. Search themes included Bun 1.4 release/regression experience; Hono RPC inference and performance; Elysia 1.4/Eden failures; HTMX production and LLM experience; and Preact islands. Positive and negative reports were sought. Official release notes and documentation cross-check technical capabilities; no installation or reproduction was performed.

**Reddit was not globally blocked.** Thread bodies/comments were readable through the web tool, but a comment permalink failed and extracted dates were often relative or stale. Indexed Reddit snippets served discovery only; they are not substantive evidence. HN also returned a 429 on one comparison comment, which was excluded. Private Discord/Slack discussions were not accessed.

Direct npm metadata requests failed DNS resolution in the restricted shell. Exact releases were therefore checked against official sources, not a reconstructed dependency graph. A discovered Hono Agent DX table could not be opened and was excluded. Rolling documentation may contain newer APIs; it is not proof that an older patch exposes them. Unknown dates/versions are recorded explicitly rather than inferred from crawl timestamps.

The evidence set contains self-selection, vendor advocacy, adjacent stacks and older reports. The two migration summaries share a framework-maintainer author, and the Preact blog/Reddit thread describe one project. Confidence describes the bounded claim, not a framework's general quality.

Only the requested research artifacts were written. No project code was modified, nothing was installed, and nobody was contacted. The process was invoked with explicit `gpt-6-astra` and medium-reasoning flags, but its JSONL did not expose the effective model/reasoning values for independent read-back. No Gemini was used.


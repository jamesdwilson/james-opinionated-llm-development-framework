# Bun-first lab ecosystem research

**Date:** 2026-11-08  
**Scope:** practitioner guidance, workflow tools, and Zod versus Elysia-native contracts and alternatives.  
**Interpretation:** “zed vs elysyia contracts” is treated as **Zod versus Elysia contracts**. If “Zed” meant the editor, that is a separate decision and does not compete with a contract layer.

## Priority correction: optimise for LLM development speed

The controlling goal is now explicit: **maximum rapid and accurate development speed for an LLM-assisted personal MVP**, not accessibility compliance, framework purity or theoretical contract architecture.

Accessibility metadata is useful only where it gives Playwright or an LLM a stable machine-readable page model. Keep native semantic HTML, names, labels and a few deliberate test ids because they improve role locators and accessibility-tree snapshots. Do not add an accessibility programme or axe-core gate merely to pursue WCAG coverage at this stage.

For a forms, lists, approvals, settings or internal-tool MVP, the lowest-entropy default is **Bun + stable Elysia + `Elysia.t` + `@elysia/html`/KitaJS + HTMX**. The current stable `@elysia/html` package is 1.4.1.[37]

Elysia’s HTML plugin renders JSX to strings through KitaJS, while HTMX expresses browser requests and replacement targets directly in HTML attributes.[32][38][39] This removes most separate client API calls, client data caches and duplicated models, so there is less for an LLM to keep synchronized.

When the product genuinely needs rich client-local state, offline behaviour, complex drag/drop or highly interactive visualisation, use **Svelte 5/SvelteKit with Elysia and Eden Treaty** rather than forcing HTMX past its natural boundary. Elysia documents a SvelteKit server-route integration, and Eden carries Elysia server types to the frontend without code generation.[33][35]

For a separate TypeScript client, **Eden Treaty is the preferred contract mechanism**. It gives typed request data, typed status/error branches and autocomplete from the exported Elysia application type.[33] Eden Fetch is a fetch-shaped alternative, but Elysia currently recommends Treaty except for unusually large clients consuming more than roughly 500 routes, where Fetch can reduce TypeScript inference cost.[34]

Hono RPC is the strongest lightweight fallback if Elysia proves unstable. It also shares server route types with a generated client shape, although its documentation identifies additional rules around strict TypeScript configuration, explicit response statuses and global error typing.[36]

## Executive decision

Keep the current testing architecture:

1. **Bun 1.4.4** as the sole JavaScript runtime.
2. **Playwright** as deterministic browser authority.
3. **Midscene** only for bounded visible-UX reasoning.
4. **Bugsink** for isolated error evidence with project-scoped read capabilities when the 2.6.3 migration is complete.
5. **Elysia `t` schemas** as the default HTTP-boundary contract if we add an Elysia service.
6. **Eden Treaty** only for internal TypeScript clients that can share the server type.
7. **OpenAPI** as the portable contract artifact for tests, external clients and future services.

The three additions worth a controlled spike are:

- **Hurl** for short, deterministic API journeys that humans and LLMs can read.
- **oasdiff** to reject accidental breaking changes in generated OpenAPI.
- **Schemathesis** to generate hostile and stateful tests from that same OpenAPI.

Do **not** add another browser agent, Cucumber layer, contract framework, report portal or LLM observability service yet. The present stack already has the right authority split. Extra orchestration would add more uncertainty than evidence.

## 1. What practitioners repeatedly recommend

### Keep the model away from release authority

The strongest recurring advice is to let an LLM explore, explain and propose, while deterministic tests decide. Playwright’s own guidance favours resilient user-facing locators, isolated tests, web-first assertions, controlled test data and traces for diagnosis rather than arbitrary sleeps or stateful test chains.[13]

Our current boundary is sound:

- Playwright owns visible state and exact journey assertions.
- deterministic runners own persistence, permissions, recovery, cleanup and API state;
- Midscene may report ambiguity, contradiction and visible friction;
- a Midscene green result cannot cancel a deterministic failure.

This is also the practical answer to the recent wave of “AI testing agent” products. Community discussion is enthusiastic about generating and exploring tests, but reliability, token use, hidden state and self-healing that masks regressions remain recurring concerns.[24][25]

### Prefer compact browser interfaces for coding agents

Microsoft’s current Playwright MCP README now makes an unusually candid distinction: routine coding agents often benefit more from **Playwright CLI plus skills** because it is more token-efficient, while MCP is better for persistent exploratory loops that need a long-lived browser and rich introspection.[12]

That means we should not install Playwright MCP merely because it is fashionable. For our workflow:

- use normal Playwright tests and concise CLI commands for implementation agents;
- give an agent the smallest useful ARIA/DOM/trace excerpt;
- reserve MCP for a future bounded exploratory worker where persistent browser state is the actual requirement;
- never let an MCP browser become the release oracle.

### Keep AI scenarios short and twin them deterministically

Practitioner examples become less reliable as prompts mix several goals, hidden state and recovery branches. The right pattern is:

- one user goal per reasoning scenario;
- explicit starting state;
- bounded visible surface;
- a structured result schema;
- a deterministic twin for every stateful or security-relevant claim;
- no “self-healing” that silently changes the intended assertion.

This supports the proposed short Gherkin catalogue. It argues against adding Cucumber or `playwright-bdd` until the catalogue proves that extra runner plumbing buys something.

### Use caching only after the uncached path is trustworthy

Midscene supports caching to replay located actions and reduce model calls, but cached actions can become stale after UI changes.[14] Our current `cache: false` policy is therefore correct for acceptance evidence. A later speed lane may use cache only when:

- the same scenario has already passed uncached;
- cache keys include the exact candidate and prompt version;
- a cache miss or stale action fails closed;
- release evidence remains uncached.

### Treat the generated API description as evidence, not decoration

Static TypeScript inference is not enough. The wire contract must be generated, diffed and attacked. A useful contract workflow is:

1. define request and response schemas beside the route;
2. generate OpenAPI;
3. validate the OpenAPI document;
4. compare it with the accepted baseline;
5. execute deterministic examples;
6. generate invalid and stateful cases;
7. confirm actual responses match the published schema.

This gives coding agents one bounded source of truth instead of forcing them to infer behaviour from handlers, client types and prose independently.

## 2. Helpful applications that fit the workflow

### Adopt by bounded spike

#### Hurl

Hurl is a single-purpose CLI that expresses HTTP requests, captures and assertions in a small plain-text format. It can chain requests and validate status, headers, JSONPath, XPath, GraphQL and response duration.[16]

**Why it fits:**

- deterministic and non-LLM;
- readable enough for James, an implementation agent and a reviewer;
- no competing browser framework;
- excellent for Bugsink capability probes and generated API examples;
- failure cases remain copyable and reproducible.

**Use:** a small set of canonical API journeys, not a second full test suite.

#### oasdiff

`oasdiff` compares OpenAPI documents and identifies breaking changes, non-breaking changes and invalid specifications. It is available as a standalone binary and supports CI-oriented output.[17]

**Why it fits:**

- catches accidental contract drift before client generation;
- gives an LLM a concise semantic diff instead of two large YAML files;
- does not add a JavaScript runtime dependency;
- lets us approve a deliberate breaking change explicitly.

**Use:** compare the generated candidate spec with the last accepted spec.

#### Schemathesis

Schemathesis generates tests from OpenAPI, GraphQL and gRPC schemas. It supports stateful operation chaining, adaptive use of response data, custom checks, reproducible failure cases, offline reports and schema-coverage reporting.[15]

**Why it fits:**

- attacks the contract rather than trusting generated clients;
- can discover invalid coercions, undocumented responses and state-machine failures;
- can consume curated or LLM-generated fuzz dictionaries without letting the LLM decide pass/fail;
- runs independently of the Bun package graph.

**Use:** a bounded OpenAPI fuzz gate against lab-owned services, with rate limits and reproducible seeds.

#### axe-core

`axe-core` is a mature accessibility engine designed to run beside functional browser tests. It covers WCAG rules and explicitly marks uncertain cases for manual review rather than pretending automation can prove everything.[18]

**Why it fits:**

- gives the LLM reasoning lane cleaner accessibility evidence;
- catches deterministic issues that Midscene might merely describe;
- pairs naturally with Playwright’s role-based locators and accessibility snapshots.

**Caution:** it is another JavaScript dependency, so it must pass the same source, cutoff and audit controls before admission.

### Useful, but not now

#### Playwright MCP

It is first-party and uses structured accessibility snapshots, but its own maintainers now recommend CLI plus skills for many coding-agent workflows because MCP schemas and large snapshots can consume more context.[12]

**Disposition:** do not install now. Revisit only for a named persistent exploratory loop.

#### OSV-Scanner

OSV-Scanner is a strong independent advisory source and can scan many manifests, lockfiles, SBOMs and containers.[19]

**Caution:** its current documented lockfile list does not establish native `bun.lock` support. It can supplement `bun audit` through an aligned `package-lock.json` or generated SBOM, but it must not be represented as exact Bun-lock proof.

**Disposition:** useful second opinion after lock/SBOM alignment, not an acceptance replacement.

#### Arize Phoenix

Phoenix provides local or self-hosted OpenTelemetry-based LLM traces, datasets, experiments and evaluations.[20]

**Why it could help:** compare Midscene model/prompt configurations on the same J05/J06 and Gherkin cases, retaining traces and scored outputs.

**Why not now:** it adds a service and operational surface, and its repository is under Elastic License 2.0 rather than an OSI-approved permissive licence. Our current evidence files are sufficient until model comparison becomes frequent enough to justify a dedicated system.

### Reject for the present stack

- **another AI browser framework:** overlaps Playwright plus Midscene and weakens authority boundaries;
- **Cypress:** duplicates deterministic browser coverage without a demonstrated gap;
- **Cucumber or `playwright-bdd`:** adds translation and runner plumbing before the small Gherkin catalogue is proven;
- **Allure or a separate report portal:** native Playwright, Midscene and acceptance artefacts already contain the needed evidence;
- **Langfuse/Phoenix-class observability by default:** service overhead is not justified for two bounded model-reviewed journeys;
- **self-healing test products:** automatic selector repair can hide a real UX or contract regression.

## 3. Zod versus Elysia contracts

### First: this is not a direct either/or

**Zod is a runtime schema library. Elysia is a web framework with route schemas, validation, type inference, OpenAPI generation and a typed client.** Elysia can consume Zod because it supports Standard Schema.[1][4][5]

The real decisions are:

1. which schema dialect defines each boundary;
2. whether the API is implementation-first or contract-first;
3. whether consumers can share TypeScript types;
4. whether OpenAPI must be the portable source of truth.

### Elysia-native `t`

Elysia’s `t` builder is based on TypeBox and is tailored for server validation. The same route schema supplies runtime validation, TypeScript inference and OpenAPI generation.[1][6]

**Best fit:**

- Bun-first Elysia services;
- request and response validation beside handlers;
- internal services where low adapter count matters;
- APIs that still emit OpenAPI for external validation.

**Advantages for LLM work:**

- fewer libraries and fewer equivalent ways to express the same contract;
- schema, handler and response contract stay close together;
- JSON-Schema-shaped output is easier to feed into deterministic generators;
- less chance that an agent updates a Zod schema but forgets a separate OpenAPI object.

**Risks:**

- Elysia and TypeBox are moving quickly;
- advanced transforms, recursive types and exact response cleaning need focused tests;
- Elysia 2 RC has attractive improvements, but its active issue tracker still shows recent package-resolution, schema and precompile churn.[23]

### Zod inside Elysia

Zod has a very broad ecosystem, familiar syntax, static inference and built-in JSON Schema conversion.[5]

**Best fit:**

- schemas already shared with forms, configuration or non-Elysia packages;
- teams with a large existing Zod corpus;
- integrations that specifically expect Zod.

**Advantages for LLM work:**

- models have seen a large amount of public Zod code;
- error handling and schema composition are familiar to many developers;
- broad tooling lowers the chance of inventing a custom pattern.

**Risks in Elysia:**

- it adds a Standard Schema adapter path instead of using Elysia’s native route dialect;
- recent Elysia issues include error-object handling and response serialization with Zod, Effect Schema and other Standard Schema validators.[21][22]
- transforms and input/output types require particular care because HTTP wire input and decoded output are not always the same type.

**Verdict:** do not choose Zod merely because it is popular or LLM-familiar. Use it where sharing and ecosystem compatibility are real requirements.

### Eden Treaty

Eden Treaty derives a fully typed client from the Elysia application type without a separate code-generation step.[2]

**Best fit:** internal TypeScript consumers in the same repository or a tightly coordinated workspace.

**Do not treat it as the only contract:** it cannot replace a portable OpenAPI artefact for non-TypeScript clients, independent conformance tests or long-lived service boundaries.

## 4. Current alternatives

### TypeBox directly

TypeBox creates JSON Schema values that also infer TypeScript types and provides compiled validation.[6]

**Use it directly** when JSON Schema itself is the canonical cross-framework artefact. **Inside Elysia, prefer `Elysia.t`** unless a specific external-schema requirement justifies bypassing Elysia’s tailored layer.

### Valibot

Valibot is dependency-free, modular and strongly tree-shakeable, with a very small client bundle.[7]

**Good for:** browser forms or shared frontend validation where bundle size matters.  
**Not a reason to replace Elysia `t`:** server bundle size is not our controlling concern, and another schema dialect increases cognitive load.

### ArkType

ArkType offers expressive TypeScript-like runtime validation.[8]

**Good for:** domain-heavy validation where its syntax clearly improves readability.  
**Caution:** an open Elysia issue currently reports OpenAPI generation trouble with an ArkType date schema. It should not be the default until our exact patterns pass a contract spike.

### Effect Schema

Effect Schema is compelling when the application already adopts Effect for typed errors, services and transformations.[9]

**Good for:** an Effect-native system.  
**Not for this lab:** adopting Effect only for validation is a large conceptual and dependency commitment, and Elysia has an open response-serialization issue involving Effect Schema and Zod.[22]

### oRPC

Current oRPC provides contract-first and implementation-first APIs, typed clients, OpenAPI, Bun support and optional MCP exposure for agent tools.[10]

**This is the strongest alternative to spike** if the goal is explicitly contract-first, multi-client API design rather than an Elysia-first service.

**Do not layer it underneath Elysia by default.** That would create two routing/contract abstractions. Compare an oRPC vertical slice with an Elysia `t` plus Eden/OpenAPI slice and choose one.

### ts-rest

`ts-rest` remains a clear contract-first design, but its upstream repository shows no commit in roughly a year as of this review.[11]

**Verdict:** do not choose it for greenfield work while oRPC is actively moving and covers more of the same contract/OpenAPI territory.

### Standard Schema

Standard Schema is an interoperability interface used by many validators.[4]

**Use it as a portability seam, not as the contract.** It lets Elysia accept Zod, Valibot, ArkType or Effect Schema, but it does not remove each library’s semantic differences in transforms, errors, JSON Schema conversion and input/output typing.

## 5. Elysia 1.4 versus Elysia 2 RC

The Elysia 2 RC article reports lower per-route memory, faster validation/coercion with `Elysia.t`, deeper error inference, richer OpenAPI error types, Eden plugin extension points and a substantially expanded test suite. The maintainers recommend the RC for new projects.[3]

However, current public issues still show active churn around TypeBox resolution under Bun and beta/RC compilation.[26][27][28]

AOT response schemas and duplicate precompile composition also have recent open reports, including one opened on 2026-11-05.[23][29]

**Decision for our lab:**

- do not adopt Elysia 2 RC into the accepted stack;
- if we need an API framework now, compare current stable Elysia 1.4.31 against current stable oRPC 1.16.2 in a disposable spike;[30][31]
- revisit Elysia 2 after stable release plus a quiet patch period and exact Bun 1.4.4 compatibility tests;
- inspect, do not blindly install, the official Elysia LLM skill mentioned in the RC notes. It is useful evidence that the project is improving agent guidance, but a skill remains executable guidance that needs source review and pinning.[3]

## 6. Recommended reference architecture

For an Elysia service:

1. define request **and response** schemas with `Elysia.t`;
2. keep domain logic independent of HTTP schemas;
3. use Eden Treaty only for internal TypeScript callers;
4. emit and freeze OpenAPI as a build artefact;
5. run `oasdiff` against the accepted specification;
6. run small Hurl examples against the live local service;
7. run bounded Schemathesis fuzz/stateful tests;
8. cover user-facing flows with Playwright;
9. let Midscene assess only visible ambiguity and completion;
10. send failures to an isolated Bugsink project with least-privilege read tokens.

This gives an LLM several small, reliable inputs:

- route schema;
- semantic OpenAPI diff;
- one reproducible Hurl case;
- one minimized Schemathesis counterexample;
- Playwright trace and accessibility snapshot;
- scoped Bugsink event.

That is materially better than handing the model a repository, a browser and an instruction to “work it out.”

## 7. Practical next experiment

Build one disposable API slice twice:

- **Variant A:** stable Elysia 1.4.31, `Elysia.t`, Eden Treaty and generated OpenAPI;
- **Variant B:** stable oRPC 1.16.2 with its contract and OpenAPI path.

Use the same resource, validation rules, typed client, error cases and persistence behaviour. Score:

- runtime and response validation;
- exact OpenAPI fidelity;
- breaking-change detection;
- generated or inferred client quality;
- Bun compatibility;
- LLM edit accuracy on five controlled changes;
- dependency/audit surface;
- failure readability for a human reviewer.

Until that comparison says otherwise, **Elysia `t` is the preferred server-boundary schema, Zod is an optional interoperability tool, and OpenAPI is the portable contract.**

## Sources

[1] https://elysiajs.com/essential/validation — Elysia validation documentation
[2] https://github.com/elysiajs/eden — Eden Treaty README
[3] https://next.elysiajs.com/blog/elysia-20-rc — Elysia 2.0 RC release article
[4] https://standardschema.dev — Standard Schema specification
[5] https://zod.dev — Zod documentation
[6] https://github.com/sinclairzx81/typebox — TypeBox README and documentation
[7] https://github.com/fabian-hiller/valibot — Valibot README
[8] https://github.com/arktypeio/arktype — ArkType README
[9] https://github.com/Effect-TS/effect — Effect repository and Schema documentation
[10] https://github.com/unnoq/orpc — oRPC README
[11] https://github.com/ts-rest/ts-rest — ts-rest repository
[12] https://github.com/microsoft/playwright-mcp — Microsoft Playwright MCP README
[13] https://playwright.dev/docs/best-practices — Playwright best practices
[14] https://midscenejs.com/caching — Midscene caching documentation
[15] https://github.com/schemathesis/schemathesis — Schemathesis README
[16] https://github.com/Orange-OpenSource/hurl — Hurl README
[17] https://github.com/oasdiff/oasdiff — oasdiff README
[18] https://github.com/dequelabs/axe-core — axe-core README
[19] https://github.com/google/osv-scanner — OSV-Scanner README
[20] https://github.com/Arize-ai/phoenix — Arize Phoenix README and licence
[21] https://github.com/elysiajs/elysia/issues/1835 — Elysia issue 1835: Standard Schema ValidationError handling
[22] https://github.com/elysiajs/elysia/issues/1670 — Elysia issue 1670: response serialization with Standard Schema validators
[23] https://github.com/elysiajs/elysia/issues/2047 — Elysia issue 2047: duplicate precompile composition
[24] https://news.ycombinator.com/item?id=50339913 — Launch HN discussion: Momentic browser testing agents
[25] https://news.ycombinator.com/item?id=50366117 — Ask HN: current AI agentic setup
[26] https://github.com/elysiajs/elysia/issues/2014 — Elysia issue 2014: TypeBox resolution under Bun
[27] https://github.com/elysiajs/elysia/issues/2001 — Elysia issue 2001: beta compile failure with schemas
[28] https://github.com/elysiajs/elysia/issues/1963 — Elysia issue 1963: OpenAPI beta TypeBox resolution under Bun
[29] https://github.com/elysiajs/elysia/issues/2024 — Elysia issue 2024: AOT crash with response union
[30] https://registry.npmjs.org/elysia/latest — npm registry metadata: elysia
[31] https://registry.npmjs.org/@orpc%2fserver/latest — npm registry metadata: @orpc/server
[32] https://elysiajs.com/plugins/html — Elysia HTML plugin documentation
[33] https://elysiajs.com/eden/overview — Elysia Eden overview
[34] https://elysiajs.com/eden/fetch — Elysia Eden Fetch documentation
[35] https://elysiajs.com/integrations/sveltekit — Elysia SvelteKit integration
[36] https://hono.dev/docs/guides/rpc — Hono RPC documentation
[37] https://registry.npmjs.org/@elysia%2fhtml/latest — npm registry metadata: @elysia/html
[38] https://github.com/kitajs/html — KitaJS HTML repository
[39] https://htmx.org/docs — htmx documentation

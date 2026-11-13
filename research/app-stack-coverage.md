# App-stack coverage priorities

Research checked: 2026-11-12. Scope: web UI and HTTP API applications, following James's current adoption question. Native mobile and desktop stacks are outside this comparison, not unsupported by policy.

**Track ten reference combinations. Target three first. Consider five only after the first three work. Preserve existing Go and other work regardless of this list.** These are coverage priorities, not a support allowlist or an installer catalogue.

## What the evidence supports

The [Stack Overflow 2026 technology results](https://survey.stackoverflow.co/2026/technology/data) provide a broad component-adoption signal. Relevant web-technology figures include React 41.5%, Node.js 46.4%, Next.js 20.6%, ASP.NET Core 19.9%, FastAPI 18.5%, Vue 17.2%, Angular 16%, WordPress 13.3%, Spring Boot 12.8%, Flask 12.5%, Django 11.3%, Svelte 7.8% and Laravel 7.6%. These are multiple-selection technology responses, **not percentages of applications using a complete combination**. The [survey methodology](https://survey.stackoverflow.co/2026/methodology/) describes its recruited, self-selected respondent population, not a census of deployed applications.

[Flatlogic's 2025 report](https://flatlogic.com/starting-web-app-in-2025-research-results) supplies some direct frontend/backend pairing evidence from 303 developers. It discusses React with Java/Node and Angular with C#/.NET, among other combinations. Its vendor audience and conditional denominators limit generalisation; its React adoption figures also differ between sections. It is corroboration, not a global ranking.

The [Django survey](https://lp.jetbrains.com/django-developer-survey-2026/) and [PHP survey](https://blog.jetbrains.com/phpstorm/2025/10/state-of-php-2025/) add ecosystem-specific checks. Their populations and questions differ from the broad survey, so their percentages are not pooled into a score.

**No source reviewed establishes the world's ten most-used complete app stacks.** The list below is an engineering selection of representative combinations drawn from popular components. Do not call its order measured joint market share. Do not multiply marginal percentages, compare conditional percentages as if they shared a denominator, or count overlapping families as independent market segments.

## Ten tracked combinations

The identifiers stay stable if priorities change. PostgreSQL is a reference-fixture choice, not a finding that it is the leading database for every combination. A target with no database needs no database role. Existing sound databases and runtime choices stay in place.

### First three: active coverage targets

- **S01: TypeScript + React + Node.js + PostgreSQL.** Reference variants: Next.js full-stack application, or React frontend with an Express API. [Next.js documentation](https://nextjs.org/docs) establishes its React/full-stack relationship. These variants are related, not interchangeable acceptance evidence. Current coverage: qualified declaration reporting and synthetic mapping exist; a [dependency-free native Node validation-layer transfer](../CONSUMER-ADOPTION.md#dependency-free-native-node-owner-transfer) now has real test/failure/recovery and preservation evidence. Complete native Next.js/Node application/database/browser readiness is still unproven. Next: exercise the existing adoption path against inspected native commands, not install a second test stack automatically.
- **S02: TypeScript + Angular + C# / ASP.NET Core + PostgreSQL.** [Microsoft's SPA guidance](https://learn.microsoft.com/en-us/aspnet/core/client-side/spa/intro?view=aspnetcore-10.0) documents the Angular/React frontend and ASP.NET Core backend arrangement. Current coverage: new combination, native execution unqualified. Next: component-scoped role map and a bounded native consumer case. React or server-rendered .NET variants remain valid alternatives, not automatic rewrites. Legacy ASP.NET is not silently converted into modern ASP.NET Core.
- **S03: TypeScript + React + Python / FastAPI + PostgreSQL.** The [maintainer's full-stack template](https://github.com/fastapi/full-stack-fastapi-template) provides direct combination evidence. Current coverage: an [owned in-process API component and mixed Node/API root workflow](../CONSUMER-ADOPTION.md#in-process-native-api-and-mixed-owner-root-workflow) have real HTTP, independent challenge, adoption, failure/recovery and preservation evidence. This is not acceptance of the upstream full-stack template, React/browser/database or full S03. Next: retain those native owners and close remaining applicable roles without treating empty tasks as PASS. Browser roles are N/A only for an explicitly API-only scope with no exposed browser UI; inspect SDK-generated documentation surfaces as well as custom routes.

These three are selected for strong component adoption, supported pairings and distinct native backend tooling. S02 also checks a non-React frontend early. That is our coverage judgement, not a statistical claim that these are the world's three most-used complete stacks.

### Native check ownership before selecting commands

Documentation checked 2026-11-13. These are selection constraints, not installed-SDK or executed-stack acceptance. Inspect the actual project and pinned versions before using a command; preserve a sound existing runner.

- **Angular unit owner:** the [current Angular testing guide](https://angular.dev/guide/testing) describes Vitest with jsdom for new CLI projects and still supports existing Karma setups. Do not replace Karma just because a new-project default changed. A Node DOM emulator and a real browser are different execution modes, not interchangeable UI evidence.
- **Angular command scope:** the [CLI reference](https://angular.dev/cli/test) takes a project name from `angular.json`; omitting it runs all projects. For a bounded non-watch run, select the actual project and make the watch setting explicit. Inspect its runner and browser configuration first: Vitest can use an installed DOM emulator, while Karma follows its configured browsers. The `headless` option alone does not guarantee a browser ran; with Vitest it has no effect unless browsers are configured. `list-tests` performs discovery without building or executing tests, so it cannot satisfy the test role.
- **C# runner identity:** [Microsoft's test-driver documentation](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test) distinguishes VSTest and Microsoft.Testing.Platform. SDK version, `global.json` and the selected runner affect command compatibility. Starting with .NET 11, a recognised `DOTNET_TEST_RUNNER` environment value overrides the file's runner selection. Record the intended effective choice rather than silently inheriting or changing it; do not copy flags from the other runner.
- **C# restore boundary:** [VSTest driver documentation](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test-vstest) describes implicit dependency restore and `--no-restore`. A test command is not automatically an offline or dependency-free action. Inspect the selected project, restored inputs and restore authority; a missing restore is setup failure, not meaningful behavioural RED.
- **ASP.NET Core HTTP owner:** [Microsoft's integration-testing guide](https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests?view=aspnetcore-10.0) describes `WebApplicationFactory` and `TestServer` through `Microsoft.AspNetCore.Mvc.Testing`. Reuse an appropriate existing test host and runner rather than adding a second harness. This can exercise the request/response boundary with an in-memory server, but does not qualify a browser, real database, external dependencies or published-service lifecycle.

For S01/S03, retain the inspected frontend and Node/Python owners described by their own project scripts and contracts. The qualified component proofs above do not supply an Angular, ASP.NET Core, Next.js or browser PASS. Native owner selection, actual execution, requirement coverage and whole-stack acceptance remain separate outcomes.

### Candidates four and five: conditional expansion

- **S04: TypeScript + Vue + Node.js + PostgreSQL.** Include plain Vue and, separately, [Nuxt](https://nuxt.com/docs/4.x/getting-started/introduction) where actually present. Existing Vue profile evidence is manual mapping only; native Vue/Nuxt execution remains unproven. Do not infer Nuxt from Vue.
- **S05: TypeScript + React or Angular + Java / Spring Boot + PostgreSQL.** Track the frontend variants separately. Pairing evidence comes from the Flatlogic report above; it does not establish a complete four-component joint share. Native Java/Spring coverage is unqualified. Next: inspect the target's Maven/Gradle and frontend owners before choosing commands.

### Tracked, not new implementation commitments

- **S06: WordPress + PHP + MySQL/MariaDB + its existing browser frontend.** [WordPress requirements](https://wordpress.org/about/requirements/) establish its runtime/database combination. Native coverage unqualified; plugin/theme boundaries need target-specific inspection.
- **S07: Python / Flask + Jinja/server-rendered HTML + PostgreSQL.** [Flask's template documentation](https://flask.palletsprojects.com/en/stable/quickstart/) supports the rendering pairing; PostgreSQL here is a reference choice. Native Flask/browser coverage unqualified.
- **S08: Python / Django + Django templates + PostgreSQL.** Django's ecosystem survey supports tracking the components; it does not give this exact joint share. Native Django/browser/database coverage unqualified. A separate JavaScript frontend is an optional variant, not required.
- **S09: TypeScript + Svelte/SvelteKit + Node.js + PostgreSQL.** [SvelteKit's Node adapter](https://svelte.dev/docs/kit/adapter-node) documents that deployment variant. Native Svelte/SvelteKit coverage unqualified; Svelte alone does not establish SvelteKit or a server deployment.
- **S10: PHP / Laravel + Vue or Blade/Livewire + MySQL/MariaDB.** [Laravel's starter kits](https://laravel.com/framework/docs/starter-kits) document frontend alternatives; the database is a reference choice. Native Laravel coverage unqualified. Preserve the actual frontend rather than imposing Vue.

## How this controls development

1. Finish and independently accept the already-dispatched bounded mock slice without discarding its evidence. Prioritise S01–S03 for subsequent adoption cases; do not start ten app implementations.
2. Classify each component's browser UI/API/CLI/library surface, then inspect language/runtime/framework/build details and existing commands. This list does not add automatic classification or prove a missing tool needs installation.
3. Reuse sound native checks. Record each role as applicable, N/A with reason, or unresolved. An unfamiliar stack can still use the explicit/manual adoption path.
4. Keep environment readiness separate from requirement coverage. Actual SDKs, dependencies, database/service execution and browser journeys need their existing authority and evidence. Research priority authorises none of those protected actions by itself.
5. For each targeted case, prove ordinary adoption, preservation, repeat application, meaningful failure detection and exact recovery at the relevant owning layer. Include rendered interaction only where a browser UI exists and browser execution is authorised. Use independent review and a blind public-workflow attempt before claiming completed coverage.
6. Consider S04–S05 only when the first three have coherent accepted evidence, or when a concrete transfer failure justifies changing the order. Record the reason; do not expand because an example merely has green metadata checks.
7. Popularity is not superiority or a quality waiver. Keep local/FOSS defaults and approved native equivalents. Do not introduce domain-specific mock validation rules into the general framework.

## Preservation and updates

Retain existing Go marker reporting/tests, package-manager and React declaration work, Python/native adoption evidence, Bun mock work and non-React/manual profile evidence. Keep their existing limits: a preserved Go marker or successful manual plan is not native Go readiness. Neither omission from this shortlist nor a later rank change authorises deletion, deprecation, migration or rewriting native tools.

This file is the coverage register. Update its source date, selection rationale and per-combination evidence state after material research or acceptance, not on a timer. Keep frozen historical evidence separate from current status. No new registry engine, scheduler, package installation or support restriction is part of this research.

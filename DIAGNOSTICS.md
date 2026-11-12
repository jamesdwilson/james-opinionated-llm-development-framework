# Basic diagnostics

**Parked by James; not a deployed service or an adoption prerequisite.** Hosting selection remains unresolved after the SigNoz Cloud pricing correction. Preserve the following draft and SDK evidence as research, not instructions to activate collection or choose a paid provider. No further telemetry work until explicitly resumed.

The preserved draft uses the official OpenTelemetry SDK and OTLP/HTTP exporter, readable local reports and a hosted dashboard. No local collector, database or dashboard service. Existing applications are not automatically migrated. References to SigNoz below describe the previous candidate, not a current purchase or deployment decision.

## What this does

Give a developer or coding agent a small, relevant failure record. Diagnostics help investigate behaviour; they do not establish environment readiness, ticket acceptance or evidence provenance. Public submissions are untrusted observations, never proof that a release passed its tests.

Use explicit structured operations, not automatic instrumentation of everything. Keep native tests responsible for correctness and recovery. Witness belongs to supply-chain provenance, not this path.

## Show the choice before collection

Place the notice at the top of first-run setup and installation instructions, before the first collection or upload. Keep the same setting under Privacy → Diagnostics. Suggested product copy, to use only once the described behaviour is implemented:

> **Basic diagnostics are on**
>
> We send app version, OS, broad hardware information, runtime/framework versions and operation results to SigNoz Cloud to find compatibility problems and failures. No source code, prompts, personal content or raw logs are included. SigNoz's terms permit AI model improvement using customer content.
>
> **Turn off diagnostics** · **See exactly what is sent**
>
> Turning this off does not affect the app. Your network address is visible to the receiving infrastructure even though it is not included as a report field.

The preview shows the actual complete report and destination, not only a field description. State retention and provider terms beside it. Never call these reports anonymous: combinations of otherwise ordinary attributes can identify people.

Default-on basic diagnostics is James's desired policy, not a universal consent exemption. Before public activation, the product owner must establish its applicable legal basis and whether provider secondary use is compatible. Ask first where required; do not infer jurisdiction from an IP lookup or collect location to implement this decision. Until this is resolved, leave public collection inactive. The read-only playbook itself collects nothing.

## Use established off switches

```text
OTEL_SDK_DISABLED=true
DO_NOT_TRACK=1
```

Either switch, or a persisted product setting of off, disables collection and export. Check before creating SDK providers, exporters, background workers or local diagnostic files. `DO_NOT_TRACK` is a convention the product must honour explicitly, not an OpenTelemetry feature. A product may expose `--no-telemetry`, but it is not a universal OTel CLI flag.

Off wins over every enable setting. Turning off prevents new submissions, discards queued unsent reports and stays off across restarts and upgrades. Do not send an opt-out event. Explain that already submitted data is not deleted by this control; a request already in transit may finish. Existing local files remain user-owned; do not silently delete them. Test the network boundary, not just the preference value.

## Collection contract: version 1

Use standard OpenTelemetry names for their defined meanings. Custom attributes below use `jolf.` for this playbook's schema; an adopting product should choose one documented namespace rather than add invented fields under standard namespaces.

| Field | Allowed value |
|---|---|
| `service.name` | fixed published product/component name, never a local repository name |
| `service.version` | published release version, not a private revision identifier |
| `os.type`, `os.name` | normalised operating-system family/name |
| `os.version` | major/minor only; no kernel/build string |
| `host.arch` | normalised architecture, e.g. `arm64`, `amd64` |
| `process.runtime.name`, `process.runtime.version` | actual runtime and version; do not label TypeScript as the execution runtime |
| `jolf.language.names` | recognised languages, bounded list |
| `jolf.framework.names`, `jolf.framework.versions` | aligned bounded lists of recognised frameworks; no private package names |
| `jolf.framework.version_source` | `resolved`, `declared` or `unknown`; mixed sources need separate records |
| `jolf.hardware.cpu_band` | `1-4`, `5-8`, `9-16`, `17+`, `unknown` logical CPUs |
| `jolf.hardware.ram_gib_band` | `0-8`, `9-16`, `17-32`, `33-64`, `65+`, `unknown`; round up to whole GiB before banding |
| `jolf.operation` | fixed approved operation category; never raw arguments |
| `jolf.outcome` | `success`, `failure`, `cancelled` |
| `jolf.error.category` | approved bounded category, or `unknown`; never arbitrary exception text |
| `jolf.diagnostics.schema_version` | `1` |

Trace/span identifiers are per operation, not stable installation or user identifiers. Span timing supplies duration. Attach the environment snapshot once per run/resource. Detect frameworks from project metadata locally; do not upload manifests, lockfiles or dependency inventories. Unknown remains unknown. Version strings must be validated and bounded rather than blindly copied from user-controlled metadata.

No usernames, hostname, serial/device IDs, IP/MAC fields, absolute paths, repository URLs, branch names, command lines, environment-variable dumps, request bodies, cookies, headers, prompts, source text, raw logs or exception stack traces in default reports. No broad resource detectors, ambient `OTEL_RESOURCE_ATTRIBUTES` passthrough or automatic exception recording. Explicitly allowlist resource attributes, span attributes, events and bodies; the environment variables themselves are not an uploadable configuration dump.

## Frequency, files and limits

These are project policy defaults to verify, not research-derived optimums:

- One bounded report per completed named run/operation, including successes. No idle heartbeat or upload on every commit.
- At most 100 operation records and 1 MiB of readable diagnostics per run. Stop adding records at the cap; explicitly report truncation when possible. Do not emit a second flood of truncation events.
- Store readable reports in git-ignored `.evidence/<run-id>/`. Keep routine reports seven days with a 50 MiB total cap. Implement cleanup only for owned diagnostic files after its safety contract is verified; never remove project evidence or user files indiscriminately.
- Native acceptance evidence is separate: retain exact revision, dirty-diff identity and relevant environment locally. It is not automatically uploaded as public diagnostics.
- No unbounded persistent upload queue. Offline, expired-key, cap-exhausted and failed-export paths cannot prevent the application doing its work. Use official bounded exporter timeouts/batching; prove the user-visible delay bound in the target runtime.
- Cloud retention target: 30 days, only after verifying actual plan controls. Until configured and read back, retention is unknown, not a promise.

The SDK's console JSON format may provide a readable local representation; it is not necessarily OTLP JSONL. Verify that the file and outgoing record contain the same approved semantic data. Do not invent a transport format or claim byte identity between JSON and protobuf.

## Reuse the official Python implementation

Use `opentelemetry-sdk` plus `opentelemetry-exporter-otlp-proto-http`, not a custom uploader. Explicit instrumentation avoids an instrumentation-distro dependency unless the target proves it needs one. Pin and review resolved dependencies in the consumer's isolated environment.

The inspected 1.45.2 releases require Python 3.10+. Keep the adoption core Python 3.9+ and standard-library-only; do not import the SDK into `quality-gate/doctor`, `install` or generated `gate.py`. A consumer using telemetry must supply a compatible runtime or remain explicitly unsupported for that optional feature. Do not silently alter the core minimum or install dependencies on startup.

Standard exporter settings include `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf`, and `OTEL_EXPORTER_OTLP_HEADERS`. Configure a reviewed HTTPS destination and the dedicated `signoz-ingestion-key` header. Never print headers or persist them in readable reports. Do not accept arbitrary inherited destinations for a bundled product's diagnostics.

## SigNoz Cloud and dashboard

Use a dedicated write-only ingestion key, not an account API key. SigNoz documents exposed ingestion keys for frontend use, with daily per-signal limits and expiration. Distributed CLI use applies that same threat model; it is not authentication of individual reports. Attackers may inject junk or exhaust the cap.

Before real uploads, the owner must select the account/region, approve any paid plan, create or supply the dedicated key securely, set daily size/count caps, expiry and retention, and verify those settings by readback. Never embed a management/read API key. Key rotation and public release need their own explicit step.

Build the first dashboard with native query-builder panels, not a new dashboard framework:

1. received run reports over time, grouped by outcome;
2. failure categories by product version;
3. OS and runtime/framework breakdown;
4. drill-down to the sanitised report.

Count reports, not unique users. Show collection version, selected time range and incomplete/sampled coverage; opt-outs and dropped reports prevent population-wide conclusions. Use a synthetic event to verify the filters and drill-down after account access is supplied.

## Bounded acceptance

- Both opt-outs prevent diagnostic files, SDK export and network traffic; test each independently.
- Notice precedes collection; settings persist; no surprise re-enable.
- Sensitive sentinel strings in ambient environment, paths, errors and payloads never appear in local or transmitted reports.
- Success, failure, unknown framework, caps and offline/expired-key cases behave as specified.
- Local readable representation matches the allowed semantic content of the real OTLP payload.
- No extra daemon, collector, database or local dashboard is installed.
- One synthetic report is found in the chosen cloud dashboard with correct filters, only after cloud access and activation approval.
- Independent review checks the exact candidate. Local SDK tests do not establish consumer installation, cloud acceptance, legal compliance or population representativeness.

## Sources and evidence limits

Official documentation establishes capabilities, not a measured coding-speed gain:

- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)
- [SDK environment variables](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/)
- [Sensitive-data handling](https://opentelemetry.io/docs/security/handling-sensitive-data/)
- [Resource conventions](https://opentelemetry.io/docs/specs/semconv/resource/)
- [Attribute naming](https://opentelemetry.io/docs/specs/semconv/general/naming/)
- [DO_NOT_TRACK convention](https://donottrack.sh/)
- [SigNoz ingestion keys](https://signoz.io/docs/ingestion/signoz-cloud/keys/)
- [SigNoz dashboards](https://signoz.io/docs/dashboards/overview/)
- [SigNoz terms](https://signoz.io/legal/terms-of-service/)
- [ICO exceptions guidance](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-the-use-of-storage-and-access-technologies/what-are-the-exceptions/)

Research does not establish SigNoz as universally best, default-on as universally lawful, or these collection limits as optimal. The consumer implementation and live account remain separate acceptance gates.

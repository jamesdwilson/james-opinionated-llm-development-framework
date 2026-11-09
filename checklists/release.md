# Cohesive-stack completion check

Use the target repository's own release and approval process. Mark a role N/A only with a product-specific reason.

## Intent and examples

- [ ] The Project Brief identifies authorities, stakeholders, requirements, constraints, acceptance conditions, assumptions, risks, and decisions.
- [ ] BDD rules, examples, and questions cover the representative slice.
- [ ] Requirement IDs connect the brief, journeys, checks, and evidence.

## Implementation

- [ ] Changed behaviour has a meaningful RED record, or behaviour-preserving work has a verified characterisation baseline.
- [ ] GREEN supplies passing deterministic evidence for the affected acceptance condition at an appropriate layer.
- [ ] Refactoring kept the relevant checks green.
- [ ] Existing affected test and build requirements passed.

## Rendered product

- [ ] Playwright or an established equivalent exercises each applicable critical rendered journey.
- [ ] Assertions cover visible outcomes and state required by the journey.
- [ ] Midscene is bounded to declared visual questions, with its local validation status recorded.
- [ ] Validated Midscene status links to the exact configuration's human-labelled sample, agreement criteria, observed result, and responsible approver.
- [ ] Midscene does not overrule deterministic failure.

## Failure and operations

- [ ] A relevant operational failure or synthetic error is exercised when the change affects that boundary.
- [ ] Bugsink or an isolated equivalent receives the expected synthetic event.
- [ ] Sensitive fields remain absent.
- [ ] User state, recovery, and cleanup match the requirement.

## Supply chain

- [ ] The lockfile or resolved graph is identified.
- [ ] The package-manager audit completed and exceptions name an owner.
- [ ] Audit-skipped scoped registries are recorded.
- [ ] The project's release-age or package-admission policy was applied where relevant.
- [ ] Release-age applicability, existing-lockfile exclusions, and exemptions are recorded.

## Evidence and review

- [ ] The project-native candidate or artefact identity is recorded.
- [ ] Each final report identifies the evaluated candidate and relevant environment, directly or through a run record.
- [ ] RED is tied to its earlier candidate and remains separate from final-candidate evidence.
- [ ] A candidate change caused affected checks to run again.
- [ ] Commands, procedures, observed results, reports, and evidence limits are recorded.
- [ ] Tool substitutions or N/A roles have reasons.
- [ ] Missing authorization, unavailable tooling, and unexecuted required roles are blocked or not run, not N/A.
- [ ] The target repository's required review and release process completed.
- [ ] Unresolved claims and risks name the responsible owner and next action.

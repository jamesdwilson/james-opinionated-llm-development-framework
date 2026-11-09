import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { describe, expect, test } from 'bun:test';

const root = new URL('../research/community/', import.meta.url);
const artifactNames = [
  'COMMUNITY_STACK_REPORT.md',
  'COMMUNITY_STACK_REPORT.json',
  'SOURCES.json',
];
const testingArtifactNames = artifactNames.map(name => name.replace('STACK', 'TESTING'));
testingArtifactNames[2] = 'SOURCES.json';

const readText = path => readFile(new URL(path, root), 'utf8');
const readJson = async path => JSON.parse(await readText(path));
const sha256 = value => createHash('sha256').update(value).digest('hex');

function collectSourceIds(value, found = new Set()) {
  if (Array.isArray(value)) {
    for (const item of value) collectSourceIds(item, found);
  } else if (value && typeof value === 'object') {
    for (const [key, item] of Object.entries(value)) {
      if (key === 'source_ids' && Array.isArray(item)) {
        for (const id of item) found.add(id);
      } else {
        collectSourceIds(item, found);
      }
    }
  }
  return found;
}

async function verifyResearchSet(directory, reportName) {
  const report = await readJson(`${directory}/${reportName}`);
  const ledger = await readJson(`${directory}/SOURCES.json`);
  const referenced = collectSourceIds(report);
  const sources = new Map(ledger.sources.map(source => [source.id, source]));

  expect([...referenced].filter(id => !sources.has(id))).toEqual([]);
  expect([...sources.values()].filter(source => source.used_as_evidence !== false && !referenced.has(source.id)).map(source => source.id)).toEqual([]);
  expect([...sources.values()].filter(source => source.used_as_evidence === false && referenced.has(source.id)).map(source => source.id)).toEqual([]);
  return { report, ledger, referenced };
}

describe('locked community research evidence', () => {
  test('preserves both complete research artifact sets', async () => {
    for (const name of artifactNames) expect(await readFile(new URL(`application/${name}`, root))).toBeInstanceOf(Uint8Array);
    for (const name of testingArtifactNames) expect(await readFile(new URL(`testing/${name}`, root))).toBeInstanceOf(Uint8Array);
  });

  test('resolves every used source and excludes access-gap records from findings', async () => {
    const application = await verifyResearchSet('application', 'COMMUNITY_STACK_REPORT.json');
    const testing = await verifyResearchSet('testing', 'COMMUNITY_TESTING_REPORT.json');
    expect(application.ledger.sources.filter(source => source.used_as_evidence !== false)).toHaveLength(34);
    expect(testing.ledger.sources.filter(source => source.used_as_evidence === true)).toHaveLength(33);
    expect(testing.ledger.sources.filter(source => source.used_as_evidence === false)).toHaveLength(6);
  });

  test('records truthful model provenance rather than claiming independent read-back', async () => {
    for (const [directory, reportName] of [
      ['application', 'COMMUNITY_STACK_REPORT.json'],
      ['testing', 'COMMUNITY_TESTING_REPORT.json'],
    ]) {
      const report = await readJson(`${directory}/${reportName}`);
      const execution = report.execution ?? report.model_constraint;
      expect(execution.requested_model ?? execution.requested).toBe('gpt-6-astra');
      expect(execution.requested_reasoning ?? execution.reasoning_effort).toBe('medium');
      expect(execution.model_setting_verified ?? execution.verified).toBe(false);
      const limitation = execution.model_limitation ?? execution.note;
      expect(limitation).toContain('explicit');
      expect(limitation).toContain('JSONL');
      expect(limitation).toContain('independent read-back');
    }
  });

  test('locks the less-first admission and overlap decisions', async () => {
    const decisions = await readJson('STACK_DECISIONS.json');
    expect(decisions.principle).toBe('less');
    expect(decisions.deterministic_authority).toEqual([
      'Bun tests and type/build checks',
      'HTTP, contract, property and integration checks at their owning boundaries',
      'Playwright Test for critical rendered journeys',
      'Bugsink injected-event readback for error-delivery acceptance',
      'Exact pins, lockfile hashes, seven-day quarantine and one advisory triage queue',
    ]);
    expect(decisions.probabilistic_boundary).toMatchObject({
      tool: 'Midscene',
      status: 'bounded_optional',
      may_override_deterministic_failure: false,
      unclear_passes: false,
    });
    expect(decisions.admission.not_admitted).toEqual(expect.arrayContaining([
      'Playwright CLI',
      'Playwright MCP',
      'Hurl',
      'Schemathesis',
      'Pact',
      'Elysia/Eden migration',
      'Sentry alongside Bugsink',
      'additional overlapping advisory scanners',
    ]));
    expect(decisions.overlap_rules).toEqual(expect.arrayContaining([
      'one routine browser-control interface',
      'one owner for each HTTP scenario',
      'one error destination',
      'one primary advisory queue',
      'one contract authority per application boundary',
    ]));
    expect(decisions.llm_productivity.evidence_status).toBe('not_proven_by_community_research');
    expect(decisions.llm_productivity.measure).toEqual(expect.arrayContaining([
      'successful-task tool turns',
      'repair turns',
      'escaped contract mistakes',
      'dependencies introduced',
    ]));
  });

  test('binds every preserved artifact and decision file to a sha256 manifest', async () => {
    const manifest = await readJson('RESEARCH_MANIFEST.json');
    expect(manifest.schema_version).toBe('1.0');
    expect(manifest.files.length).toBe(8);
    for (const artifact of manifest.files) {
      const bytes = await readFile(new URL(artifact.path, root));
      expect(sha256(bytes), artifact.path).toBe(artifact.sha256);
    }
  });

  test('binds the locked research into the exact candidate identity', async () => {
    const { candidatePaths } = await import('../scripts/candidate.mjs');
    expect(candidatePaths).toContain('research');
  });
});

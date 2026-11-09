import { spawn } from 'node:child_process';
import { auditOutputPassed } from './acceptance-contract.mjs';

const child = spawn(process.execPath, ['audit', '--json'], {
  cwd: process.cwd(),
  env: { PATH: '/opt/homebrew/bin:/usr/bin:/bin', HOME: process.env.HOME },
  stdio: ['ignore', 'pipe', 'pipe'],
});
let stdout = '';
let stderr = '';
child.stdout.on('data', chunk => {
  stdout += chunk;
  if (stdout.length > 1024 * 1024) child.kill('SIGKILL');
});
child.stderr.on('data', chunk => {
  stderr += chunk;
  if (stderr.length > 1024 * 1024) child.kill('SIGKILL');
});
const exit = await new Promise(resolve => {
  child.once('error', () => resolve(1));
  child.once('close', code => resolve(code ?? 1));
});
let audit;
try {
  audit = JSON.parse(stdout);
} catch {
  audit = { invalidAuditOutput: true };
}
const plainObject = audit !== null &&
  typeof audit === 'object' &&
  !Array.isArray(audit) &&
  Object.getPrototypeOf(audit) === Object.prototype;
const advisories = plainObject
  ? Object.values(audit).reduce(
      (total, value) => total + (Array.isArray(value) ? value.length : 1),
      0,
    )
  : 1;
const passed = auditOutputPassed(exit, stdout, stderr);
console.log(JSON.stringify({ passed, advisories, audit }));
process.exitCode = passed ? 0 : 1;

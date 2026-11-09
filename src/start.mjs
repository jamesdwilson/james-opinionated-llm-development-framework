import { mkdir } from 'node:fs/promises';
import { createTaskServer } from './server.mjs';
await mkdir(new URL('../.tmp/', import.meta.url), { recursive: true });
const server = createTaskServer({ databasePath: new URL('../.tmp/manual.sqlite', import.meta.url).pathname });
const address = await server.listen(0);
console.log(`Household lab: http://127.0.0.1:${address.port}`);
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, async () => { await server.close(); process.exit(0); });

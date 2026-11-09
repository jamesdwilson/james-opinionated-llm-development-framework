import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const reviewsPath = new URL('../e2e/reviews.spec.ts', import.meta.url);

test('J05 verdict rubric treats a visible unexplained required choice as RED rather than UNCLEAR', async () => {
  const source = await readFile(reviewsPath, 'utf8');

  assert.match(
    source,
    /RED[^\n]*required choice[^\n]*practical consequences[^\n]*guess or stop/i,
    'The model rubric must classify a fully visible required choice with no practical consequences as a RED obstacle.',
  );
  assert.match(
    source,
    /UNCLEAR[^\n]*capture[^\n]*does not show[^\n]*required choice/i,
    'UNCLEAR must be reserved for insufficient observation rather than a clearly observed ambiguous blocker.',
  );
});

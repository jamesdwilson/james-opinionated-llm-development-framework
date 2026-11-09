import {spawn} from 'node:child_process';
import {prescribed,validateReviewConfig} from './review-config.mjs';
// No inherited provider values are copied. Reject unexpected keys before spawning.
const env={...process.env,...prescribed};validateReviewConfig(env);
const child=spawn(process.execPath,['node_modules/@playwright/test/cli.js','test','e2e/reviews.spec.ts'],{env,stdio:'inherit'});
child.once('exit',code=>{process.exitCode=code??1;});child.once('error',()=>{process.exitCode=1;});

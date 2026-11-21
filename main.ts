// gta6-meme-x-01 round 4 entry (Node 22, standard library only).
//
// It copies POST.json from this repository to the output directory, where
// the gate reads it. That is all the program has to do: the entry is the
// X post itself. The house reads the post from X (its first picture, the
// doctor's-note meme, and its text) and hands that to the judge.
//
// POST.json as committed holds a placeholder address, so the gate refuses
// it as it stands (valid 0) until the real post URL is put in. That is on
// purpose: a placeholder that passed would need no post at all.
//
// Paths: POST.json is resolved relative to this script file itself
// (import.meta.url), never relative to the working directory, so the
// program works no matter where it is invoked from. The output directory
// comes from MAKEFUN_OUTPUT_DIR, defaulting to /output.
//
// Outside the grader's container:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const SOURCE_PATH = join(SCRIPT_DIR, 'POST.json');
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const OUTPUT_PATH = join(OUTPUT_DIR, 'POST.json');

// An X post address, as X shows it: x.com or twitter.com (www. or
// mobile. before either), /status/<id>. The id here is the digits X
// assigns, or the literal PLACEHOLDER until the real post is put in.
const POST_URL_PATTERN =
  /^https:\/\/(www\.|mobile\.)?(x\.com|twitter\.com)\/[^/]+\/status\/[^/?#]+$/;
const MAX_POST_BYTES = 16384;

function fail(message: string): never {
  console.error(`main.ts: ${message}`);
  process.exit(1);
}

let raw: string;
try {
  raw = readFileSync(SOURCE_PATH, 'utf8');
} catch (err) {
  fail(`POST.json could not be read from ${SOURCE_PATH}: ${(err as Error).message}`);
}

if (Buffer.byteLength(raw, 'utf8') > MAX_POST_BYTES) {
  fail(`POST.json is over ${MAX_POST_BYTES} bytes`);
}

let parsed: unknown;
try {
  parsed = JSON.parse(raw);
} catch (err) {
  fail(`POST.json is not valid JSON: ${(err as Error).message}`);
}

if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
  fail('POST.json must be a JSON object');
}
const url = (parsed as { url?: unknown }).url;
if (typeof url !== 'string' || !POST_URL_PATTERN.test(url)) {
  fail('POST.json url must be an X post address (https://x.com/<handle>/status/<id>)');
}

mkdirSync(OUTPUT_DIR, { recursive: true });
try {
  copyFileSync(SOURCE_PATH, OUTPUT_PATH);
} catch (err) {
  fail(`POST.json could not be copied to ${OUTPUT_PATH}: ${(err as Error).message}`);
}

// The copy must be byte for byte the source: the gate reads the output.
const copied = readFileSync(OUTPUT_PATH);
if (!copied.equals(Buffer.from(raw, 'utf8'))) {
  fail('copied POST.json differs from the source');
}

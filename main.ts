// news-image-20261122 v3 — one-day world news image (Node 22, stdlib only).
//
// The entry is the entry.png beside this file: a 1024x1024 newspaper front
// page summing up Sunday 22 November 2026 in 35 dated stories across 7
// regions (hero: COP31 collapses with no deal in Antalya; then Europe,
// Middle East, Asia, North America, Latin America, Africa, Oceania &
// Pacific, plus a Markets & Tech cell). This program writes that exact
// image to the output directory, so the judge sees precisely these bytes.
// It refuses to finish unless the copy is a whole PNG of the size the
// competition allows.
//
// Outside the grader, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const src = join(here, 'entry.png');
const dest = join(outDir, 'entry.png');

const bytes = readFileSync(src);
const pngMagic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!bytes.subarray(0, 8).equals(pngMagic)) {
  throw new Error(`entry image is not a PNG: ${src}`);
}
if (bytes.length > 1048576) {
  throw new Error(`entry image is ${bytes.length} bytes, over the 1 MiB cap`);
}
// The IHDR chunk follows the 8-byte signature: 4-byte length, 4-byte type
// "IHDR", then width and height as 4-byte big-endian integers. The
// competition allows at most 1024 by 1024 pixels, so refuse anything
// bigger here instead of letting an oversized image reach the judge.
if (bytes.length < 29 || bytes.toString('ascii', 12, 16) !== 'IHDR') {
  throw new Error(`entry image has no IHDR chunk: ${src}`);
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  throw new Error(`entry image is ${width}x${height}, over the 1024x1024 cap`);
}
// A whole PNG ends with the IEND chunk: 4-byte length 0, type "IEND",
// then a 4-byte CRC. Refuse a truncated file instead of letting the
// judge see half an image.
const iend = bytes.subarray(bytes.length - 12);
if (iend.readUInt32BE(0) !== 0 || iend.toString('ascii', 4, 8) !== 'IEND') {
  throw new Error(`entry image has no IEND chunk, it may be truncated: ${src}`);
}

mkdirSync(outDir, { recursive: true });
writeFileSync(dest, bytes);

const { size } = statSync(dest);
if (size !== bytes.length) {
  throw new Error(`copy mismatch: wrote ${size} of ${bytes.length} bytes`);
}
console.log(`wrote ${dest} (${size} bytes)`);

#!/usr/bin/env node
/** Dựng bundle build-time cho engine/excalidraw.py.
 *
 *  Vì sao cần bước này: mermaid-to-excalidraw và exportToSvg đều là ESM có cây
 *  phụ thuộc sâu và cần DOM. Chromium không nạp thẳng được từ node_modules,
 *  nên gộp sẵn thành một file. Bundle ~13MB nhưng CHỈ build dùng, không lên site.
 *
 *  Chạy lại sau mỗi lần `npm install`. build.py tự gọi khi thiếu file.
 */
import { build } from 'esbuild';
import path from 'node:path';
import { mkdirSync, writeFileSync } from 'node:fs';

const root = path.join(import.meta.dirname, '..');
const cache = path.join(root, '.cache');
mkdirSync(cache, { recursive: true });

const entry = path.join(cache, 'exca-entry.js');
writeFileSync(entry, `
import { parseMermaidToExcalidraw } from '@excalidraw/mermaid-to-excalidraw';
import { exportToSvg, convertToExcalidrawElements, FONT_FAMILY } from '@excalidraw/excalidraw';
Object.assign(window, {
  __m2e: parseMermaidToExcalidraw,
  __toSvg: exportToSvg,
  __conv: convertToExcalidrawElements,
  __FF: FONT_FAMILY,
  __ready: true,
});
`);

await build({
  entryPoints: [entry],
  bundle: true,
  format: 'esm',
  outfile: path.join(cache, 'exca.bundle.js'),
  define: { 'process.env.NODE_ENV': '"production"' },
  loader: { '.woff2': 'dataurl', '.ttf': 'dataurl', '.png': 'dataurl', '.svg': 'dataurl' },
  logLevel: 'error',
});
console.log('✓ .cache/exca.bundle.js');

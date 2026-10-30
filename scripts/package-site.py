#!/usr/bin/env python3
"""Package the already-reviewed report; never fetch sources or rebuild charts."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'index.html').read_text()
for marker in ['<!-- part3:start -->','id="p3-safety-rate-chart"','id="p3-growth-ratio-chart"']:
    if marker not in html:raise SystemExit(f'Report is not built: missing {marker}')
for marker in ['__P3_DATA__','__SAFETY_DATA__','__COMBINED_JS__']:
    if marker in html:raise SystemExit(f'Unrendered report placeholder: {marker}')
site=ROOT/'dist'
site.mkdir(exist_ok=True)
# Netlify receives a dedicated publish directory, never the source repository.
shutil.copyfile(ROOT/'index.html',site/'index.html')
shutil.copyfile(ROOT/'LICENSE',site/'LICENSE.txt')
(site/'archive').mkdir(exist_ok=True)
shutil.copyfile(ROOT/'archive/report-2026-08-10.html',site/'archive/report-2026-08-10.html')
print(f'Packaged {len(html.encode()):,} bytes of self-contained HTML into dist/.')

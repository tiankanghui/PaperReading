#!/usr/bin/env python3
"""Extract attributed figure/table screenshots from the local source PDFs.

Requires Pillow and Poppler. This script is optional; CI uses committed PNGs.
"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FIGURES = [
    ('cua-gym', 'cua-gym.pdf', 3, 'overview', (0.11, 0.08, 0.89, 0.39)),
    ('cua-gym', 'cua-gym.pdf', 4, 'environment-pipeline', (0.11, 0.08, 0.89, 0.325)),
    ('cua-gym', 'cua-gym.pdf', 8, 'data-scaling', (0.11, 0.08, 0.89, 0.36)),
    ('cua-gym', 'cua-gym.pdf', 8, 'environment-scaling', (0.51, 0.50, 0.90, 0.79)),
    ('gamedevbench', 'gamedevbench.pdf', 2, 'overview', (0.09, 0.08, 0.91, 0.425)),
    ('gamedevbench', 'gamedevbench.pdf', 7, 'results', (0.09, 0.07, 0.91, 0.59)),
    ('gamecraft-bench', 'gamecraft-bench.pdf', 6, 'overview', (0.10, 0.51, 0.90, 0.86)),
    ('gamecraft-bench', 'gamecraft-bench.pdf', 11, 'results', (0.11, 0.10, 0.91, 0.30)),
    ('swe-game', '2609.33678v3.pdf', 3, 'overview', (0.14, 0.09, 0.86, 0.49)),
    ('swe-game', '2609.33678v3.pdf', 8, 'results', (0.11, 0.10, 0.91, 0.705)),
]


def extract():
    bundled = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm'
    executable = shutil.which('pdftoppm') or (str(bundled) if bundled.exists() else None)
    if not executable:
        raise SystemExit('pdftoppm is required; use the bundled PDF runtime or install Poppler.')
    with tempfile.TemporaryDirectory(prefix='paper-figures-') as folder:
        temporary = Path(folder)
        env = os.environ.copy()
        if Path('/System/Library/Fonts').exists():
            (temporary / 'cache').mkdir()
            fontconfig = temporary / 'fonts.conf'
            fontconfig.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig><dir>/System/Library/Fonts</dir><dir>/Library/Fonts</dir><cachedir>' + str(temporary / 'cache') + '</cachedir></fontconfig>')
            env['FONTCONFIG_FILE'] = str(fontconfig)
        for slug, filename, page, name, bounds in FIGURES:
            source = ROOT / 'papers' / filename
            if not source.exists():
                raise FileNotFoundError('Missing local source PDF: ' + filename)
            prefix = temporary / (slug + '-' + name)
            with (temporary / 'render.log').open('w') as log:
                subprocess.run([executable, '-f', str(page), '-l', str(page), '-scale-to', '2400', '-png', '-singlefile', str(source), str(prefix)], env=env, stdout=log, stderr=log, timeout=60, check=True)
            with Image.open(prefix.with_suffix('.png')) as image:
                width, height = image.size
                crop = image.crop(tuple(round(value * (width if i % 2 == 0 else height)) for i, value in enumerate(bounds))).convert('RGB')
                destination = ROOT / 'papers' / slug / 'images' / (name + '.png')
                destination.parent.mkdir(parents=True, exist_ok=True)
                crop.save(destination, optimize=True)
                print('{}: PDF page {} → {}'.format(slug, page, destination.relative_to(ROOT)))


if __name__ == '__main__':
    extract()

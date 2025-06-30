#!/usr/bin/env python3
"""
build_svg.py

Automatisches Kombinieren von zwei SVG-Dateien in eine gemeinsame SVG mit <symbol> und <use>,
inklusive optionalem PNG-Export über Inkscape.

Usage:
  chmod +x build_svg.py
  ./build_svg.py matrix.svg telegram.svg combined.svg \
      --main-size 400 400 \
      --badge-size 100 100 \
      --main-scale 0.9 \
      --export-png
"""

import argparse
import re
import sys
import subprocess
import os

def extract_inner(svg_path):
    try:
        text = open(svg_path, 'r', encoding='utf-8').read()
    except IOError:
        sys.exit(f"Fehler: Datei nicht gefunden – {svg_path}")
    inner = re.sub(r'(?is)<svg[^>]*>', '', text)
    inner = re.sub(r'(?is)</svg>', '', inner)
    return inner.strip()

def get_viewbox(svg_path):
    text = open(svg_path, 'r', encoding='utf-8').read()
    m = re.search(r'viewBox=["\']([^"\']+)["\']', text)
    return m.group(1) if m else None

def main():
    parser = argparse.ArgumentParser(
        description="SVG-Kombinator: zwei SVGs zu einer machen, mit Skalierung und PNG-Export")
    parser.add_argument('base',    help='Pfad zur Haupt-SVG (z.B. matrix.svg)')
    parser.add_argument('badge',   help='Pfad zur Badge-SVG (z.B. telegram.svg)')
    parser.add_argument('output',  help='Zieldatei für die kombinierte SVG (z.B. combined.svg)')
    parser.add_argument('--main-size',    nargs=2, type=int, default=[24,24],
                        metavar=('W','H'),
                        help='Output-Viewbox (W H), Standard 24×24')
    parser.add_argument('--badge-size',   nargs=2, type=int, default=[6,6],
                        metavar=('w','h'),
                        help='Badge-Größe (w h), Standard 6×6')
    parser.add_argument('--badge-offset', nargs=2, type=int, metavar=('x','y'),
                        help='Badge-Offset (x y), Standard unten-rechts')
    parser.add_argument('--main-scale',   type=float, default=1.0,
                        help='Skalierung Haupt-Icon (0.0–1.0), Standard 1.0')
    parser.add_argument('--export-png',   action='store_true',
                        help='Erzeuge zusätzlich eine PNG-Datei via Inkscape')

    args = parser.parse_args()

    base_w, base_h   = args.main_size
    badge_w, badge_h = args.badge_size
    scale = args.main_scale

    # Berechne Haupt-Icon-Größe und Position (zentriert)
    main_w = int(base_w * scale)
    main_h = int(base_h * scale)
    main_x = (base_w - main_w) // 2
    main_y = (base_h - main_h) // 2

    # Badge-Offset
    if args.badge_offset:
        badge_x, badge_y = args.badge_offset
    else:
        badge_x = base_w - badge_w
        badge_y = base_h - badge_h

    # Extrahiere Grafikinhalte und viewBox
    base_inner  = extract_inner(args.base)
    badge_inner = extract_inner(args.badge)
    base_vb  = get_viewbox(args.base)  or f"0 0 {main_w} {main_h}"
    badge_vb = get_viewbox(args.badge) or f"0 0 {badge_w} {badge_h}"

    # Schreibe combined.svg
    with open(args.output, 'w', encoding='utf-8') as out:
        out.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{base_w}" height="{base_h}">\n')
        out.write('  <defs>\n')
        out.write(f'    <symbol id="matrix"  viewBox="{base_vb}">\n{base_inner}\n    </symbol>\n')
        out.write(f'    <symbol id="telegram" viewBox="{badge_vb}">\n{badge_inner}\n    </symbol>\n')
        out.write('  </defs>\n')
        out.write(f'  <use href="#matrix"   x="{main_x}" y="{main_y}" '
                  f'width="{main_w}" height="{main_h}"/>\n')
        out.write(f'  <use href="#telegram" x="{badge_x}" y="{badge_y}" '
                  f'width="{badge_w}" height="{badge_h}"/>\n')
        out.write('</svg>\n')

    print(f"SVG exportiert: {args.output}")

    # Optional PNG-Export
    if args.export_png:
        png_path = os.path.splitext(args.output)[0] + '.png'
        try:
            subprocess.run([
                'inkscape', args.output,
                '--export-type=png',
                '--export-filename', png_path,
                '--export-width', str(base_w),
                '--export-height', str(base_h)
            ], check=True)
            print(f"PNG exportiert: {png_path}")
        except Exception as e:
            print(f"Fehler beim PNG-Export: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()


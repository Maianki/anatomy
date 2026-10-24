#!/bin/sh
# Rebuild every data file the site loads.
# Usage: build/all.sh <path to @dagno/anatomy-model package>/model <output dir, e.g. site/data>
# Order matters: build3.py (lungs) and build5.py (brain) record meshes with data errors, which build.py (body) leaves out.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=$1
OUT=$2
OS="$HERE/../sources/openstax"
mkdir -p "$OUT"
python3 -I "$HERE/build3.py" "$SRC" "$OUT"   # lungs
python3 -I "$HERE/build5.py" "$SRC" "$OUT"   # brain + head context
python3 -I "$HERE/build.py" "$SRC" "$OUT"    # whole body
python3 -I "$HERE/build2.py" "$SRC" "$OUT"   # heart + thorax context
python3 -I "$HERE/build4.py" "$SRC" "$OUT"   # liver, digestive tract, urinary + abdomen context
python3 -I "$HERE/content_heart.py" "$OS/m46676.cnxml" "$OUT/heart2.json" "$OUT/content-heart.json"
python3 -I "$HERE/content_lungs.py" "$OS" "$OUT/lungs.json" "$OUT/content-lungs.json"
python3 -I "$HERE/content_abdomen.py" "$OS" "$OUT"
python3 -I "$HERE/content_brain.py" "$OS" "$OUT" "$SRC"
python3 -I "$HERE/content_body.py" "$OS" "$OUT"
python3 -I "$HERE/content_sources.py" "$OUT" "$SRC/.."   # Sources screen: sections and quote counts actually used
for n in body heart2 thorax lungs liver gut urinary abdomen brain head; do
  base64 < "$OUT/$n.bin.gz" | tr -d '\n' > "$OUT/$n.gz.txt"
  rm "$OUT/$n.bin.gz"
done

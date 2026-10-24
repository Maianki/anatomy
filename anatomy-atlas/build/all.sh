#!/bin/sh
# Rebuild every data file the site loads.
# Usage: build/all.sh <path to @dagno/anatomy-model package>/model <output dir, e.g. site/data>
# Order matters: build3.py (lungs) writes the list of misplaced meshes that build.py (body) leaves out.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=$1
OUT=$2
OS="$HERE/../sources/openstax"
mkdir -p "$OUT"
python3 -I "$HERE/build3.py" "$SRC" "$OUT"
python3 -I "$HERE/build.py" "$SRC" "$OUT"
python3 -I "$HERE/build2.py" "$SRC" "$OUT"
python3 -I "$HERE/content_heart.py" "$OS/m46676.cnxml" "$OUT/heart2.json" "$OUT/content-heart.json"
python3 -I "$HERE/content_lungs.py" "$OS" "$OUT/lungs.json" "$OUT/content-lungs.json"
for n in body heart2 thorax lungs; do
  base64 < "$OUT/$n.bin.gz" | tr -d '\n' > "$OUT/$n.gz.txt"
  rm "$OUT/$n.bin.gz"
done

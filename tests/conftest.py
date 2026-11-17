import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
# ve.py tự thêm engine/ vào sys.path khi import, nhưng import theme trực tiếp
# (không qua ve) cũng cần đường dẫn này.
for p in (str(ROOT / 'scripts'), str(ROOT / 'engine')):
    if p not in sys.path:
        sys.path.insert(0, p)

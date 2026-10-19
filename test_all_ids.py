import re
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

with open("static/demo.html", "r", encoding="utf-8") as f:
    content = f.read()

js_ids = set(re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", content))
html_ids = set(re.findall(r'id=["\']([^"\']+)["\']', content))

missing = js_ids - html_ids
print("MISSING IDs:", missing)

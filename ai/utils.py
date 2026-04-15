# ai/utils.py

import os
import io
import zipfile

# -----------------------------------------------------
# Website Generator Class (Preview)
# -----------------------------------------------------
class WebsiteGenerator:
    def combine_to_html(self, files):
        html = files.get("index.html", "")
        css = files.get("styles.css", "")
        js = files.get("script.js", "")

        return f"""
<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<style>{css}</style>
</head>
<body>
{html}
<script>{js}</script>
</body>
</html>
"""


# -----------------------------------------------------
# ZIP creator
# -----------------------------------------------------
def create_zip_bytes(files: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content.encode("utf-8"))
    buf.seek(0)
    return buf.getvalue()

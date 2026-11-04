"""Export a fully offline single-file preview, with actual product photos embedded."""
from pathlib import Path
import base64
import re
root = Path(__file__).resolve().parents[1]
html = (root / 'index.html').read_text()
css = (root / 'style.css').read_text()
js = (root / 'app.js').read_text()
for path in (root / 'assets/products').iterdir():
    if path.suffix not in ('.jpg', '.png', '.webp'):
        continue
    mime = {'.jpg':'image/jpeg','.png':'image/png','.webp':'image/webp'}[path.suffix]
    encoded = base64.b64encode(path.read_bytes()).decode()
    js = js.replace('/assets/products/' + path.name, 'data:' + mime + ';base64,' + encoded)
js = js.replace("$('#share').onclick=async()=>{try{", "$('#share').onclick=async()=>{if(location.protocol==='file:'){toast('This is a local preview. Host the site to share a link.');return;}try{")
assert '/assets/products/' not in js, 'A product image is missing from the offline export'
html = html.replace('<link rel="stylesheet" href="/style.css">', '<style>' + css + '</style>')
html = html.replace('<script type="module" src="/app.js"></script>', '')
html = html.replace('</body>', '<script>' + js + '</script></body>')
destination = root.parent / 'Things-to-get-me.html'
destination.write_text(html)
print('Offline preview exported:', destination)

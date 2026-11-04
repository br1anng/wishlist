"""Build the self-contained preview and its downloadable ZIP."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import runpy
root=Path(__file__).resolve().parents[1]
runpy.run_path(str(root/'scripts/export-preview.py'))
html=(root.parent/'Things-to-get-me.html').read_bytes()
archive_path=root.parent/'Things-to-get-me.zip'
with ZipFile(archive_path,'w',ZIP_DEFLATED) as archive:
    archive.writestr('Things-to-get-me/index.html',html)
    archive.writestr('Things-to-get-me/READ-ME.txt','THINGS TO GET ME — 30 WISHES\n\nUnzip this folder and open index.html from Finder/File Explorer in Chrome or Safari. The chat code viewer displays HTML as text.\n\nBrowse category tabs and previous/next scene buttons. Budgets are VND wishlist targets, not live seller prices. The small Naruto minifigure budget is about 30,000 VND. New wishes without a budget are labeled and hidden by finite price filters.\n\nLocal product-reference images and styles are embedded. Online Blokees photos and some book covers need Internet access. If a cover cannot load, a clearly labeled title link is shown; no fictional edition cover is substituted. Shopping links also need Internet.\n\nRexy/Roxy references are user-approved Mini GT models. The separate Porsche GT3 R uses Mini GT #770 as a reference; the requested Pop Race release is not verified. Covers may show original-language editions; confirm translation and edition before buying.\n')
    archive.write(root/'assets/products/sources.json','Things-to-get-me/photo-sources.json')
    archive.write(root/'assets/PatrickHand-OFL.txt','Things-to-get-me/PatrickHand-OFL.txt')
    archive.write(root/'assets/LilitaOne-OFL.txt','Things-to-get-me/LilitaOne-OFL.txt')
    archive.write(root/'assets/products/kindle-dash-LICENSE.txt','Things-to-get-me/kindle-dash-LICENSE.txt')
with ZipFile(archive_path) as archive:
    assert archive.testzip() is None
    assert archive.read('Things-to-get-me/index.html')==html
print('ZIP verified:',archive_path)

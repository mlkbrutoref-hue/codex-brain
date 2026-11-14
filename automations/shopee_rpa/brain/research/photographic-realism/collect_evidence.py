"""Read-only source collection for this research; not a generation provider."""
from pathlib import Path
import json, re, hashlib, html, concurrent.futures
import requests
from PIL import Image, ExifTags
import fitz

ROOT = Path(__file__).resolve().parent
MEDIA = ROOT / 'evidence'
MEDIA.mkdir(exist_ok=True)
HEAD = {'User-Agent': 'PhotographyResearch/1.0 (source attribution; private research)'}
SOURCES = [
 ('R01', 'https://commons.wikimedia.org/wiki/File:Portrait_with_natural_light_(Creative_Commons).jpg', 'commons'),
 ('R02', 'https://commons.wikimedia.org/wiki/File:Natural_Light_Portrait_of_Rosie_(20710648621).jpg', 'commons'),
 ('R03', 'https://commons.wikimedia.org/wiki/File:Freckles_(1351739811).jpg', 'commons'),
 ('R04', 'https://commons.wikimedia.org/wiki/File:FrecklesCloseup.jpg', 'commons'),
 ('P01', 'https://www.pinterest.com/pin/photo-by-philip-white-on-unsplash-in-2024--1097330265444341450/', 'pinterest'),
 ('P02', 'https://uk.pinterest.com/pin/a-window-light-portrait-on-a-very-sunny-day--374502525235873685/', 'pinterest'),
 ('R05', 'https://www.fimeko.fi/pdf/Creating_long_and_even_highlights_with_softboxes.pdf', 'pdf'),
 ('R06', 'https://people.csail.mit.edu/hasinoff/pubs/HasinoffEtAl16-hdrplus-preprint.pdf', 'pdf'),
 ('T01', 'https://www.pauldebevec.com/Research/LS/debevec-siggraph2000-high.pdf', 'pdf'),
 ('T02', 'https://www.cs.cornell.edu/~srm/publications/SG03-hair.pdf', 'pdf'),
]
DIRECT = {
 'R01':'https://upload.wikimedia.org/wikipedia/commons/6/6f/Portrait_with_natural_light_%28Creative_Commons%29.jpg',
 'R02':'https://upload.wikimedia.org/wikipedia/commons/e/eb/Natural_Light_Portrait_of_Rosie_%2820710648621%29.jpg',
 'R04':'https://upload.wikimedia.org/wikipedia/commons/8/82/FrecklesCloseup.jpg',
}
def collect(item):
    rid, source, kind = item
    row = {'id':rid,'source_url':source,'access_date':'2026-10-12','kind':kind,'pixels_inspected':False}
    try:
        response = requests.get(source, headers=HEAD, timeout=45)
        response.raise_for_status()
        if kind == 'pdf':
            blob=response.content; suffix='.pdf'; asset=source
        else:
            page=response.text
            if kind == 'commons':
                match=re.search(r'class="fullImage".*?<a href="([^"]+)"',page,re.S)
            else:
                match=re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"',page)
            if not match and rid not in DIRECT: raise ValueError('No original/og:image found')
            asset=DIRECT.get(rid) or html.unescape(match.group(1))
            if asset.startswith('//'): asset='https:'+asset
            pic=requests.get(asset,headers=HEAD,timeout=45);pic.raise_for_status()
            blob=pic.content;suffix='.jpg'
        path=MEDIA/(rid+suffix)
        path.write_bytes(blob)
        row.update(asset_url=asset,path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(blob).hexdigest(),bytes=len(blob),status='FETCHED')
        if kind != 'pdf':
            im=Image.open(path);row['dimensions']=list(im.size)
            tags={ExifTags.TAGS.get(k,str(k)):str(v) for k,v in im.getexif().items()}
            try: tags.update({ExifTags.TAGS.get(k,str(k)):str(v) for k,v in im.getexif().get_ifd(34665).items()})
            except Exception: pass
            row['exif']={k:v for k,v in tags.items() if k in ['Make','Model','LensModel','FNumber','ExposureTime','ISOSpeedRatings','FocalLength','FocalLengthIn35mmFilm','DateTimeOriginal','Software','Flash','WhiteBalance']}
        else:
            doc=fitz.open(path);row['pages']=len(doc)
            pages = [0] if rid=='R05' else ([0,5,6,7,8] if rid=='R06' else [0])
            for p in pages:
                if p<len(doc): doc[p].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(MEDIA/f'{rid}_page_{p+1}.png')
            # Technical excerpts stay local; do not paste full papers into report.
            (MEDIA/f'{rid}_text.txt').write_text('\n'.join(p.get_text() for p in doc),encoding='utf-8')
    except Exception as exc: row.update(status='UNAVAILABLE',error=str(exc))
    return row
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool: rows=list(pool.map(collect,SOURCES))
    (ROOT/'reference_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    for row in rows: print(row['id'],row['status'],row.get('dimensions',row.get('pages')),row.get('exif',{}),row.get('error',''))

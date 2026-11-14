from pathlib import Path
import json,hashlib,requests,concurrent.futures
from PIL import Image,ExifTags
import fitz
ROOT=Path(__file__).resolve().parent
MEDIA=ROOT/'evidence'
rows=json.loads((ROOT/'reference_manifest.json').read_text(encoding='utf-8'))
def save_item(rid,url):
    row=next(r for r in rows if r['id']==rid)
    try:
        res=requests.get(url,timeout=30);res.raise_for_status()
        path=MEDIA/(rid+'.jpg');path.write_bytes(res.content)
        im=Image.open(path)
        tags=dict(im.getexif());tags.update(im.getexif().get_ifd(34665))
        row.update(status='FETCHED',path=path.relative_to(ROOT).as_posix(),asset_url=url,sha256=hashlib.sha256(res.content).hexdigest(),dimensions=list(im.size),bytes=len(res.content),exif={ExifTags.TAGS.get(k,str(k)):str(v) for k,v in tags.items() if ExifTags.TAGS.get(k,str(k)) in ['Make','Model','FNumber','ExposureTime','ISOSpeedRatings','FocalLength','DateTimeOriginal','Software','Flash','WhiteBalance']})
        row.pop('error',None)
    except Exception as e: row['error']=str(e)
    print(rid,row['status'])
save_item('R03','https://live.staticflickr.com/1295/1351739811_3f6903ecf1_o.jpg')
base=ROOT.parents[2]
lib=json.loads((base/'references/library.json').read_text(encoding='utf-8'))
for rid,libid in [('P03','P01_MIRROR'),('P04','P02_VANITY')]:
    record=next(x for x in lib['references'] if x['reference_id']==libid)
    path=base/record['local_path'];im=Image.open(path)
    rows.append(dict(id=rid,source_url=record['source_url'],asset_url=record['image_url'],access_date='2026-10-12',kind='pinterest_existing',status='FETCHED',path='../../../'+record['local_path'],sha256=hashlib.sha256(path.read_bytes()).hexdigest(),dimensions=list(im.size),pixels_inspected=False,authenticity=record['authenticity'],library_reference_id=libid))
doc=fitz.open(MEDIA/'R06.pdf')
for p in [9]:doc[p].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(MEDIA/f'R06_page_{p+1}.png')
(ROOT/'reference_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')

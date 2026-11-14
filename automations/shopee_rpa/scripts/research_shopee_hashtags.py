"""Read-only parsing of already visible hashtag suggestions. Does not type queries."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.mobile.read_only import read_only_session
from app.mobile.shopee_video import Screen

def parse_visible_suggestions(xml):
    screen=Screen(xml); screen.guard(); rows=[]
    for node in screen.root.iter('node'):
        if node.get('resource-id','').endswith('/ll_tag_item'):
            tags=[n.get('text') for n in node.iter('node') if n.get('resource-id','').endswith('/tv_hashtag')]
            metrics=[n.get('text') for n in node.iter('node') if n.get('resource-id','').endswith('/tv_hashtag_num')]
            if tags: rows.append(dict(tag=tags[0],metric=metrics[0] if metrics else None))
    return dict(rows=rows,metric_meaning='Observed platform label; views are not usage counts',read_only=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--xml',help='Offline captured XML, preferred')
    parser.add_argument('--config',help='Explicit read-only inspection config')
    args=parser.parse_args()
    if args.xml: report=parse_visible_suggestions(Path(args.xml).read_text(encoding='utf-8-sig'))
    elif args.config:
        config=json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
        with read_only_session(config) as ui: report=parse_visible_suggestions(ui.dump_hierarchy())
    else: parser.error('--xml or --config required; automatic query typing was removed')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__': main()

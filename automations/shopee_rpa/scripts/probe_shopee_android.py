"""Read-only Shopee inspection; legacy action flags are intentionally unsupported."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.mobile.read_only import read_only_session, capture_read_only

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True)
    parser.add_argument('--output',default='debug/shopee_android/read_only_probe.json')
    args=parser.parse_args()
    config=json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
    with read_only_session(config) as ui:
        report=capture_read_only(ui)
    target=Path(args.output); target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(read_only=True,report=str(target)),ensure_ascii=False))

if __name__=='__main__': main()

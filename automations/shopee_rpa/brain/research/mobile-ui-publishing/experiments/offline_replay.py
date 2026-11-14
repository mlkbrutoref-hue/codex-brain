"""Offline research replay. No device construction, network, ledger or publication."""
import json,hashlib,sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from importlib.metadata import version
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
import uiautomator2.core as core
from uiautomator2.exceptions import HTTPTimeoutError
from app.mobile.shopee_video import Screen,product_cards,product_sheet_matches
from app.mobile.safety_runtime import AndroidSafetyRuntime

def main():
 calls=[];restarts=[]
 def transport(dev,port,method,params,timeout,debug):
  calls.append(dict(method=method,simulated_effect_applied=True))
  if len(calls)==1:raise HTTPTimeoutError('Synthetic response lost after simulated effect')
  return True
 dummy=SimpleNamespace(_dev=None,_device_server_port=0,_debug=False,stop_uiautomator=lambda:restarts.append('stop'),start_uiautomator=lambda:restarts.append('start'))
 with patch.object(core,'_jsonrpc_call',side_effect=transport):
  result=core.BasicUiautomatorServer.jsonrpc_call(dummy,'click',[100,200],1)
 assert result is True and len(calls)==2 and restarts==['stop','start']
 p=ROOT/'output/preparation_abandonment_20261008';c=json.loads((p/'candidate-config-03.json').read_text(encoding='utf-8'))
 card=Screen((p/'product-current.xml').read_text(encoding='utf-8'));sheet=Screen((p/'add-result.xml').read_text(encoding='utf-8'))
 title=c['product_title'];matched=product_cards(card,c['product_query'],title)
 original_predicate=len(sheet.texts('Editar informações do produto'))==1 and len(sheet.texts(title))==1 and len(sheet.texts('Feito'))==1
 assert len(matched)==1 and not original_predicate and product_sheet_matches(sheet,title)
 a=[{'resource-id':'com.shopee.br:id/tv_product_title','package':'com.shopee.br','class':'android.widget.TextView','text':title,'bounds':'[0,0][50,50]'}];b=[dict(a[0],bounds='[0,80][50,130]')]
 assert AndroidSafetyRuntime._evidence_digest(a)!=AndroidSafetyRuntime._evidence_digest(b)
 assert AndroidSafetyRuntime._linked_product_digest(a)==AndroidSafetyRuntime._linked_product_digest(b)
 changed=[dict(b[0],text='Other product')]
 assert AndroidSafetyRuntime._linked_product_digest(a)!=AndroidSafetyRuntime._linked_product_digest(changed)
 report=dict(mode='OFFLINE_NO_DEVICE_NO_NETWORK',uiautomator2=version('uiautomator2'),core_path=str(Path(core.__file__).resolve()),core_sha256=hashlib.sha256(Path(core.__file__).read_bytes()).hexdigest(),
  experiments=[dict(id='E01',hypothesis='Installed client retries a mutating RPC after response timeout',status='PASS_REPRODUCED',outer_calls=1,simulated_transport_calls=len(calls),simulated_effects=len(calls),restart_operations=restarts,limitation='Synthetic response loss; does not establish real duplicate publication or latency'),
  dict(id='E02',hypothesis='Actual native product sheet contains duplicate title and defeats old predicate',status='PASS_REPRODUCED',exact_title_occurrences=len(sheet.texts(title)),old_predicate=original_predicate,current_predicate=product_sheet_matches(sheet,title),exact_card_count=len(matched),source_xml_sha256=hashlib.sha256((p/'add-result.xml').read_bytes()).hexdigest()),
  dict(id='E03',hypothesis='Geometry-only reflow changes raw hash but not semantic hash',status='PASS_REPRODUCED',real_incident_root_cause='INFERRED_NOT_PROVEN',changed_title_rejected=True)])
 target=Path(__file__).with_name('offline-replay-results.json');target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()

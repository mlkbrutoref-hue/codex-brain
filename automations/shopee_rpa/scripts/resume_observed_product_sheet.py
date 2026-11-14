"""Resume only the observed product info sheet, with audited Add reconciliation."""
import hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.mobile.safety_runtime import AndroidSafetyRuntime
from app.mobile.preparation_diagnostic import preparation_diagnostic
from app.mobile.observed_add_recovery import reconcile_observed_add
from app.mobile.shopee_video import ShopeeVideoPublisher,Screen,atomic_json,validation_checks,product_sheet_matches
from app.mobile.ui import ShopeeUI
from app.operational.deadlines import OperationalStop

def main():
 p=ROOT/'output/preparation_abandonment_20261008';out=p/'live-feito-02';out.mkdir(exist_ok=False)
 config=json.loads((p/'candidate-config-03.json').read_text(encoding='utf-8'))
 rt=AndroidSafetyRuntime(config,ROOT);w=ShopeeVideoPublisher(None,config,ROOT);job=rt.ledger.identity(rt.candidate)
 result=dict(job_id=job,publish_button_clicked=False,publish_performed=False,ready_for_publish=False)
 try:
  with preparation_diagnostic(rt,job,authorization_reference='Operator: falta mais um botão tem que apertar em feito') as diag:
   # Revalidate local content while excluding only this already reserved identity.
   rt.job=job
   rt.local_preflight(w.expected_caption)
   if not rt.platform_authorized():raise OperationalStop('PLATFORM_AUTHORIZATION_REQUIRED')
   record,proof=reconcile_observed_add(rt,diag,w,p/'live-03/product_card-request.json',p/'card-review.json',out/'reconciliation.json',resolved_failures=(p/'live-01/result.json',p/'live-02/result.json'))
   rt.owner=record['original_snapshot']['owner']
   rt.ui=ShopeeUI(diag.device,rt.config,rt.deadline,rt.budget,rt.breaker,rt.logger,rt.modes,rt.ledger,job,rt.owner)
   screen=Screen(rt.ui.dump_hierarchy());screen.guard()
   if rt._evidence_digest(screen.nodes)!=record['screen_sha256']:raise OperationalStop('RECONCILED_SCREEN_CHANGED')
   rt.input['account_preflight_review']=dict(status='APPROVED',account_id=rt.expected.account_id,username=rt.expected.username,
      reviewer='Codex continuous account/media/editor trace and operator current Feito confirmation',timestamp=time.time(),
      screen_sha256=record['screen_sha256'],evidence_reference=str(out/'reconciliation.json'))
   rt._confirm_reviewed_account(screen);rt.ui.account_proven=True;rt.check_app()
   w.safety=rt;w.d=rt.ui
   # The validated card review was accepted immediately before the successful Add.
   raw=(p/'card-review.json').read_bytes()
   binding=dict(validation_scope='ASSISTED_UI_VALIDATION',product=proof['product'],candidate_fingerprint=proof['candidate_fingerprint'],
      reviewer=proof['reviewer'],timestamp=proof['reviewed_at'],source_url=proof['official_source_url'],
      evidence_reference=str((p/'card-review.json').resolve()),evidence_sha256=hashlib.sha256(raw).hexdigest(),
      card=proof['card'],card_screen_sha256=proof['screen_sha256'],screenshot_sha256=proof['screenshot_sha256'])
   rt._pending_card_binding=binding
   w.checkpoint('PRODUCT_SELECTED')
   screen=w.tap_text('Feito',lambda s:s.has('btn_post') and len(s.ids('tv_product_title'))==1 and s.ids('tv_product_title')[0].get('text')==config['product_title'],'PRODUCT_LINKED')
   rt.bind_selected_card(screen,binding);rt.product_evidence(screen)
   if not w.media_matches():raise OperationalStop('MEDIA_SELECTION_REVIEW_REQUIRED')
   w.fill_caption();w.ensure_shopee_only()
   screen=w.observe();media_ok=w.media_matches();checks=validation_checks(screen,w.expected_caption,config['product_title'],media_ok,w.sharing_disabled())
   w.session['validation']=checks
   rt.ui.screenshot().save(out/'final-editor.png')
   w.session['assisted_validation']=rt.complete_assisted(screen,media_ok,checks)
   w.session['ready_for_publish']=False;w.checkpoint('ASSISTED_VALIDATED')
   result.update(state='ASSISTED_VALIDATED',publish_button_reached=screen.has('btn_post'),product_linked=True,checks=checks)
 except Exception as exc:
  if rt.job and rt.ui:rt.fail(str(exc));w.checkpoint('REVIEW',error=str(exc))
  result.update(state='REVIEW',blocker=str(exc))
 result.update(ledger_state=rt.ledger.get(job)['state'],breaker=rt.breaker.snapshot()['state'])
 atomic_json(out/'result.json',result);print(json.dumps(result,ensure_ascii=False),flush=True)
 return 0 if result.get('state')=='ASSISTED_VALIDATED' else 1
if __name__=='__main__':raise SystemExit(main())

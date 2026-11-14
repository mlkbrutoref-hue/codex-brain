"""Recover one explicitly abandoned preparation and run the existing assisted worker.

Review checkpoints write a request and wait for a hash-bound review artifact;
the Android connection and leases stay held. There is no publish option.
"""
import argparse
from contextlib import contextmanager
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.mobile.preparation_diagnostic import preparation_diagnostic
from app.mobile.safety_runtime import AndroidSafetyRuntime
from app.mobile.shopee_video import ShopeeVideoPublisher, Screen, RpaError, atomic_json, validation_checks, device_lock
from app.operational.config import FeatureMode
from app.operational.deadlines import OperationalStop
from app.publishing.preparation_abandonment import abandon_preparation


class ReviewedRuntime(AndroidSafetyRuntime):
    def product_card_evidence(self,screen,card):
        if not Path(self.input['product_card_review']).exists():
            self.review('product_card',screen,dict(card=asdict(card),
                button_node_sha256=self._evidence_digest(screen.root.findall('.'+card.button_xpath[len('/hierarchy'):])[0].attrib),
                product=asdict(self.candidate.product),official_source_url=f'https://shopee.com.br/product/{self.candidate.product.shop_id}/{self.candidate.product.item_id}'))
        return super().product_card_evidence(screen,card)


def run(args):
    out=Path(args.output).resolve()
    if out.exists(): raise OperationalStop('ASSISTED_OUTPUT_ALREADY_EXISTS')
    out.mkdir(parents=True)
    config=json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
    runtime=ReviewedRuntime(config,ROOT)
    if runtime.config.mode!=FeatureMode.ASSISTED_MODE or config.get('publish_authorized'):
        raise OperationalStop('ASSISTED_ONLY_NO_PUBLICATION')
    job=runtime.ledger.identity(runtime.candidate)
    worker=ShopeeVideoPublisher(None,config,ROOT)
    if worker.session_path.exists(): raise OperationalStop('RECOVERY_SESSION_ALREADY_EXISTS')
    result=dict(job_id=job,publish_button_clicked=False,publish_performed=False,ready_for_publish=False)

    def review(stage,screen,extra=None):
        request=out/(stage+'-request.json'); response=out/(stage+'-review.json')
        if request.exists() or response.exists(): raise OperationalStop('REVIEW_CHECKPOINT_ALREADY_USED')
        fresh=worker.observe()
        if runtime._evidence_digest(fresh.nodes)!=runtime._evidence_digest(screen.nodes):
            raise OperationalStop('REVIEW_SCREEN_CHANGED')
        screenshot=out/(stage+'.png'); worker.d.screenshot().save(screenshot)
        proof=dict(stage=stage,job_id=job,candidate_fingerprint=runtime.candidate.fingerprint(),
            screen_sha256=runtime._evidence_digest(screen.nodes),screenshot_reference=str(screenshot),
            screenshot_sha256=hashlib.sha256(screenshot.read_bytes()).hexdigest(),
            selection=worker.session.get('selection_evidence'),preview_nodes=screen.ids('iv_video_preview'),
            response_path=str(response),**(extra or {}))
        atomic_json(request,proof)
        print(json.dumps(dict(state='AWAITING_REVIEW',request=str(request))),flush=True)
        while not response.exists(): runtime.deadline.wait(.25)
        payload=json.loads(response.read_text(encoding='utf-8'))
        if payload.get('status') not in ('APPROVED','APPROVED_UI_ONLY'):
            raise OperationalStop('REVIEW_NOT_APPROVED')
        if stage=='product_card':
            target=Path(config['product_card_review'])
            if target.exists(): raise OperationalStop('CARD_REVIEW_ALREADY_EXISTS')
            atomic_json(target,payload)
        return response

    runtime.review=review
    @contextmanager
    def connection():
        row=runtime.ledger.get(job)
        if row['state']=='UNKNOWN':
            with preparation_diagnostic(runtime,job,authorization_reference=args.evidence) as diagnostic:
                result['recovery']=abandon_preparation(runtime,diagnostic,args.evidence)
                atomic_json(out/'recovery-result.json',result['recovery'])
                yield diagnostic.device
        elif row['state'] in ('PREPARATION_ABANDONED','FAILED') and row.get('preparation_history'):
            runtime.breaker.check()
            with device_lock(config['serial'],ROOT/'logs/shopee_android/locks'):
                try: yield None
                finally: runtime.close()
        else: raise OperationalStop('NO_ELIGIBLE_ABANDONED_PREPARATION')
    try:
        with connection() as device:
            # Reuse this bounded device and the outer exclusive device lock.
            runtime.start(worker.expected_caption,Screen,device=device)
            worker.safety=runtime; worker.d=runtime.ui
            worker.session['central_job_id']=job
            worker.checkpoint('DEVICE_READY')
            if getattr(args,'resume_evidence',None):
                proof=Path(args.resume_evidence)
                worker.adopt_selection(proof)
                screen=worker.observe()
                if worker.liked_tab_active(screen) and screen.texts('Adicionar Produto'):
                    worker.d.press('back')
                    worker.wait(lambda s: s.has('btn_post') and s.has('iv_video_preview'))
            else:
                try:
                    worker.select_media()
                except RpaError as exc:
                    if str(exc)!='MEDIA_SELECTION_REVIEW_REQUIRED': raise
                proof=review('media_selection',worker.observe())
            worker.adopt_selection(proof)
            try:
                worker.continue_selected_media()
            except RpaError as exc:
                if str(exc)!='MEDIA_SELECTION_REVIEW_REQUIRED' or not worker.observe().has('iv_video_preview'): raise
                proof=review('editor_media',worker.observe())
                worker.adopt_selection(proof)
                worker.continue_selected_media()
            worker.select_product()
            worker.fill_caption()
            worker.ensure_shopee_only()
            screen=worker.observe(); media_ok=worker.media_matches()
            checks=validation_checks(screen,worker.expected_caption,config['product_title'],media_ok,worker.sharing_disabled())
            worker.session['validation']=checks
            worker.session['assisted_validation']=runtime.complete_assisted(screen,media_ok,checks)
            worker.session['ready_for_publish']=False
            worker.checkpoint('ASSISTED_VALIDATED')
            result.update(state='ASSISTED_VALIDATED',publish_button_reached=screen.has('btn_post'),product_linked=True)
    except Exception as exc:
        reason=str(exc) if isinstance(exc,(OperationalStop,RpaError)) else type(exc).__name__
        if runtime.job is not None:
            runtime.fail(reason)
            worker.checkpoint('REVIEW',error=reason)
        result.update(state='REVIEW',blocker=reason)
    result['ledger_state']=runtime.ledger.get(job)['state']
    result['breaker']=runtime.breaker.snapshot()['state']
    atomic_json(out/'result.json',result)
    print(json.dumps(result,ensure_ascii=False),flush=True)
    return 0 if result.get('state')=='ASSISTED_VALIDATED' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('config','evidence','output'): parser.add_argument('--'+name,required=True)
    parser.add_argument('--resume-evidence',help='Existing current selection proof; never reselect media')
    raise SystemExit(run(parser.parse_args()))

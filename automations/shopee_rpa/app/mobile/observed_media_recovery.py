"""Confirm the editor effect of a reviewed Next action without repeating it."""
import json,time,hashlib,re
from datetime import datetime
from pathlib import Path
from app.mobile.shopee_video import Screen,video_profile_account_matches
from app.mobile.media_selection import selection_unambiguous
from app.mobile.ui import IsolatedAndroidDevice,ShopeeUI
from app.media.identity import file_sha256
from app.operational.config import ActionType
from app.operational.deadlines import OperationalStop

def recover_observed_media_editor(runtime,worker,device,*,reviewed_screenshot,reviewer,evidence_path):
 if not isinstance(device,IsolatedAndroidDevice) or device.serial!=runtime.input['serial'] or device.deadline is not runtime.deadline:
  raise OperationalStop('BOUNDED_RECOVERY_DEVICE_REQUIRED')
 if not reviewer or not runtime.validator.operator_listing_approval(runtime.candidate):
  raise OperationalStop('OPERATOR_RECOVERY_REVIEW_REQUIRED')
 job=runtime.ledger.identity(runtime.candidate);selection=worker.session.get('selection_evidence',{})
 profile_path=Path(reviewed_screenshot).parent/'01-start.xml'
 if not profile_path.exists():profile_path=Path(reviewed_screenshot).parent/'candidate-01/01-start.xml'
 if (not video_profile_account_matches(Screen(profile_path.read_text(encoding='utf-8')),runtime.candidate.account_id)
     or not 0<=time.time()-profile_path.stat().st_mtime<=runtime.config.approval_ttl
     or selection.get('expected_account')!=runtime.candidate.account_id):
  raise OperationalStop('RECOVERY_ACCOUNT_CONTINUITY_NOT_PROVEN')
 if (worker.session.get('publish_attempted') or worker.session.get('central_job_id')!=job
     or worker.session.get('state') not in ('MEDIA_PREVIEW','EDITOR_READY','EDITOR_MEDIA_REVIEW') or not selection.get('visual_preview_reviewed')
     or selection.get('candidate_fingerprint')!=runtime.candidate.fingerprint()
     or not selection_unambiguous(selection,runtime.input['video_path'],runtime.input['video_sha256'])
     or any(file_sha256(ref['path'])!=ref['sha256'] for ref in selection['files'])):
  raise OperationalStop('MEDIA_RECOVERY_SELECTION_TRACE_INVALID')
 log=[json.loads(line) for line in (runtime.root/'logs/operational'/f'{runtime.input["job_id"]}.jsonl').read_text(encoding='utf-8').splitlines()]
 if any(e.get('action_type')=='PUBLISH_ATTEMPT' for e in log):raise OperationalStop('PUBLICATION_MUST_BE_RECONCILED')
 mutations=[e for e in log if e.get('event')=='action' and e.get('action_type')!='READ_STATE']
 if not mutations or mutations[-1].get('action_type')!='CLICK' or mutations[-1].get('status')!='SUCCESS':
  raise OperationalStop('NEXT_EFFECT_TRACE_INVALID')
 def assess(db):
  row=runtime.ledger.get(job,db)
  if (not row or row['state'] not in ('UNKNOWN','FAILED') or row['attempted'] or row['fingerprint']!=runtime.candidate.fingerprint()
      or json.loads(row['evidence'] or '{}').get('reason')!='SUPERVISED_FLOW_INCOMPLETE'
      or db.execute('SELECT 1 FROM authorizations WHERE job=?',(job,)).fetchone()
      or db.execute("SELECT 1 FROM jobs WHERE account=? AND id<>? AND state IN ('UNKNOWN','PUBLISHING','UPLOADING','PREPARING','READY','RESERVED')",(row['account'],job)).fetchone()
      or runtime.store.killed(db)):
   raise OperationalStop('MEDIA_RECOVERY_SCOPE_INVALID')
  boundary=db.execute("SELECT COALESCE(MAX(id),0) FROM breaker_events WHERE account=? AND kind='RELEASE' AND reason='CLOSED'",(row['account'],)).fetchone()[0]
  events=[dict(e) for e in db.execute("SELECT * FROM breaker_events WHERE account=? AND id>? AND kind='FAILURE'",(row['account'],boundary))]
  resolved=set()
  for recorded in db.execute("SELECT value FROM kv WHERE key LIKE 'confirmed_media_editor_recovery:%'"):
   prior=json.loads(recorded['value']);old=prior.get('original_snapshot',{})
   published=db.execute("SELECT * FROM jobs WHERE id=? AND account=? AND state='PUBLISHED'",(old.get('id'),row['account'])).fetchone()
   if not published or published['fingerprint']!=prior.get('candidate_fingerprint') or prior.get('effect')!='CONFIRMED_NATIVE_EDITOR_FROM_REVIEWED_MEDIA':continue
   confirmed=json.loads(published['evidence'] or '{}')
   if (confirmed.get('candidate_fingerprint')==published['fingerprint'] and confirmed.get('account_id')==row['account']
       and (confirmed.get('post_id') or confirmed.get('post_url')) and all(confirmed.get(k)=='PASS' for k in ('media_match','caption_match','product_match'))):
    resolved.update(prior.get('incident_ids',[]))
  events=[e for e in events if e['id'] not in resolved]
  if not events or any(e['reason'] not in ('PUBLICATION_UNKNOWN','SUPERVISED_FLOW_INCOMPLETE') or e['job'] not in (None,job) for e in events):
   raise OperationalStop('UNRELATED_BREAKER_INCIDENT')
  for event in events:
   if event['job'] is None and not any(e.get('event')=='error' and e.get('error_code')==event['reason']
       and abs(datetime.fromisoformat(e['timestamp']).timestamp()-event['timestamp'])<2 for e in log):
    raise OperationalStop('UNSCOPED_BREAKER_INCIDENT_NOT_CORROBORATED')
  for key in ('account:'+row['account'],'device:'+runtime.input['serial']):
   lease=db.execute('SELECT owner FROM leases WHERE key=?',(key,)).fetchone()
   if row['state']=='FAILED':
    if lease:raise OperationalStop('RECOVERY_LEASE_MISMATCH')
   elif not lease or lease['owner']!=row['owner']:raise OperationalStop('RECOVERY_LEASE_MISMATCH')
  return row,events
 with runtime.store.transaction() as db:original=assess(db)
 breaker_before=runtime.breaker.snapshot()['state']
 if breaker_before not in ('OPEN','CLOSED'):raise OperationalStop('MEDIA_RECOVERY_REQUIRES_REVIEWED_BREAKER_STATE')
 if original[0]['state']=='UNKNOWN' and breaker_before!='OPEN':raise OperationalStop('MEDIA_RECOVERY_REQUIRES_OPEN')
 # These incident-scoped reads cannot dispatch navigation, selection or publication.
 def read(op,args):
  runtime.deadline.raise_if_expired()
  with runtime.store.transaction() as db:
   if assess(db)!=original:raise OperationalStop('INCIDENT_CHANGED')
   runtime.account_budget.charge(db,ActionType.READ_STATE)
  return device.invoke(op,args)
 def observe():
  if read('app_current',[])['package']!='com.shopee.br' or read('app_info',['com.shopee.br'])['versionName'] not in runtime.config.allowed_app_versions:
   raise OperationalStop('RECOVERY_APP_CHANGED')
  screen=Screen(read('dump_hierarchy',[]));screen.guard()
  if not screen.has('btn_post') or not screen.has('et_caption') or len(screen.ids('iv_video_preview'))!=1 or screen.ids('tv_product_title'):
   raise OperationalStop('EXPECTED_UNBOUND_EDITOR_NOT_OBSERVED')
  remote=read('shell',[['sha256sum',runtime.input['video_path']]])
  if remote.exit_code or remote.output.split()[0]!=runtime.input['video_sha256'] or file_sha256(runtime.input['local_media_path'])!=runtime.input['video_sha256']:
   raise OperationalStop('MEDIA_HASH_MISMATCH')
  image=read('screenshot',[]);bounds=tuple(map(int,re.findall(r'\d+',screen.ids('iv_video_preview')[0]['bounds'])))
  from PIL import Image
  with Image.open(reviewed_screenshot) as reviewed:
   if image.convert('RGB').crop(bounds).tobytes()!=reviewed.convert('RGB').crop(bounds).tobytes():raise OperationalStop('REVIEWED_EDITOR_THUMBNAIL_CHANGED')
  return screen,image,bounds
 observe()
 runtime.breaker.release(reviewer=reviewer,reason='Observed native Next editor effect; final dispatch absent in ledger and log',evidence=str(evidence_path))
 screen,image,bounds=observe()
 proof=dict(original_snapshot=original[0],incident_ids=[e['id'] for e in original[1]],reviewer=reviewer,reviewed_at=time.time(),
  candidate_fingerprint=runtime.candidate.fingerprint(),effect='CONFIRMED_NATIVE_EDITOR_FROM_REVIEWED_MEDIA',native_upload_status='UNKNOWN',
  publication_dispatch='NOT_DISPATCHED_BY_AUTOMATION',reviewed_screenshot=str(reviewed_screenshot),reviewed_screenshot_sha256=file_sha256(reviewed_screenshot),
  selection_evidence=selection,account_profile_reference=str(profile_path),account_profile_sha256=file_sha256(profile_path),
  screen_sha256=runtime._evidence_digest(screen.nodes),last_action=mutations[-1])
 path=Path(evidence_path)
 with path.open('x',encoding='utf-8') as f:json.dump(proof,f,ensure_ascii=False,indent=2)
 with runtime.store.transaction() as db:
  if assess(db)!=original or runtime.breaker.snapshot(db)['state']!='HALF_OPEN':raise OperationalStop('INCIDENT_CHANGED')
  runtime.store.put(db,'confirmed_media_editor_recovery:'+job+':'+str(original[1][-1]['id']),proof)
  if original[0]['state']=='FAILED':
   for key in ('account:'+runtime.candidate.account_id,'device:'+runtime.input['serial']):db.execute('INSERT INTO leases VALUES (?,?)',(key,original[0]['owner']))
  db.execute("UPDATE jobs SET state='PREPARING',evidence=? WHERE id=?",(json.dumps(proof),job));runtime.ledger.record(db,job,'PREPARING',original[0]['owner'])
  runtime.breaker.release(reviewer=reviewer,reason='Reviewed native media editor confirmed; retain upload UNKNOWN and resume same job without reselection',evidence=str(path),close=True,db=db)
 runtime.job=job;runtime.owner=original[0]['owner'];runtime.ui=ShopeeUI(device,runtime.config,runtime.deadline,runtime.budget,runtime.breaker,runtime.logger,runtime.modes,runtime.ledger,job,runtime.owner)
 runtime.ui.account_proven=True
 selection['preview_pixel_sha256']=hashlib.sha256(image.convert('RGB').crop(bounds).tobytes()).hexdigest()
 worker.safety=runtime;worker.d=runtime.ui;worker.session['selection_evidence']=selection;worker.checkpoint('EDITOR_READY')
 return proof

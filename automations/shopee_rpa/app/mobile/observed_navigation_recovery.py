"""Resume navigation-only preparation; never assert absence of native uploads."""
import json,time
from datetime import datetime
from pathlib import Path
from app.mobile.shopee_video import Screen,video_profile_account_matches
from app.mobile.ui import IsolatedAndroidDevice,ShopeeUI
from app.media.identity import file_sha256
from app.operational.config import ActionType
from app.operational.deadlines import OperationalStop

def validate_navigation_trace(session,log,job):
 mutations=[e for e in log if e.get('event')=='action' and e.get('action_type')!='READ_STATE']
 if (session.get('central_job_id')!=job or session.get('state')!='SHOPEE_PROFILE'
     or session.get('publish_attempted') or session.get('selection_evidence') or session.get('media')
     or len(mutations)!=1 or mutations[0].get('action_type')!='CLICK' or mutations[0].get('status')!='SUCCESS'
     or any(e.get('action_type') in ('PUBLISH_ATTEMPT','MEDIA_SELECT','UPLOAD_START') for e in log)):
  raise OperationalStop('NAVIGATION_ONLY_TRACE_REQUIRED')
 return mutations[0]

def recovery_incidents(db,account,job,log,root):
 boundary=db.execute("SELECT COALESCE(MAX(id),0) FROM breaker_events WHERE account=? AND kind='RELEASE' AND reason='CLOSED'",(account,)).fetchone()[0]
 events=[dict(r) for r in db.execute("SELECT * FROM breaker_events WHERE account=? AND id>? AND kind='FAILURE'",(account,boundary))]
 own=[];previous=[]
 for event in events:
  matched=any(e.get('event')=='error' and e.get('error_code')==event['reason'] and abs(datetime.fromisoformat(e['timestamp']).timestamp()-event['timestamp'])<2 for e in log)
  if event['reason']=='PUBLICATION_UNKNOWN' and event['job']==job or event['reason']=='SUPERVISED_FLOW_INCOMPLETE' and event['job'] is None and matched:
   own.append(event);continue
  # A historical unscoped failure requires a completed publication plus its
  # own timestamp-correlated error log. Security incidents are never waived.
  if event['reason']!='SUPERVISED_FLOW_INCOMPLETE' or event['job'] is not None:
   raise OperationalStop('UNRELATED_BREAKER_INCIDENT')
  proofs=[]
  for row in db.execute("SELECT * FROM jobs WHERE account=? AND state='PUBLISHED'",(account,)):
   evidence=json.loads(row['evidence'] or '{}')
   if not (evidence.get('candidate_fingerprint')==row['fingerprint'] and evidence.get('account_id')==account and evidence.get('post_id') and evidence.get('post_url') and all(evidence.get(k)=='PASS' for k in ('media_match','caption_match','product_match'))):continue
   reference=Path(evidence.get('evidence_reference',''))
   if not reference.is_file():continue
   for path in (Path(root)/'debug/shopee_android').glob('*/session.json'):
    session=json.loads(path.read_text(encoding='utf-8'))
    if session.get('central_job_id')!=row['id']:continue
    log_path=Path(root)/'logs/operational'/(session['job_id']+'.jsonl')
    if not log_path.is_file():continue
    older=[json.loads(line) for line in log_path.read_text(encoding='utf-8').splitlines()]
    if any(e.get('event')=='error' and e.get('error_code')==event['reason'] and abs(datetime.fromisoformat(e['timestamp']).timestamp()-event['timestamp'])<2 for e in older):
     proofs.append(dict(event_id=event['id'],job=row['id'],evidence_reference=str(reference),evidence_sha256=file_sha256(reference),log_reference=str(log_path),log_sha256=file_sha256(log_path),post_id=evidence['post_id']))
  if len(proofs)!=1:raise OperationalStop('UNSCOPED_BREAKER_INCIDENT_NOT_CORROBORATED')
  previous.extend(proofs)
 if not own:raise OperationalStop('NAVIGATION_INCIDENT_REQUIRED')
 return own,previous

def recover_observed_navigation(runtime,worker,device,*,reviewer,evidence_path):
 if not isinstance(device,IsolatedAndroidDevice) or device.serial!=runtime.input['serial'] or device.deadline is not runtime.deadline:
  raise OperationalStop('BOUNDED_RECOVERY_DEVICE_REQUIRED')
 if not reviewer or not runtime.validator.operator_listing_approval(runtime.candidate):raise OperationalStop('OPERATOR_RECOVERY_REVIEW_REQUIRED')
 job=runtime.ledger.identity(runtime.candidate)
 log_path=runtime.root/'logs/operational'/(runtime.input['job_id']+'.jsonl')
 log=[json.loads(line) for line in log_path.read_text(encoding='utf-8').splitlines()]
 mutation=validate_navigation_trace(worker.session,log,job)
 def assess(db):
  row=runtime.ledger.get(job,db)
  if (not row or row['state']!='UNKNOWN' or row['attempted'] or row['fingerprint']!=runtime.candidate.fingerprint()
      or json.loads(row['evidence'] or '{}').get('reason')!='SUPERVISED_FLOW_INCOMPLETE'
      or db.execute('SELECT 1 FROM authorizations WHERE job=?',(job,)).fetchone()
      or db.execute("SELECT 1 FROM jobs WHERE account=? AND id<>? AND state IN ('UNKNOWN','PUBLISHING','UPLOADING','PREPARING','READY','RESERVED')",(row['account'],job)).fetchone()
      or runtime.store.killed(db)):raise OperationalStop('NAVIGATION_RECOVERY_SCOPE_INVALID')
  for key in ('account:'+row['account'],'device:'+runtime.input['serial']):
   lease=db.execute('SELECT owner FROM leases WHERE key=?',(key,)).fetchone()
   if not lease or lease['owner']!=row['owner']:raise OperationalStop('RECOVERY_LEASE_MISMATCH')
  own,previous=recovery_incidents(db,row['account'],job,log,runtime.root)
  return row,own,previous
 with runtime.store.transaction() as db:original=assess(db);before=runtime.breaker.snapshot(db)
 if before['state']!='OPEN':raise OperationalStop('NAVIGATION_RECOVERY_REQUIRES_OPEN')
 def read(op,args):
  runtime.deadline.raise_if_expired()
  with runtime.store.transaction() as db:
   if assess(db)!=original:raise OperationalStop('INCIDENT_CHANGED')
   runtime.account_budget.charge(db,ActionType.READ_STATE)
  return device.invoke(op,args)
 def observe():
  if read('app_current',[])['package']!='com.shopee.br' or read('app_info',['com.shopee.br'])['versionName'] not in runtime.config.allowed_app_versions:raise OperationalStop('RECOVERY_APP_CHANGED')
  screen=Screen(read('dump_hierarchy',[]));screen.guard()
  if (not video_profile_account_matches(screen,runtime.candidate.account_id) or screen.has('rv_gallery') or screen.has('btn_post') or screen.has('et_caption')
      or sum(n.get('content-desc')=='click to post video' for n in screen.nodes)!=1):raise OperationalStop('EXACT_PROFILE_NO_SELECTION_REQUIRED')
  remote=read('shell',[['sha256sum',runtime.input['video_path']]])
  if remote.exit_code or remote.output.split()[0]!=runtime.input['video_sha256'] or file_sha256(runtime.input['local_media_path'])!=runtime.input['video_sha256']:raise OperationalStop('MEDIA_HASH_MISMATCH')
  return screen
 observe();runtime.breaker.release(reviewer=reviewer,reason='Review navigation-only incomplete preparation; no media/final action dispatched',evidence=str(evidence_path))
 screen=observe();proof=dict(original_snapshot=original[0],breaker_before=before,incident_ids=[e['id'] for e in original[1]],previous_completed_incidents=original[2],
  candidate_fingerprint=runtime.candidate.fingerprint(),effect='CURRENT_EXACT_PROFILE_AFTER_NAVIGATION_ONLY',media_selection_by_automation='NOT_DISPATCHED',publication_dispatch='NOT_DISPATCHED_BY_AUTOMATION',native_upload_status='UNKNOWN',
  reviewer=reviewer,reviewed_at=time.time(),screen_sha256=runtime._evidence_digest(screen.nodes),last_action=mutation,log_reference=str(log_path),log_sha256=file_sha256(log_path))
 path=Path(evidence_path)
 with path.open('x',encoding='utf-8') as stream:json.dump(proof,stream,ensure_ascii=False,indent=2)
 with runtime.store.transaction() as db:
  if assess(db)!=original or runtime.breaker.snapshot(db)['state']!='HALF_OPEN':raise OperationalStop('INCIDENT_CHANGED')
  runtime.store.put(db,'confirmed_navigation_recovery:'+job+':'+str(original[1][-1]['id']),proof)
  db.execute("UPDATE jobs SET state='PREPARING',evidence=? WHERE id=?",(json.dumps(proof),job));runtime.ledger.record(db,job,'PREPARING',original[0]['owner'])
  runtime.breaker.release(reviewer=reviewer,reason='Navigation-only incident reviewed with read-only profile preflight; same job retained',evidence=str(path),close=True,db=db)
 runtime.job=job;runtime.owner=original[0]['owner'];runtime.ui=ShopeeUI(device,runtime.config,runtime.deadline,runtime.budget,runtime.breaker,runtime.logger,runtime.modes,runtime.ledger,job,runtime.owner)
 runtime.ui.account_proven=True;worker.safety=runtime;worker.d=runtime.ui;worker.checkpoint('SHOPEE_PROFILE')
 return proof

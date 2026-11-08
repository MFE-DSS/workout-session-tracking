"""Hermetic science execution, attestation bytes are never runtime inputs."""

from pathlib import Path

import pytest


def test_bundle_runs_actual_authorities_outside_checkout_and_rejects_tamper(tmp_path):
    from app.services.plan_v3.packaging import execute_science
    from scripts.build_plan_v3_runtime_bundle import build_bundle

    target = tmp_path / "private-science"
    manifest = build_bundle(target)
    result = execute_science("authorities", {}, root=target, expected_digest=manifest)
    assert (
        result["v3"]["binding_digest"]
        == "9ef301da08ec3614c7e2a4fbbb95a2384f1c870bca84b6b69eeb4e20a1897389"
    )
    assert (
        result["encounter"]["bundle_digest"]
        == "e840d5edfc2bbe150f077062227a503a6f3a996fb92a3f7e7cbe49972dee72f9"
    )
    assert all(Path(p).is_relative_to(target) for p in result["module_paths"])
    assert not any("artifacts" in p or "fixtures" in p for p in result["module_paths"])
    assert result["runtime_payload_source"] == "REQUEST_ONLY"
    material = result["encounter"]["protocol_material"]
    assert material["text"] == (target / material["source_ref"]).read_text()
    assert (
        material["sha256"]
        == __import__("hashlib").sha256((target / material["source_ref"]).read_bytes()).hexdigest()
    )
    module = target / "tools/science_initial_policy/v3_producer.py"
    module.write_text(module.read_text() + "\n# tampered\n")
    with pytest.raises(ValueError, match="science_bundle_unavailable"):
        execute_science("authorities", {}, root=target, expected_digest=manifest)


def test_hermetic_api_consumes_real_positive_producer_and_logs_owned_session(tmp_path):
    """No checkout import or synthetic READY factory in the deployed app process."""
    import os
    import shutil
    import subprocess
    import sys

    from scripts.build_plan_v3_runtime_bundle import build_bundle

    checkout = Path(__file__).resolve().parents[1]
    deployed = tmp_path / "deployment"
    deployed.mkdir()
    shutil.copytree(
        checkout / "app", deployed / "app", ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )
    shutil.copytree(checkout / "data", deployed / "data")
    bundle = tmp_path / "private-science"
    package_digest = build_bundle(bundle)
    script = r"""
import sys,json
from pathlib import Path
from datetime import UTC,datetime
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root))
from app.main import app
from app.database import Base,engine,SessionLocal
from app.models.user import User
from app.models.first_plan_runtime import FirstPlanRuntimeAuthority
from app.services.auth import hash_password
from app.services.plan_v3.packaging import execute_science
from app.services.plan_v3.snapshots import canonical
from fastapi.testclient import TestClient
Base.metadata.create_all(engine)
a=execute_science('authorities',{})
pins={k:a['v3'][k] for k in ('registry_digest','binding_digest','bundle_digest','effective_science_digest')}
with SessionLocal() as db:
    db.add(User(username='synthetic-hermetic',password_hash=hash_password('test-only-1234')))
    db.add(FirstPlanRuntimeAuthority(profile_key='first-session-runtime/3.0.0',generation=1,state='ACTIVE',publication_json=canonical(pins),packaging_digest=sys.argv[2],approval_ref='GO_BUILD:DISPOSABLE_SYNTHETIC_HTTP_TEST'));db.commit()
with TestClient(app) as client:
    token=client.post('/api/mobile/v1/auth/login',json={'username':'synthetic-hermetic','password':'test-only-1234'}).json()['access_token']
    h={'Authorization':'Bearer '+token,'X-Auren-Contract':'first-session-runtime/3.0.0'};prefix='/api/mobile/v3';revision=0
    def call(method,path,body=None,extra=None):
        response=client.request(method,prefix+path,headers={**h,**(extra or {})},json=body)
        assert response.status_code==200,(path,response.status_code,response.text)
        return response.json()
    fields={k:{'state':'KNOWN','value':v} for k,v in {'objective':'HYPERTROPHY','population_scope':'ADULT_NON_CLINICAL','sessions_per_week':2,'session_budgets_minutes':[60,60],'limitations':[]}.items()}
    revision=call('PUT','/me/blueprint/declarations',{'request_id':'decl','fields':fields},{'If-Match':'0'})['source_revision']
    def observe(key,event):
        global revision
        result=call('POST','/me/blueprint/observations',{'request_id':key,'expected_revision':revision,'event':event});revision=result['source_revision'];return result
    for index,selected in enumerate(a['v3']['policy']['selection']):
        context={'canonical_exercise_id':selected['candidate_id'],'realization_ref':selected['realization_ref'],'context_ref':'synthetic:room','equipment_ref':f'synthetic:device:{index}','side':'BILATERAL','load_semantics':'PER_IMPLEMENT' if selected['candidate_id']=='romanian-deadlift-halteres' else 'MACHINE_DISPLAY_KG'}
        episode=observe(f'open:{index}',{'kind':'CONTEXT_OPENED','context':context,'availability':'AVAILABLE'})['episode_ref']
        setting={'kind':'MASS_KG','unit':'kg','value':17.0+index} # Synthetic observations, not starting-load defaults.
        def event(n,payload):return observe(f'event:{index}:{n}',{'kind':'CALIBRATION_EVENT','episode_ref':episode,'event':payload})
        event(0,{'kind':'CONTEXT_CONFIRMED','setting':setting});event(1,{'kind':'FAMILIARIZATION_CONFIRMED'})
        trial=event(2,{'kind':'ATTEMPT_OBSERVED','setting':setting,'reps':10,'completed':True,'successful':True,'technique':'ACCEPTABLE','discomfort':'NO_CONCERN','occurred_at':datetime.now(UTC).isoformat()})['event_ref']
        event(3,{'kind':'SETTING_ACCEPTED','reference_event_id':trial})
    progress=call('GET','/me/blueprint/declarations')['observation_progress']
    assert len(progress)==7 and all(len(row['events'])==4 for row in progress)
    snapshot=call('POST','/me/blueprint/snapshots',{'request_id':'capture','expected_revision':revision})
    evaluation=call('POST','/me/first-plan/evaluations',{'request_id':'evaluate','snapshot_ref':snapshot['snapshot_ref'],'expected_pins':pins})
    r=evaluation['recommendation'];assert r['scientific_readiness']=='SCIENTIFICALLY_READY' and r['start_permission']=='REQUIRES_TIME_ACK'
    final=call('POST','/me/first-plan/evaluations/'+evaluation['evaluation_ref']+'/time-acknowledgments',{'request_id':'ack','expected_context':{k:r[k] for k in ('request_fingerprint','observation_fingerprint','plan_time_fingerprint','start_policy_ref')}})
    r=final['recommendation'];assert r['start_permission']=='ELIGIBLE'
    command={k:r[k] for k in ('request_fingerprint','observation_fingerprint','full_evaluation_fingerprint','plan_time_fingerprint','binding_ref','binding_digest','bundle_digest','effective_science_digest','engine_version','policy_version','contract_version')}
    command.update(evaluation_ref=final['evaluation_ref'],snapshot_ref=snapshot['snapshot_ref'],source_revision=revision,registry_digest=pins['registry_digest'],selected_scientific_session_id=r['candidate_plan']['sessions'][0]['session_id'])
    start=call('POST','/me/first-session-requests',{'request_id':'first','command':command});assert start['state']=='CREATED'
    execution=call('GET',f"/sessions/{start['session_id']}/execution")['execution'];assert len(execution['exercises'])==7
    ex=execution['exercises'][0];fact={'context':ex['prescription']['context'],'setting':ex['prescription']['setting'],'reps':9,'completed':True,'performed_at':datetime.now(UTC).isoformat()}
    receipt=call('PUT',f"/sessions/{start['session_id']}/sets/{ex['sets'][0]['set_id']}",{'op_id':'actual-fact','expected_set_revision':0,'observation':fact})['receipt'];assert receipt['state']=='APPLIED'
    refreshed=call('GET',f"/sessions/{start['session_id']}/execution")['execution'];assert refreshed['exercises'][0]['sets'][0]['observation']['setting']['value']==17
    assert client.post(f"/api/mobile/v1/sessions/{start['session_id']}/finish",headers=h,json={}).status_code==200
    assert call('GET',f"/sessions/{start['session_id']}/execution")['execution']['status']=='completed'
assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in tuple(sys.modules.items()) if (n=='app' or n.startswith('app.')) and getattr(m,'__file__',None))
assert not any(n.startswith('tools.science_') for n in sys.modules)
print('HERMETIC_REAL_PRODUCER_HTTP_SESSION_LOG_PASS')
"""
    env = {
        **os.environ,
        "APP_ENV": "test",
        "DATABASE_URL": f"sqlite:///{tmp_path}/runtime.db",
        "APP_SECRET_KEY": "synthetic-isolated-hermetic-only",
        "PLAN_V3_CONTROLLED_TEST_ENABLED": "true",
        "PLAN_V3_ACQUISITION_ENABLED": "true",
        "PLAN_V3_EVALUATION_ENABLED": "true",
        "PLAN_V3_CREATION_ENABLED": "true",
        "PLAN_V3_GUIDANCE_ENABLED": "true",
        "PLAN_V3_BUNDLE_PATH": str(bundle),
    }
    result = subprocess.run(
        [sys.executable, "-I", "-c", script, str(deployed), package_digest],
        cwd=deployed,
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert result.returncode == 0, result.stderr[-4000:]
    assert result.stdout.strip().endswith("HERMETIC_REAL_PRODUCER_HTTP_SESSION_LOG_PASS")

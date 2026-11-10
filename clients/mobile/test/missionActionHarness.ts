/** Synthetic HTTP testimony only; never imported by the native runtime. */
import { accountHarness, reply } from './accountDataHarness';
export const CONTRACT = 'mission-action/1.0.0';
export const HOST = 'first-session-runtime/3.0.0';
export function firstUse(owner=7) {
  return {contract_version:CONTRACT,owner_id:owner,requested_path:'FIRST_USE',observed_at:'2026-11-10T12:00:00Z',
    state:'FIRST_USE',source:'OWNED_FIRST_USE',primary_action:{kind:'OPEN_FIRST_USE'},reason:null,
    payload:{execution_profile:'first-plan-execution/3.0.0',calibration_inventory:'plan-calibration-inventory/2.0.0',source_revision:'blueprint-source/0'}};
}
export function resumed(profile='LEGACY_V1',closed=false) {
  return {...firstUse(),state:closed?'FIRST_SESSION_HISTORY':'RESUME',source:closed?'OWNED_FIRST_USE':'OPEN_SESSION',
    primary_action:{kind:closed?'OPEN_FIRST_SESSION_HISTORY':profile==='LEGACY_V1'?'RESUME_LEGACY':'RESUME_V3',session_id:19},
    payload:{state:'RESUME',primary_action:'RESUME',execution_profile:profile,
      session:{id:19,template_slug:'test-session',name:'Test',subtitle:null,started_at:'2026-11-10T09:00:00Z'},position:null}};
}
export function historical() {
 const decision={fingerprint:null,policy:'historical',top:'test-template',alternatives:[]};
 return {...firstUse(),requested_path:'HISTORICAL',state:'HISTORICAL_READY',source:'HISTORICAL_MISSION',
   primary_action:{kind:'START_LEGACY',template_slug:'test-template',decision},payload:{state:'READY',executable:true,
    template:{slug:'test-template',name:'Test',subtitle:null},reason:{phrase:'Server phrase',reasons:[],winning:[],limiting:[],horizon:null,provenance:null},
    alternatives:[],scope:{exercise_count:1,work_set_count:2,first_exercise:{name:'Test movement',set_scheme:null}},zones:[],
    duration_estimate:null,decision,primary_action:'START'}};
}
export function negotiatedReply(body:unknown,status=200,host=true,contract=CONTRACT) {
 return {...reply(body,status),headers:{get:(name:string)=>name.toLowerCase()==='x-auren-mission-action'?contract:
  name.toLowerCase()==='x-auren-mission-v3-host'&&host?HOST:null}} as Response;
}
export async function missionHarness() {
 const s=await accountHarness();let handler:(url:string,init?:RequestInit)=>Promise<Response>=async()=>negotiatedReply(firstUse());
 const fetcher=(url:string|URL|Request,init?:RequestInit)=>handler(String(url),init);
 return {...s,fetcher:fetcher as typeof fetch,respond:(fn:typeof handler)=>{handler=fn;}};
}

import {createHash} from 'node:crypto';
import witness from '../../test/libraryWitness.json';
import {accountHarness, deferred, reply} from '../../test/accountDataHarness';
import {LibraryClient,createLibraryPorts,decodeLibraryDetail,decodeLibraryPage,decodeLibraryCreated,decodeLibraryRefusal,LIBRARY_VERSION} from './library';

const hash=async(raw:string)=>createHash('sha256').update(raw).digest('hex');
const owner=witness.page.owner_id;
const clone=<T,>(x:T):T=>JSON.parse(JSON.stringify(x));
const negotiated=(raw:unknown,status=200,version:string|null=LIBRARY_VERSION)=>({...reply(raw,status),headers:{get:()=>version}} as unknown as Response);
async function setup(){
 const s=await accountHarness();s.setOwner(owner);await s.auth.login('synthetic', 'synthetic',null);
 let handler:(url:string,init?:RequestInit)=>Promise<Response>=async()=>negotiated(witness.page);
 const fetcher=async(url:string|URL|Request,init?:RequestInit)=>{
  if(String(url).endsWith('/auth/me')){
   const token=String((init?.headers as Record<string,string>)?.Authorization??'').replace('Bearer ','');
   return reply(await s.call('/auth/me',{token}));
  }
  return handler(String(url),init);
 };
 const ports=createLibraryPorts('https://qa.test.invalid',fetcher as typeof fetch,hash);
 return {...s,ports,client:new LibraryClient(s.auth,ports),respond:(fn:typeof handler)=>{handler=fn;}};
}

test('decodes source-labelled real HTTP page, detail, created execution and definitive refusal',()=>{
 expect(decodeLibraryPage(witness.page,owner,{section:'all',zone:null})).toEqual(witness.page);
 expect(decodeLibraryDetail(witness.detail,owner,witness.created.source_ref)).toEqual(witness.detail);
 expect(decodeLibraryCreated(witness.created,owner,witness.created.request_sha256,witness.created.source_ref)).toEqual(witness.created);
 expect(decodeLibraryRefusal(witness.refused,409,owner,witness.created.request_sha256)).toEqual(witness.refused);
});
test.each(['owner','extra','count','state','programType','duplicate'])('rejects incoherent page %s rather than empty success',kind=>{
 const x:any=clone(witness.page);
 if(kind==='owner')x.owner_id++;
 if(kind==='extra')x.weight_kg=50;
 if(kind==='count')x.entries[0].counts.exercise_slots=true;
 if(kind==='state')x.collection_state='PARTIAL';
 if(kind==='programType')x.entries[0].kind='PROGRAM_RECOMMENDATION';
 if(kind==='duplicate')x.entries.push(x.entries[0]);
 expect(decodeLibraryPage(x,owner,{section:'all',zone:null})).toBeNull();
});
test.each(['unit','warmup','selection','range','duplicate','identity'])('rejects detail corruption %s without rewriting prescriptions',kind=>{
 const x:any=clone(witness.detail),e=x.composition[0].exercises[0];
 if(kind==='unit')e.weight_kg=40;
 if(kind==='warmup')e.rep_targets[0].is_warmup='false';
 if(kind==='selection')x.selection.native_support.state='UNSUPPORTED';
 if(kind==='range')e.rep_targets[0].min_reps=99;
 if(kind==='duplicate')x.composition[0].exercises.push(e);
 if(kind==='identity')x.source.kind='OWNED_PROGRAM';
 expect(decodeLibraryDetail(x,owner,witness.created.source_ref)).toBeNull();
});
test.each(['echo','owner','profile','cursor','actions','sets','extra'])('created %s mismatch cannot adopt execution',kind=>{
 const x:any=clone(witness.created);
 if(kind==='echo')x.request_sha256='0'.repeat(64);
 if(kind==='owner')x.owner_id++;
 if(kind==='profile')x.execution_profile='SCI_V3';
 if(kind==='cursor')x.execution.cursor_set_id=999999;
 if(kind==='actions')x.execution.allowed_actions=['SCI_OVERRIDE'];
 if(kind==='sets')x.execution.sets.push(x.execution.sets[0]);
 if(kind==='extra')x.execution.claimed_total_external_mass=40;
 expect(decodeLibraryCreated(x,owner,witness.created.request_sha256,witness.created.source_ref)).toBeNull();
});
test.each([401,422,503])('generic HTTP %s is not a certain refusal',status=>{
 expect(decodeLibraryRefusal({detail:{error:'invalid_request'}},status,owner,witness.created.request_sha256)).toBeNull();
});
test('negotiates and omits cookies, preserving page/read identity',async()=>{
 const s=await setup();let init:RequestInit|undefined;
 s.respond(async(url,value)=>{expect(url).toContain('/me/library?section=all&limit=30');init=value;return negotiated(witness.page);});
 expect(await s.client.page({section:'all',zone:null})).toEqual({state:'confirmed',value:witness.page});
 expect(init).toMatchObject({method:'GET',credentials:'omit',headers:{'X-Auren-Library-Contract':LIBRARY_VERSION}});
});
test('missing negotiation echo is unknown, not accepted data',async()=>{
 const s=await setup();s.respond(async()=>negotiated(witness.page,200,null));
 expect(await s.client.page({section:'all',zone:null})).toEqual({state:'unknown'});
});
test('late A response cannot enter B after account switch',async()=>{
 const s=await setup(),late=deferred<Response>();s.respond(async()=>late.promise);
 const pending=s.client.page({section:'all',zone:null});await new Promise(r=>setTimeout(r,0));
 s.setOwner(owner+1);await s.auth.login('B','synthetic',null);late.resolve(negotiated(witness.page));
 expect(await pending).toEqual({state:'cancelled'});
});
test('mutation uses exact body once and does not refresh/replay 401',async()=>{
 const s=await setup();let sends=0;
 s.respond(async(_url,init)=>{sends++;expect(init?.method).toBe('POST');expect(JSON.parse(String(init?.body))).toEqual(witness.request);return negotiated({detail:{error:'unauthorized'}},401);});
 const result=await s.client.start(owner,witness.request.selection_ref,witness.created.source_ref,witness.created.request_sha256);
 expect(result).toEqual({state:'unknown'});expect(sends).toBe(1);
});
test('wrong source or unknown refusal cannot resolve a submitted command',async()=>{
 const s=await setup();s.respond(async()=>negotiated(witness.created,201));
 expect(await s.client.start(owner,witness.request.selection_ref,'x.'+'0'.repeat(64),witness.created.request_sha256)).toEqual({state:'unknown'});
 s.respond(async()=>negotiated({...witness.refused,code:'future_refusal'},409));
 expect(await s.client.start(owner,witness.request.selection_ref,witness.created.source_ref,witness.created.request_sha256)).toEqual({state:'unknown'});
});

test('review M1: canonical zone vocabulary is closed even when an unknown requested filter is echoed',()=>{
 const x:any=clone(witness.page);x.entries[0].zones={state:'MAPPED',codes:['future-unknown-zone']};
 expect(decodeLibraryPage(x,owner,{section:'all',zone:null})).toBeNull();
});
test('review M2: descriptor and per-session source references must match the requested source identity',()=>{
 const x:any=clone(witness.detail);x.source.id+=100000;
 expect(decodeLibraryDetail(x,owner,witness.created.source_ref)).toBeNull();
 const y:any=clone(witness.detail);y.composition[0].source_ref=witness.page.entries[0].source_ref;
 expect(decodeLibraryDetail(y,owner,witness.created.source_ref)).toBeNull();
});

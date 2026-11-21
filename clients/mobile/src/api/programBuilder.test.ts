import {AuthSession} from '../auth/authSession';
import {ApiFailure,type Transport} from './http';
import {ProgramBuilderClient,createProgramBuilderTransport} from './programBuilder';
import {BUILDER_VERSION,prepareBuilderCommand} from '../domain/programBuilderCommand';
const sha=async(s:string)=>require('node:crypto').createHash('sha256').update(s).digest('hex');
const scope='https://qa.invalid',pair={access_token:'access',refresh_token:'refresh',access_expires_in:3600,server_now:'2026-11-15T12:00:00Z'};
const prepare=(operation='CREATE')=>prepareBuilderCommand(7,scope,{contract_version:BUILDER_VERSION,command_id:'one',operation,program_id:operation==='CREATE'?null:3,expected_source_digest:operation==='CREATE'?null:'a'.repeat(64),payload:operation==='CREATE'||operation==='RENAME'?{title:'Programme'}:{}},sha);
const receipt=async()=>{const p=await prepare();return {contract_version:BUILDER_VERSION,owner_id:7,command_id:'one',request_sha256:p.request_sha256,operation:'CREATE',program_id:3,resulting_source_digest:'a'.repeat(64),resulting_version:1,publication_ids:[],selections:[],recorded_at:'2026-11-15T12:00:00Z'};};
const response=(body:unknown,status=200,headers:Record<string,string>={})=>({ok:status<400,status,headers:{get:(key:string)=>headers[key]??({'X-Auren-Program-Builder':BUILDER_VERSION,'Cache-Control':'no-store','Content-Type':'application/json'} as Record<string,string>)[key]??null},text:async()=>JSON.stringify(body)} as Response);
async function fixture(fetchImpl:any,identity=()=>7){
 let refreshes=0;const call:Transport=async<T>(path:string)=>{if(path==='/auth/me')return {id:identity()} as T;if(path==='/auth/refresh')refreshes++;return pair as T;};
 const auth=new AuthSession(call,{read:async()=>'refresh',write:async()=>{},clear:async()=>{}});await auth.login('synthetic','synthetic',null);
 return {auth,client:new ProgramBuilderClient(auth,{scope,call},createProgramBuilderTransport(scope,fetchImpl),7,sha),refreshes:()=>refreshes};
}
test('POST sends exact prepared bytes with negotiation and CREATE CAS and confirms exact receipt',async()=>{
 const fakes=jest.fn(async()=>response(await receipt())),f=await fixture(fakes),p=await prepare();
 expect(await f.client.submit(p)).toEqual({state:'confirmed',value:await receipt()});
 const [url,init]=fakes.mock.calls[0] as any;expect(url).toBe(scope+'/api/mobile/v1/me/program-builder/commands');expect(init.method).toBe('POST');expect(init.body).toBe(p.payload_json);
 expect(init.headers).toMatchObject({'X-Auren-Program-Builder':BUILDER_VERSION,Authorization:'Bearer access','If-None-Match':'*','Content-Type':'application/json'});
});
test('root mutation uses exact If-Match and 401 never replays POST',async()=>{
 const wire=jest.fn(async()=>response({detail:{error:'auth'}},401)),f=await fixture(wire);expect(await f.client.submit(await prepare('RENAME'))).toEqual({state:'unknown'});
 expect(wire).toHaveBeenCalledTimes(1);expect(f.refreshes()).toBe(0);expect((wire.mock.calls[0] as any)[1].headers['If-Match']).toBe('a'.repeat(64));
});
test('refresh owner substitution prevents POST and logout cancels a late receipt',async()=>{
 let owner=8;const wire=jest.fn(),f=await fixture(wire,()=>owner);expect(await f.client.submit(await prepare())).toEqual({state:'changed'});expect(wire).not.toHaveBeenCalled();
 owner=7;let done!:(v:unknown)=>void;wire.mockImplementation(()=>new Promise(r=>{done=r;}));const pending=f.client.submit(await prepare());await new Promise(r=>setTimeout(r,0));await f.auth.logout();done(response(await receipt()));expect(await pending).toEqual({state:'cancelled'});
});
test('foreign backend and corrupted saved bytes cannot send, identity backend mismatch fails closed',async()=>{
 const wire=jest.fn(),f=await fixture(wire),p=await prepare();expect(await f.client.submit({...p,backend_scope:'https://other.invalid'})).toEqual({state:'changed'});
 expect(await f.client.submit({...p,request_sha256:'b'.repeat(64)})).toMatchObject({state:'rejected',status:422});expect(wire).not.toHaveBeenCalled();
 const call:Transport=async()=>{throw Error();};expect(()=>new ProgramBuilderClient(f.auth,{scope:'https://other.invalid',call},createProgramBuilderTransport(scope),7,sha)).toThrow();
});
test('operation 404, 503, unrecognized rejection, malformed echo or missing no-store preserve uncertainty',async()=>{
 const wire=jest.fn(async()=>response({detail:{error:'foreign_or_missing'}},404)),f=await fixture(wire),p=await prepare();expect(await f.client.status(p)).toEqual({state:'unknown'});
 for(const [status,code] of [[503,'storage_unavailable'],[409,'future_error'],[422,null]]){wire.mockImplementation(async()=>response({detail:{error:code}},status as number));expect(await f.client.submit(p)).toEqual({state:'unknown'});}
 wire.mockImplementation(async()=>response(await receipt(),200,{'X-Auren-Program-Builder':'other'}));expect(await f.client.submit(p)).toEqual({state:'unknown'});
 wire.mockImplementation(async()=>response(await receipt(),200,{'Cache-Control':'public'}));expect(await f.client.submit(p)).toEqual({state:'unknown'});
 wire.mockImplementation(async()=>response({detail:{error:'stale_source'}},409));expect(await f.client.submit(await prepare('RENAME'))).toEqual({state:'rejected',status:409,code:'stale_source'});
});
test('empty owner reads are confirmed; invalid page args never acquire or call transport',async()=>{
 const empty={contract_version:BUILDER_VERSION,owner_id:7,items:[],next_cursor:null};const wire=jest.fn(async()=>response(empty)),f=await fixture(wire);
 expect(await f.client.programs()).toEqual({state:'confirmed',value:empty});expect(await f.client.exercises(50)).toEqual({state:'confirmed',value:empty});
 expect(await f.client.programs(51)).toMatchObject({state:'rejected'});expect(await f.client.program(1.5)).toMatchObject({state:'rejected'});expect(wire).toHaveBeenCalledTimes(2);
});
test('transport refuses path escape, query duplication, arbitrary commands and excessive response bytes',async()=>{
 const wire=jest.fn(async()=>response({})),transport=createProgramBuilderTransport(scope,wire as any);
 for(const path of ['/me/program-builder/../auth/me','/me/program-builder/programs?limit=1&limit=2','/me/program-builder/programs?extra=x','/me/program-builder/operations/a%2Fb'])await expect(transport.call(path,'token')).rejects.toBeDefined();
 await expect(transport.call('/me/program-builder/commands','token','{}')).rejects.toBeDefined();expect(wire).not.toHaveBeenCalled();
 wire.mockImplementation(async()=>response('x'.repeat(131073)));await expect(transport.call('/me/program-builder/programs?limit=25','token')).rejects.toBeInstanceOf(ApiFailure);
});
test('a status read refusal cannot establish that an earlier mutation did not happen',async()=>{
 const wire=jest.fn(async()=>response({detail:{error:'unsupported_contract'}},406)),f=await fixture(wire),p=await prepare();expect(await f.client.status(p)).toEqual({state:'unknown'});
 wire.mockImplementation(async()=>response(await receipt()));expect(await f.client.status(p)).toEqual({state:'confirmed',value:await receipt()});
 const [url,init]=wire.mock.calls[1] as any;expect(url).toBe(scope+'/api/mobile/v1/me/program-builder/operations/one');expect(init.method).toBe('GET');expect(init.body).toBeUndefined();
});
test('logout during hash verification cancels the captured intent before authentication',async()=>{
 const wire=jest.fn(),f=await fixture(wire);let finish!:(v:string)=>void;const delayed=()=>new Promise<string>(done=>{finish=done;});
 const call:Transport=async<T>()=>({id:7} as T),client=new ProgramBuilderClient(f.auth,{scope,call},createProgramBuilderTransport(scope,wire as any),7,delayed),p=await prepare();
 const pending=client.submit(p);await f.auth.logout();finish(p.request_sha256);expect(await pending).toEqual({state:'cancelled'});expect(wire).not.toHaveBeenCalled();
});
test('known pre-effect lifecycle refusal rejects initial submit but cannot settle earlier status uncertainty',async()=>{
 const wire=jest.fn(async()=>response({detail:{error:'domain_refused'}},409)),f=await fixture(wire),p=await prepare('PUBLISH');
 expect(await f.client.submit(p)).toEqual({state:'rejected',status:409,code:'domain_refused'});
 expect(await f.client.status(p)).toEqual({state:'unknown'});
});

test.each(['no-store, no-store','NO-STORE, no-store',' no-store , no-store ','no-store,\tNO-STORE'])('combined no-store directives confirm owner reads and exact receipt without another POST: %s',async cache=>{
 const empty={contract_version:BUILDER_VERSION,owner_id:7,items:[],next_cursor:null};
 const wire=jest.fn(async()=>response(empty,200,{'Cache-Control':cache})),f=await fixture(wire),p=await prepare();
 expect(await f.client.programs()).toEqual({state:'confirmed',value:empty});
 wire.mockImplementation(async()=>response(await receipt(),200,{'Cache-Control':cache}));
 expect(await f.client.submit(p)).toEqual({state:'confirmed',value:await receipt()});
 expect(await f.client.status(p)).toEqual({state:'confirmed',value:await receipt()});
 expect(wire.mock.calls.map(call=>(call as any)[1].method)).toEqual(['GET','POST','GET']);
 expect((wire.mock.calls[1] as any)[1].body).toBe(p.payload_json);
});
test.each(['','public','no-store, public','no-store, max-age=0','no-store, no-cache','no-store,','no-store=1','no-store; no-store','no-store,\u00a0no-store','no-store\n'])('unsafe or malformed cache directives preserve command uncertainty without retry: %s',async cache=>{
 const wire=jest.fn(async()=>response(await receipt(),200,{'Cache-Control':cache})),f=await fixture(wire),p=await prepare();
 expect(await f.client.submit(p)).toEqual({state:'unknown'});
 expect(wire).toHaveBeenCalledTimes(1);expect(f.refreshes()).toBe(0);
});
test('missing cache policy preserves command uncertainty',async()=>{
 const value=await receipt(),raw=response(value),get=raw.headers.get;
 raw.headers.get=(key:string)=>key==='Cache-Control'?null:get(key);
 const wire=jest.fn(async()=>raw),f=await fixture(wire);
 expect(await f.client.submit(await prepare())).toEqual({state:'unknown'});expect(wire).toHaveBeenCalledTimes(1);
});

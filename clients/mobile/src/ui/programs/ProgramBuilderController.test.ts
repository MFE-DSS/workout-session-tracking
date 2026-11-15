import {createHash} from 'node:crypto';
import {ProgramBuilderController,type ProgramBuilderPorts} from './ProgramBuilderController';
import {BUILDER_VERSION,prepareBuilderCommand,type BuilderCommand} from '../../domain/programBuilderCommand';
import type {BuilderProgram,BuilderReceipt} from '../../api/programBuilderDTO';
import type {PendingBuilderCommand,ProgramBuilderPendingCommands} from '../../storage/programBuilderPendingCommands';
const hash=async(s:string)=>createHash('sha256').update(s).digest('hex');
const clone=<T,>(v:T):T=>JSON.parse(JSON.stringify(v));
function harness(){
 let current=true,sequence=0,unknown=false,reject=false,readUnknown=false;
 let program:BuilderProgram={id:7,title:'Personnel',slug_base:'personnel',status:'draft',version:1,source_digest:'a'.repeat(64),publication_ids:[],sessions:[]};
 const rows=new Map<string,PendingBuilderCommand>(),sent:BuilderCommand[]=[];
 const store:ProgramBuilderPendingCommands={ownerId:3,backendScope:'https://qa.invalid',
  prepare:async body=>{const p=await prepareBuilderCommand(3,'https://qa.invalid',body,hash);const row={...p,state:'PREPARED' as const,receipt:null,rejection:null,rejection_status:null,created_at_ms:1};rows.set(p.command_id,row);return clone(row);},
  get:async key=>clone(rows.get(key)??null),pending:async()=>clone([...rows.values()].filter(r=>r.state==='PREPARED'||r.state==='SENT_UNKNOWN')),
  markUnknown:async key=>{rows.get(key)!.state='SENT_UNKNOWN';},ack:async(key,receipt)=>{Object.assign(rows.get(key)!,{state:'ACKED',receipt});},refuse:async(key,_hash,code,status)=>{Object.assign(rows.get(key)!,{state:'REFUSED',rejection:code,rejection_status:status});}};
 const client={ownerId:3,backendScope:'https://qa.invalid',
  programs:jest.fn(async()=>({state:'confirmed',value:{contract_version:BUILDER_VERSION,owner_id:3,items:[clone(program)],next_cursor:null}})),
  exercises:jest.fn(async()=>({state:'confirmed',value:{contract_version:BUILDER_VERSION,owner_id:3,items:[{slug:'squat',name:'Squat',ekb_version:'v1',equipment_family:null,movement_pattern:null}],next_cursor:null}})),
  program:jest.fn(async()=>readUnknown?{state:'unknown'}:{state:'confirmed',value:{contract_version:BUILDER_VERSION,owner_id:3,program:clone(program)}}),
  status:jest.fn(async()=>({state:'unknown'})),
  submit:jest.fn(async(row:PendingBuilderCommand)=>{const b=JSON.parse(row.payload_json) as BuilderCommand;sent.push(b);if(unknown)return {state:'unknown'};if(reject)return {state:'rejected',status:409,code:'stale_source'};
   if(b.operation==='CREATE'||b.operation==='RENAME')program.title=(b.payload as {title:string}).title;
   if(b.operation==='VALIDATE')program.status='validated';if(b.operation==='PUBLISH')program.status='published';if(b.operation==='ARCHIVE')program.status='archived';if(b.operation==='NEW_CYCLE'){program.status='draft';program.version++;}
   program.source_digest=String(sequence%10).repeat(64);
   const receipt:BuilderReceipt={contract_version:BUILDER_VERSION,owner_id:3,command_id:b.command_id,request_sha256:row.request_sha256,operation:b.operation,program_id:7,resulting_source_digest:program.source_digest,resulting_version:program.version,publication_ids:[],selections:[],recorded_at:'2026-11-15T12:00:00Z'};return {state:'confirmed',value:receipt};})};
 const ports={client,store,current:()=>current,newId:()=>`command-${++sequence}`} as unknown as ProgramBuilderPorts;
 return {ports,client,store,rows,sent,get program(){return program;},set program(p){program=p;},setCurrent:(v:boolean)=>{current=v;},setUnknown:()=>{unknown=true;},setReject:()=>{reject=true;},setReadUnknown:()=>{readUnknown=true;},controller:new ProgramBuilderController(ports)};
}
test('initial/foreground loading is GET-only; create needs an explicit title and command',async()=>{
 const h=harness(),c=h.controller;await c.refresh();expect(h.sent).toEqual([]);expect(c.state.programs[0].id).toBe(7);
 c.create();await c.command('CREATE');expect(h.sent).toEqual([]);c.title('Choisi');await c.command('CREATE');
 expect(h.sent[0]).toMatchObject({operation:'CREATE',program_id:null,expected_source_digest:null,payload:{title:'Choisi'}});expect(c.state.source?.title).toBe('Choisi');expect(h.client.program).toHaveBeenCalledTimes(1);
 await c.refresh();expect(h.sent).toHaveLength(1);
});
test('ordered sessions, canonical selection and manual targets produce exact SAVE_TREE',async()=>{
 const h=harness(),c=h.controller;await c.select(7);c.addSession();c.sessionName('A');c.addSession();c.sessionName('B');c.moveSession(-1);
 await c.loadExercises();c.chooseExercise(c.state.exercises[0]);const m=c.activeMovement();expect(m).toMatchObject({kind:'manual',sets:'',targets:[]});
 await c.command('SAVE_TREE');expect(h.sent).toEqual([]);c.movementSets('2');c.target(0,'min','8');c.target(0,'max','12');c.target(1,'min','6');c.target(1,'max','10');await c.command('SAVE_TREE');
 const b=h.sent[0];expect(b.operation).toBe('SAVE_TREE');expect(b.expected_source_digest).toBe('a'.repeat(64));
 expect((b.payload as any).sessions.map((s:any)=>s.name)).toEqual(['B','A']);expect((b.payload as any).sessions[0].exercises[0]).toEqual({position:1,keep:null,selection:{slug:'squat',name:'Squat',ekb_version:'v1'},notes:null,rep_targets:[{min_reps:8,max_reps:12,technique:null,is_warmup:false},{min_reps:6,max_reps:10,technique:null,is_warmup:false}]});
});
test('structural validation is distinct; publishing/new-cycle/archive each require explicit confirmation',async()=>{
 const h=harness(),c=h.controller;await c.select(7);await c.command('PUBLISH',true);expect(h.sent).toHaveLength(0);
 await c.command('VALIDATE');expect(c.state.source?.status).toBe('validated');expect(c.state.source?.publication_ids).toEqual([]);
 await c.command('PUBLISH');expect(h.sent.map(b=>b.operation)).toEqual(['VALIDATE']);expect(c.state.confirm).toBe('PUBLISH');
 await c.command('PUBLISH',true);expect(c.state.source?.status).toBe('published');c.addSession();expect(c.state.draft?.sessions).toHaveLength(0);await c.command('SAVE_TREE');expect(h.sent).toHaveLength(2);
 await c.command('NEW_CYCLE');expect(h.sent).toHaveLength(2);await c.command('NEW_CYCLE',true);expect(c.state.source?.version).toBe(2);
 await c.command('ARCHIVE');expect(h.sent).toHaveLength(3);await c.command('ARCHIVE',true);expect(c.state.source?.status).toBe('archived');
});
test('unknown commands retain drafts; GET verify unlocks only explicit same-key exact replay',async()=>{
 const h=harness(),c=h.controller;await c.select(7);c.title('À garder');h.setUnknown();await c.command('RENAME');const initial=clone(h.sent[0]);expect(c.state.draft?.title).toBe('À garder');expect(c.state.pending).toHaveLength(1);
 await c.refresh();expect(h.sent).toHaveLength(1);await c.replay(c.state.pending[0]);expect(h.sent).toHaveLength(1);
 await c.verify(c.state.pending[0]);expect(h.client.status).toHaveBeenCalledTimes(1);expect(h.sent).toHaveLength(1);
 await c.replay(c.state.pending[0]);expect(h.sent).toHaveLength(2);expect(h.sent[1]).toEqual(initial);expect(c.state.draft?.title).toBe('À garder');
});
test('receipt never grants permission or updates current facts when following GET is unknown',async()=>{
 const h=harness(),c=h.controller;await c.select(7);h.setReadUnknown();await c.command('VALIDATE');expect(c.state.source?.status).toBe('draft');expect(c.state.fresh).toBe(false);await c.command('PUBLISH',true);expect(h.sent).toHaveLength(1);
});
test('stale source refusal and subsequent refresh preserve local draft and require explicit discard',async()=>{
 const h=harness(),c=h.controller;await c.select(7);c.title('Local');h.setReject();await c.command('RENAME');expect(c.state.draft?.title).toBe('Local');expect(c.state.fresh).toBe(false);
 h.program={...h.program,title:'Autre appareil',source_digest:'c'.repeat(64)};await c.refresh();expect(c.state.conflict).toBe(true);expect(c.state.draft?.title).toBe('Local');await c.command('RENAME');expect(h.sent).toHaveLength(1);
 c.discard();expect(c.state.draft?.title).toBe('Autre appareil');expect(c.state.conflict).toBe(false);
});
test('late GET after current account/host becomes invalid cannot expose source or send',async()=>{
 const h=harness();let resolve!:(v:any)=>void;h.client.program.mockImplementationOnce(()=>new Promise(r=>{resolve=r;}));const c=h.controller,pending=c.select(7);for(let i=0;i<10;i++)await Promise.resolve();h.setCurrent(false);resolve({state:'confirmed',value:{program:h.program}});await pending;
 expect(c.state.source).toBeUndefined();await c.command('VALIDATE');expect(h.sent).toEqual([]);
});
test('renaming preserves unsent composition while confirmed tree save preserves unsent title',async()=>{
 const h=harness(),c=h.controller;await c.select(7);c.addSession();c.sessionName('Non envoyée');c.title('Nom envoyé');await c.command('RENAME');
 expect(c.state.draft?.sessions.map(s=>s.name)).toEqual(['Non envoyée']);expect(c.dirtyTree()).toBe(true);
 c.title('Nom non envoyé');await c.command('SAVE_TREE');expect(c.state.draft?.title).toBe('Nom non envoyé');expect(c.dirtyTitle()).toBe(true);
});
test('historical verified receipt followed by newer source retains draft as conflict, not current permission',async()=>{
 const h=harness(),c=h.controller;await c.select(7);c.title('Publication perdue');h.setUnknown();await c.command('RENAME');const row=c.state.pending[0];
 h.client.status.mockImplementationOnce(async()=>({state:'confirmed',value:{contract_version:BUILDER_VERSION,owner_id:3,command_id:row.command_id,request_sha256:row.request_sha256,operation:'RENAME',program_id:7,resulting_source_digest:'b'.repeat(64),resulting_version:1,publication_ids:[],selections:[],recorded_at:'2026-11-15T12:00:00Z'}} as any));
 h.program={...h.program,title:'Changement ultérieur',status:'published',source_digest:'c'.repeat(64)};await c.verify(row);
 expect(c.state.source?.title).toBe('Changement ultérieur');expect(c.state.source?.status).toBe('published');expect(c.state.draft?.title).toBe('Publication perdue');expect(c.state.conflict).toBe(true);expect(c.can('NEW_CYCLE')).toBe(false);
});

test('verifying another programme cannot replace a new unsent creation draft',async()=>{
 const h=harness(),c=h.controller;await c.select(7);c.title('Perdu');h.setUnknown();await c.command('RENAME');const row=c.state.pending[0];
 c.create();c.title('Nouveau non envoyé');
 h.client.status.mockImplementationOnce(async()=>({state:'confirmed',value:{contract_version:BUILDER_VERSION,owner_id:3,command_id:row.command_id,request_sha256:row.request_sha256,operation:'RENAME',program_id:7,resulting_source_digest:'b'.repeat(64),resulting_version:1,publication_ids:[],selections:[],recorded_at:'2026-11-15T12:00:00Z'}} as any));
 await c.verify(row);expect(c.state.view).toBe('create');expect(c.state.draft?.title).toBe('Nouveau non envoyé');expect(c.state.pending).toEqual([]);
});

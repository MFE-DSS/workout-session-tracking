import React,{act} from 'react';
import {createRoot,type Root} from 'test-renderer';
import {ProgramBuilderScreen} from './ProgramBuilderScreen';
import {ProgramBuilderController,type ProgramBuilderPorts} from './ProgramBuilderController';
import {manualMovement} from './programBuilderModel';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
let root:Root;beforeEach(()=>{root=createRoot();});afterEach(async()=>{await act(async()=>root.unmount());});
const node=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
const text=(x:any):string=>Array.isArray(x)?x.map(text).join(''):typeof x==='string'||typeof x==='number'?String(x):x?.props?text(x.props.children):'';
const allText=()=>root.container.queryAll(()=>true).map((n:any)=>text(n.props.children)).join('\n');
const press=async(id:string)=>act(async()=>node(id).onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));
function controller(){const c=new ProgramBuilderController({client:{ownerId:1,backendScope:'https://qa.invalid'},store:{ownerId:1,backendScope:'https://qa.invalid'},current:()=>true,newId:()=> 'id'} as ProgramBuilderPorts);Object.assign(c.state,{view:'editor',fresh:true,source:{id:1,title:'Choisi',slug_base:'choisi',status:'draft',version:2,source_digest:'a'.repeat(64),publication_ids:[],sessions:[]},draft:{title:'Choisi',sessions:[{name:'A',kind:'strength',focus:'',duration_target_minutes:null,notes:null,movements:[manualMovement({slug:'squat',name:'Squat',ekb_version:'v1'})]}]}});return c;}
test('G1 uses one active DA08 surface with empty numeric inputs and explicit save, without launch/calendar claims',async()=>{
 const c=controller();await act(async()=>root.render(React.createElement(ProgramBuilderScreen,{controller:c,onBack:()=>{}})));
 expect(node('builder-sets')?.value).toBe('');expect(node('builder-reps-min-0')).toBeUndefined();expect(node('builder-save')?.accessibilityState.disabled).toBe(true);
 expect(root.container.queryAll((n:any)=>n.props.testID==='da08-surface')).toHaveLength(1);
 expect(allText()).not.toContain('Programme actif');expect(allText()).not.toContain('Lundi');expect(allText()).not.toContain('Démarrer');
 const controls=root.container.queryAll((n:any)=>n.props.accessibilityRole==='button'||n.props.accessibilityRole==='radio');for(const control of controls)expect(control.props.style.minHeight).toBeGreaterThanOrEqual(48);
});
test('historical source shows stored targets/unknown identity without applying new manual bounds',async()=>{
 const c=controller();c.state.draft!.sessions[0].movements=[{kind:'historical',source:{slot_id:8,slot_digest:'b'.repeat(64),position:1,exercise_name:'Historique',set_scheme:'ancienne',variant_key:null,variant_group:null,equipment_family:null,movement_pattern:null,notes:null,source_reason:null,rep_targets:[{set_index:0,min_reps:75,max_reps:90,technique:null,is_warmup:false}],identity:{state:'UNRESOLVED',slug:null,name:null,ekb_version:null}}}];
 await act(async()=>root.render(React.createElement(ProgramBuilderScreen,{controller:c,onBack:()=>{}})));expect(allText()).toContain('75–90');expect(allText()).toContain('Identité non cartographiée');expect(node('builder-sets')).toBeUndefined();expect(node('builder-save')?.accessibilityState.disabled).toBe(false);
});
test('published source stays read-only with explicit new-cycle confirmation and library return',async()=>{
 const c=controller();c.state.source!.status='published';c.state.draft!.sessions=[];
 await act(async()=>root.render(React.createElement(ProgramBuilderScreen,{controller:c,onBack:()=>{}})));expect(node('builder-new-cycle')).toBeDefined();expect(node('builder-save')).toBeUndefined();expect(node('builder-add-session')).toBeUndefined();
 await press('builder-new-cycle');await act(async()=>root.render(React.createElement(ProgramBuilderScreen,{controller:c,onBack:()=>{}})));expect(allText()).toContain('Les publications et séances précédentes sont conservées.');expect(node('builder-confirm-new-cycle')).toBeDefined();
});
test('pending verification exposes same-command retry only after GET verification',async()=>{
 const c=controller();c.state.pending=[{command_id:'lost',operation:'PUBLISH',program_id:1,request_sha256:'c'.repeat(64)} as any];
 await act(async()=>root.render(React.createElement(ProgramBuilderScreen,{controller:c,onBack:()=>{}})));expect(node('builder-verify-lost')).toBeDefined();expect(node('builder-replay-lost')).toBeUndefined();
 c.state.replayKeys=['lost'];await act(async()=>root.render(React.createElement(ProgramBuilderScreen,{controller:c,onBack:()=>{}})));expect(node('builder-replay-lost')).toBeDefined();
});

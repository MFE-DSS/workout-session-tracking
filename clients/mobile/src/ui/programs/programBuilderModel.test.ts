import {draftFromProgram,manualMovement,treePayload,moveItem,setCount} from './programBuilderModel';
import type {BuilderProgram} from '../../api/programBuilderDTO';
export const source:BuilderProgram={id:7,title:'Personnel',slug_base:'personnel',status:'draft',version:1,source_digest:'a'.repeat(64),publication_ids:[],sessions:[{position:1,name:'Séance historique',kind:'strength',focus:'ancien',duration_target_minutes:0,notes:'préservée',exercises:[{slot_id:22,slot_digest:'b'.repeat(64),position:1,exercise_name:'Ancien inconnu',set_scheme:'ancien',variant_key:null,variant_group:null,equipment_family:null,movement_pattern:null,notes:'historique',source_reason:null,rep_targets:[{set_index:0,min_reps:75,max_reps:90,technique:null,is_warmup:false}],identity:{state:'UNRESOLVED',slug:null,name:null,ekb_version:null}}]}]};
test('historical unknown/out-of-bound slots save as exact keep tokens with preserved session metadata',()=>{
 const d=draftFromProgram(source),tree=treePayload(d);
 expect(tree.sessions[0]).toMatchObject({name:'Séance historique',focus:'ancien',duration_target_minutes:0,notes:'préservée'});
 expect(tree.sessions[0].exercises[0]).toEqual({position:1,selection:null,keep:{slot_id:22,slot_digest:'b'.repeat(64)},rep_targets:null,notes:null});
 expect(d.sessions[0].movements[0]).toMatchObject({kind:'historical',source:{exercise_name:'Ancien inconnu'}});
});
test('manual prescriptions start empty, require exact explicit integers, and do not normalize user input',()=>{
 const d=draftFromProgram({...source,sessions:[]});d.sessions.push({name:'Choisie',kind:'strength',focus:'',duration_target_minutes:null,notes:null,movements:[]});
 const m=manualMovement({slug:'squat',name:'Squat',ekb_version:'v1'});d.sessions[0].movements.push(m);
 expect(m.sets).toBe('');expect(m.targets).toEqual([]);expect(()=>treePayload(d)).toThrow();
 setCount(m,'2');expect(m.targets).toEqual([{min:'',max:'',technique:null,is_warmup:false},{min:'',max:'',technique:null,is_warmup:false}]);
 m.targets.forEach(t=>{t.min='8';t.max='12';});expect(treePayload(d).sessions[0].exercises[0].rep_targets).toEqual([{min_reps:8,max_reps:12,technique:null,is_warmup:false},{min_reps:8,max_reps:12,technique:null,is_warmup:false}]);
 for(const value of ['01',' 2','2.0','7','0']){m.sets=value;expect(()=>treePayload(d)).toThrow();}m.sets='2';m.targets[0].min='08';expect(()=>treePayload(d)).toThrow();
});
test('session/movement reordering changes real wire order and never invents identities',()=>{
 const d=draftFromProgram(source);d.sessions.push({...d.sessions[0],name:'Deuxième',movements:[]});moveItem(d.sessions,1,-1);
 expect(treePayload(d).sessions.map(s=>[s.position,s.name])).toEqual([[1,'Deuxième'],[2,'Séance historique']]);
 expect(treePayload(d).sessions[1].exercises[0].selection).toBeNull();
});

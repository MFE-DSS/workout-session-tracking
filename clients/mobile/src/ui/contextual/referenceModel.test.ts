import {contextualFixture} from '../../../test/contextualHarness';
import {contextTarget,selectReference} from './referenceModel';
test('previous completed server observation is a reference, never a prefilled prescription',()=>{
 const f=contextualFixture(),target=contextTarget(f.state,f.set.set_id)!;f.exercise.prescription.setting.value=99;const before=JSON.stringify(f.state);
 expect(selectReference(target,f.execution)).toMatchObject({setId:f.exercise.sets[0].set_id,value:17.5,reps:9,revision:1,unit:'kg',semantics:'MACHINE_DISPLAY_KG'});
 expect(f.state.drafts).toEqual({});expect(JSON.stringify(f.state)).toBe(before);
});
test.each(['session','binding','start','exercise','slot','intent','equipment','context','realization','side','semantics','unit','kind','unknown','missing','incomplete','revision','reps','nan','coherence'])('rejects unqualified %s reference',kind=>{
 const f=contextualFixture(),t=contextTarget(f.state,f.set.set_id)!,e=f.exercise,s=e.sets[0],o=s.observation!;
 if(kind==='session')f.execution.session_id++;if(kind==='binding')f.execution.binding_digest='f'.repeat(64);if(kind==='start')f.execution.started_at='2026-11-08T00:00:00Z';
 if(kind==='exercise')e.canonical_exercise_id='different';if(kind==='slot')e.slot_id+='different';if(kind==='intent')e.intent_id+='different';
 if(['equipment','context','realization'].includes(kind))(o.context as any)[kind+'_ref']='different';
 if(kind==='side')o.context.side='LEFT';if(kind==='semantics')o.context.load_semantics='PER_IMPLEMENT';if(kind==='unit')o.setting!.unit='setting';if(kind==='kind')o.setting!.kind='NON_MASS_SETTING';
 if(kind==='unknown')o.context.equipment_ref=null;if(kind==='missing')s.observation=null;if(kind==='incomplete'){s.completed=false;o.completed=false;}
 if(kind==='revision')s.revision=0;if(kind==='reps'){s.reps=null;o.reps=null;}if(kind==='nan')o.setting!.value=NaN;if(kind==='coherence')s.reps=8;
 expect(selectReference(t,f.execution)).toBeNull();
});
test('only immediate prior set: first set has no reference and no older fallback',()=>{
 const f=contextualFixture();expect(selectReference(contextTarget(f.state,f.exercise.sets[0].set_id)!,f.execution)).toBeNull();
 const t=contextTarget(f.state,f.set.set_id)!;f.exercise.sets[0].set_index=0;expect(selectReference(t,f.execution)).toBeNull();
});
test('pending or refused local source invalidates old server reference',()=>{
 const f=contextualFixture(),source=f.exercise.sets[0].set_id;expect(selectReference(contextTarget(f.state,f.set.set_id,[source])!,f.execution)).toBeNull();
});
test('selector never upgrades unknown context or per-implement setting',()=>{
 const f=contextualFixture();f.exercise.prescription.context.equipment_ref=null;expect(contextTarget(f.state,f.set.set_id)).toBeNull();
 f.exercise.prescription.context.equipment_ref='known';f.exercise.prescription.context.load_semantics='PER_IMPLEMENT';expect(contextTarget(f.state,f.set.set_id)).toBeNull();
});

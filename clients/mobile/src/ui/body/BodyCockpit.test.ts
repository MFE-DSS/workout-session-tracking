import React,{act} from 'react';
import {createRoot,type Root} from 'test-renderer';
import {BodyCockpit} from './BodyCockpit';
let root:Root;beforeEach(()=>root=createRoot());afterEach(async()=>{await act(async()=>root.unmount());});
const node=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
const click=async(id:string)=>act(async()=>node(id).onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));
const value=(v:number|null)=>({value:v,quality:v===null?'MISSING':'KNOWN',unit:'kg',raw_value_repr:null,provenance:{origin:'USER_DECLARED',acquisition:'MANUAL_ENTRY',source_ref:'owned'}});
function setup(){const rows=[9,11].map((day,i)=>({root_ref:i+1,measurement_id:i+1,revision:1,state:'CURRENT',date_precision:'DAY_UTC_CONVENTION',measured_at:`2026-11-${day===9?'09':day}T00:00:00`,fields:{weight_kg:value(i?71.4:72)}}));return {entries:rows,specs:[{key:'weight_kg',unit:'kg',label:'Poids',min:20,max:400},{key:'arm_cm_right',unit:'cm',label:'Bras droit',min:10,max:100}],previous:false,partial:false,locked:false,onAcquire:jest.fn(),onInspect:jest.fn()} as any;}
test('active instrument uses exact owned observation and integrated acquisition callback',async()=>{
 const p=setup();await act(async()=>root.render(React.createElement(BodyCockpit,p)));await click('body-new');expect(p.onAcquire).toHaveBeenCalledWith('weight_kg',p.entries[1]);await click('body-sources');expect(p.onInspect).toHaveBeenCalledWith(2);
});
test('peripheral unknown selected without borrowing another value or manufacturing history',async()=>{
 const p=setup();await act(async()=>root.render(React.createElement(BodyCockpit,p)));await click('body-field-arm_cm_right');expect(node('body-value-unknown')).toBeDefined();await click('body-new');expect(p.onAcquire).toHaveBeenCalledWith('arm_cm_right',undefined);expect(node('body-plot')).toBeUndefined();
});
test('comparison appears only after an explicit reference choice and disappears when field changes',async()=>{
 await act(async()=>root.render(React.createElement(BodyCockpit,setup())));expect(node('body-comparison')).toBeUndefined();await click('body-compare-open');await click('body-reference-1');expect(node('body-comparison')).toBeDefined();await click('body-field-arm_cm_right');expect(node('body-comparison')).toBeUndefined();
});
test('unknown-date source remains reachable even when it cannot enter the chronology',async()=>{
 const p=setup();p.entries=[{...p.entries[0],date_precision:'UNKNOWN'}];await act(async()=>root.render(React.createElement(BodyCockpit,p)));expect(node('body-plot')).toBeUndefined();await click('body-observations-open');await click('body-observation-1');await click('body-sources');expect(p.onInspect).toHaveBeenCalledWith(1);
});
test('refresh never silently substitutes a new endpoint for an explicitly selected comparison',async()=>{
 const p=setup();await act(async()=>root.render(React.createElement(BodyCockpit,p)));await click('body-compare-open');await click('body-reference-1');
 const next={...p.entries[1],root_ref:3,measurement_id:3,measured_at:'2026-11-12T00:00:00',fields:{weight_kg:value(80)}};
 await act(async()=>root.render(React.createElement(BodyCockpit,{...p,entries:[...p.entries,next]})));await click('body-sources');expect(p.onInspect).toHaveBeenLastCalledWith(2);
});
test('ambiguous known peripheral observations remain selectable facts rather than missing data',async()=>{
 const p=setup();p.entries.push({...p.entries[1],root_ref:3,measurement_id:3});
 await act(async()=>root.render(React.createElement(BodyCockpit,p)));
 await click('body-field-arm_cm_right');
 const peripheral=node('body-peripheral-weight_kg');expect(peripheral).toBeDefined();
 const text=JSON.stringify(root.container.queryAll((n:any)=>n.props.testID==='body-peripheral-weight_kg')[0]);
 expect(text).toContain('Choisir le relevé');expect(text).not.toContain('Non renseigné');
});

import React,{act} from 'react';
import {createRoot,type Root} from 'test-renderer';
import {MeasurementSheet,measurementValues} from './MeasurementSheet';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:24,bottom:24,left:0,right:0}),SafeAreaProvider:({children}:any)=>children,SafeAreaView:({children,...props}:any)=>require('react').createElement(require('react-native').View,props,children)}));
let root:Root;beforeEach(()=>{root=createRoot();});afterEach(async()=>{await act(async()=>root.unmount());});
const spec=(key:string)=>({key,label:key,min:1,max:500,unit:key==='weight_kg'?'kg':'cm'}) as any;
const node=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
// Synthetic legacy DTO projection: preserved facts are not fresh acquisitions.
const legacy=(left=800)=>({measured_at:'2025-01-02T00:00:00Z',date_precision:'UNKNOWN',fields:{
 arm_cm_left:{value:left,quality:'LEGACY_OUTSIDE_CURRENT_BOUNDS'},
 arm_cm_right:{value:32,quality:'KNOWN'},
}}) as any;
test.each([800,-12,1e21])('unchanged legacy %s is inherited while its grouped peer is corrected',left=>{
 expect(measurementValues([spec('arm_cm_left'),spec('arm_cm_right')],{arm_cm_left:String(left),arm_cm_right:'33'},{},legacy(left))).toEqual({arm_cm_right:33});
});
test('the actual grouped native sheet permits peer and date-only corrections without reacquiring legacy values',async()=>{
 const saved:any[]=[];
 await act(async()=>root.render(React.createElement(MeasurementSheet,{specs:[spec('arm_cm_left'),spec('arm_cm_right')],initial:legacy(),busy:false,onClose:()=>{},onSave:(form:any)=>saved.push(form)})));
 await act(async()=>node('body-side-arm_cm_right').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));
 await act(async()=>node('body-value-arm_cm_right').onChangeText('33'));
 expect(node('body-save').accessibilityState.disabled).toBe(false);
 await act(async()=>node('body-save').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));
 expect(saved[0]).toEqual({values:{arm_cm_right:33}});
 await act(async()=>node('body-value-arm_cm_right').onChangeText('32'));
 await act(async()=>node('body-day').onChangeText('2025-01-01'));
 expect(node('body-save').accessibilityState.disabled).toBe(false);
 await act(async()=>node('body-save').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));
 expect(saved[1]).toEqual({values:{},measured_on:'2025-01-01'});
});
test.each(['801','-11','1e20','NaN','Infinity'])('changed or fresh invalid %s remains rejected',raw=>{
 expect(()=>measurementValues([spec('arm_cm_left')],{arm_cm_left:raw},{},legacy())).toThrow('invalid_value');
 expect(()=>measurementValues([spec('arm_cm_left')],{arm_cm_left:raw},{})).toThrow('invalid_value');
});
test('comma decimal and a single declared side do not zero or clear the other side',()=>{
 expect(measurementValues([spec('arm_cm_left'),spec('arm_cm_right')],{arm_cm_left:'32,5',arm_cm_right:''},{})).toEqual({arm_cm_left:32.5});
 expect(measurementValues([spec('weight_kg')],{weight_kg:''},{weight_kg:true})).toEqual({weight_kg:null});
 expect(()=>measurementValues([spec('weight_kg')],{weight_kg:'NaN'},{})).toThrow();
});
test('day is explicit and all writes are disabled without one; decimal input and 48dp controls',async()=>{
 const sent:any[]=[];await act(async()=>root.render(React.createElement(MeasurementSheet,{specs:[spec('weight_kg')],onSave:(v:any)=>sent.push(v),onClose:()=>{},busy:false})));
 expect(node('body-value-weight_kg').inputMode).toBe('decimal');expect(node('body-save').accessibilityState.disabled).toBe(true);
 await act(async()=>node('body-value-weight_kg').onChangeText('72,5'));
 await act(async()=>node('body-day').onChangeText('2026-11-11'));
 await act(async()=>node('body-save').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));
 expect(sent[0]).toEqual({values:{weight_kg:72.5},measured_on:'2026-11-11'});
});
test('choosing a day alone cannot enable creation of an empty observation',async()=>{
 await act(async()=>root.render(React.createElement(MeasurementSheet,{specs:[spec('weight_kg')],onSave:()=>{},onClose:()=>{},busy:false})));
 await act(async()=>node('body-day').onChangeText('2026-11-11'));
 expect(node('body-save').accessibilityState.disabled).toBe(true);
});
test('bilateral editor activates one channel at a time and preserves the unentered peer',async()=>{
 const save=jest.fn();await act(async()=>root.render(React.createElement(MeasurementSheet,{specs:[spec('arm_cm_left'),spec('arm_cm_right')],onSave:save,onClose:()=>{},busy:false})));
 expect(node('body-value-arm_cm_left')).toBeDefined();expect(node('body-value-arm_cm_right')).toBeUndefined();
 await act(async()=>node('body-side-arm_cm_right').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));
 await act(async()=>node('body-value-arm_cm_right').onChangeText('33,1'));await act(async()=>node('body-day').onChangeText('2026-11-11'));
 await act(async()=>node('body-save').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));
 expect(save).toHaveBeenCalledWith({values:{arm_cm_right:33.1},measured_on:'2026-11-11'});
});
test('acquisition reference is display-only and never pre-fills or silently copies the earlier observation',async()=>{
 const previous:any={measured_at:'2026-11-11T00:00:00Z',date_precision:'DAY_UTC_CONVENTION',fields:{weight_kg:{value:71.4,quality:'KNOWN'}}};
 await act(async()=>root.render(React.createElement(MeasurementSheet,{specs:[spec('weight_kg')],reference:previous,onSave:()=>{},onClose:()=>{},busy:false} as any)));
 expect(node('body-acquisition-reference')).toBeDefined();expect(node('body-value-weight_kg').value).toBe('');
 await act(async()=>node('body-day').onChangeText('2026-11-11'));expect(node('body-save').accessibilityState.disabled).toBe(true);
});
test('single acquisition owns modal safe areas and prevents silent abandonment of an edited draft',async()=>{
 const close=jest.fn();await act(async()=>root.render(React.createElement(MeasurementSheet,{specs:[spec('weight_kg')],onSave:()=>{},onClose:close,busy:false})));
 expect(node('body-acquisition-safe-surface')).toBeDefined();
 await act(async()=>node('body-value-weight_kg').onChangeText('71,5'));
 await act(async()=>node('body-cancel').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));
 expect(close).not.toHaveBeenCalled();expect(node('body-keep-draft')).toBeDefined();
 await act(async()=>node('body-keep-draft').onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));
 expect(node('body-value-weight_kg').value).toBe('71,5');
});

test('correction exposes busy command and expanded contextual help to accessibility',async()=>{
 await act(async()=>root.render(React.createElement(MeasurementSheet,{specs:[spec('arm_cm_right')],initial:legacy(),onSave:()=>{},onClose:()=>{},busy:true})));
 expect(node('body-save').accessibilityState.busy).toBe(true);expect(node('body-save').accessibilityState.disabled).toBe(true);
 const help=()=>root.container.queryAll((n:any)=>n.props.accessibilityLabel==='Source et aide')[0]?.props;
 expect(help().accessibilityState.expanded).toBe(false);
 await act(async()=>help().onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));
 expect(help().accessibilityState.expanded).toBe(true);
});

import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {MeasurementMemory} from './MeasurementMemory';
import {color} from '../theme';
jest.mock('react-native-svg',()=>{const R=require('react'),V=require('react-native').View;const component=(p:any)=>R.createElement(V,p);return {__esModule:true,default:component,Circle:component,Line:component};});
test('selecting a manual observation preserves its filled provenance symbol',async()=>{
 const root=createRoot(),row:any={entry:{measurement_id:1},day:'2026-11-11',key:'weight_kg',value:{value:71,quality:'KNOWN',unit:'kg',provenance:{origin:'USER_DECLARED',acquisition:'MANUAL_ENTRY'}}};
 await act(async()=>root.render(React.createElement(MeasurementMemory,{rows:[row],unit:'kg',selected:1,onChoose:()=>{}})));
 const point=root.container.queryAll((n:any)=>n.props.r===5&&n.props.stroke===color.signal)[0];
 expect(point.props.fill).toBe(color.ink2);
 await act(async()=>root.unmount());
});

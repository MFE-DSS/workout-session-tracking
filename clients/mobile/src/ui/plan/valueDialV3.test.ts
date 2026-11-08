import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {ValueDial} from '../components';
test('unknown hardware increment disables arithmetic pads and accessibility increments; direct entry remains available',async()=>{
 const root=createRoot(),edit=jest.fn();await act(async()=>root.render(React.createElement(ValueDial,{label:'Par élément',value:'—',unit:'kg',stepLabel:'réglage',stepAvailable:false,onMinus:jest.fn(),onPlus:jest.fn(),onEdit:edit})));
 const plus=root.container.queryAll(n=>n.props.accessibilityLabel==='Plus réglage')[0];expect(plus.props.accessibilityState?.disabled).toBe(true);
 const entry=root.container.queryAll(n=>n.props.accessibilityHint==='Toucher pour saisir une valeur')[0];expect(entry.props.accessibilityActions).toBeUndefined();
 await act(async()=>entry.props.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));expect(edit).toHaveBeenCalledTimes(1);await act(async()=>root.unmount());
});

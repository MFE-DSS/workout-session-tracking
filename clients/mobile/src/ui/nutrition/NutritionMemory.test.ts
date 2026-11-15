import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {NutritionComparisonReadout,NutritionMemory} from './NutritionMemory';
const values=(n:number|null)=>({kcal_milli:n,protein_milli:null,carbohydrate_milli:null,fat_milli:null});
test.each([[0,0,'0'],[1000,0,'+1'],[0,1000,'−1']])('known intake %s / declared target %s keeps reference and difference without invented zero division',async(a,b,diff)=>{
 const root=createRoot();try{await act(async()=>root.render(React.createElement(NutritionComparisonReadout,{entry:{id:1,local_day:'2026-11-12',state:'ACTIVE',target_ref:9,values:values(a)},target:{id:9,values:values(b)},field:'kcal_milli'} as any)));
  expect(root.container.queryAll((n:any)=>n.props.testID==='nutrition-target-reference-kcal_milli')).toHaveLength(1);
  expect(root.container.queryAll((n:any)=>n.props.accessibilityLabel===`Écart arithmétique ${diff} kcal`)).toHaveLength(1);
  if(b===0)expect(root.container.queryAll((n:any)=>n.props.testID==='nutrition-target-ratio')).toHaveLength(0);
 }finally{await act(async()=>root.unmount());}
});
test('missing intake or foreign target reference does not create a comparison',async()=>{
 const root=createRoot();try{await act(async()=>root.render(React.createElement(NutritionComparisonReadout,{entry:{state:'ACTIVE',target_ref:9,values:values(null)},target:{id:9,values:values(0)},field:'kcal_milli'} as any)));expect(root.container.queryAll((n:any)=>n.props.testID==='nutrition-target-reference-kcal_milli')).toHaveLength(0);
  await act(async()=>root.render(React.createElement(NutritionComparisonReadout,{entry:{state:'ACTIVE',target_ref:8,values:values(1000)},target:{id:9,values:values(1000)},field:'kcal_milli'} as any)));expect(root.container.queryAll((n:any)=>n.props.testID==='nutrition-target-ratio')).toHaveLength(0);
 }finally{await act(async()=>root.unmount());}
});
test.each([7,30])('mixed %s-day current heads expose coverage, real zero points and absent days without double counting',async period=>{
 const root=createRoot(),rows=[{id:1,local_day:'2026-11-06',revision:1,state:'ACTIVE',declared_complete:false,values:values(0)}, {id:3,local_day:'2026-11-08',revision:2,state:'ACTIVE',declared_complete:true,values:values(2000000)}, {id:4,local_day:'2026-11-09',revision:2,state:'WITHDRAWN',declared_complete:false,values:values(null)}];
 const state:any={state:'confirmed',previous:null,value:{entries:rows,window:{from:period===7?'2026-11-06':'2026-10-14',through:'2026-11-12'},coverage:{kcal_milli:{known_days:2,missing_days:period-2,partial_days:1,declared_complete_days:1,withdrawn_days:1,total_calendar_days:period}},totals:{kcal_milli:{value:2000000,known_days:2}}}};
 try{await act(async()=>root.render(React.createElement(NutritionMemory,{state,field:'kcal_milli',onDay:()=>{}})));
  const labels=root.container.queryAll((n:any)=>typeof n.props.accessibilityLabel==='string').map((n:any)=>n.props.accessibilityLabel);
  expect(labels).toContain(`Couverture Énergie : 2 jours connus, ${period-2} jours sans valeur, 1 partiel, 1 déclaré complet, 1 retiré, sur ${period} jours`);
  expect(labels).toContain('2026-11-06 · 0 kcal · partiel');expect(labels).toContain('2026-11-07 · absent');expect(labels).toContain('2026-11-08 · 2 000 kcal · déclaré complet');
  expect(root.container.queryAll((n:any)=>n.props.testID==='nutrition-history-point-1')).toHaveLength(1);expect(root.container.queryAll((n:any)=>n.props.testID==='nutrition-history-point-3')).toHaveLength(1);expect(root.container.queryAll((n:any)=>n.props.testID==='nutrition-history-point-4')).toHaveLength(0);
  if(period===30){const all=root.container.queryAll((n:any)=>n.props.accessibilityLabel==='Tous les 30 jours')[0];expect(all).toBeDefined();await act(async()=>all.props.onClick({nativeEvent:{},stopPropagation:()=>{},currentTarget:1,target:1}));expect(root.container.queryAll((n:any)=>n.props.accessibilityLabel==='2026-10-14 · absent')).toHaveLength(1);}
 }finally{await act(async()=>root.unmount());}
});

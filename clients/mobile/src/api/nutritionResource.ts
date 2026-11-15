import type {NutritionClient} from './nutrition';
import {decodeNutritionPage,nutritionCoverageMatches,type NutritionPage,type NutritionRead} from './nutritionDTO';
export type NutritionCollectionState={state:'confirmed'|'partial'|'unknown'|'cancelled'|'consent_required'|'rejected'|'changed'|'unavailable';value:NutritionPage|null;previous:NutritionPage|null};
/** A partial page traversal is never presented as an empty or complete daily log. */
export class NutritionResource{
 private generation=0;
 private previous:NutritionPage|null=null;
 private pending:{options:NutritionRead;page:NutritionPage;ids:Set<string>;keys:Set<string>;cursors:Set<string>}|null=null;
 constructor(private client:NutritionClient,private current:()=>boolean){}
 private result(state:NutritionCollectionState['state'],value:NutritionPage|null=null):NutritionCollectionState{
  if(!this.current()){this.previous=null;this.pending=null;return{state:'cancelled',value:null,previous:null};}
  return JSON.parse(JSON.stringify({state,value,previous:this.previous}));
 }
 async load(options:NutritionRead):Promise<NutritionCollectionState>{
  const generation=++this.generation;this.pending=null;
  return this.traverse({...options,cursor:undefined},generation);
 }
 async resume():Promise<NutritionCollectionState>{
  if(!this.pending)return this.result('unknown');
  return this.traverse(this.pending.options,++this.generation);
 }
 private async traverse(options:NutritionRead,generation:number):Promise<NutritionCollectionState>{
  for(let budget=0;budget<50;budget++){
   if(!this.current()||generation!==this.generation)return{state:'cancelled',value:null,previous:null};
   const outcome=await this.client.read(options);
   if(!this.current()||generation!==this.generation)return{state:'cancelled',value:null,previous:null};
   if(outcome.state!=='confirmed'){
    if(outcome.state==='changed'||outcome.state==='cancelled'||outcome.state==='consent_required'){this.previous=null;this.pending=null;return this.result(outcome.state);}
    return this.pending?this.result('partial',this.pending.page):this.result(outcome.state);
   }
   const page=decodeNutritionPage(outcome.value,this.client.ownerId,options);
   const prior=this.pending;
   if(!page||prior&&(page.read_id!==prior.page.read_id||JSON.stringify(page.window)!==JSON.stringify(prior.page.window)||JSON.stringify(page.coverage)!==JSON.stringify(prior.page.coverage)||JSON.stringify(page.totals)!==JSON.stringify(prior.page.totals))){this.pending=null;return this.result('unknown');}
   const ids=prior?.ids??new Set<string>(),keys=prior?.keys??new Set<string>(),cursors=prior?.cursors??new Set<string>();
   for(const item of page.entries){
    const namespace='namespace' in item?item.namespace:options.kind==='days'?'DAY':options.kind==='targets'?'TARGET':options.namespace!;
    const entry='entry' in item?item.entry:item,id=namespace+'/'+entry.id;
    const key=namespace==='DAY'?entry.local_day:entry.variant+'/'+entry.effective_from;
    if(ids.has(id)||['days','targets'].includes(options.kind)&&keys.has(key!)){this.pending=null;return this.result('unknown');}
    ids.add(id);keys.add(key!);
   }
   const merged={...page,entries:[...(prior?.page.entries??[]),...page.entries]};
   if(page.next_cursor===null){
    this.pending=null;
    if(options.kind==='days'&&!nutritionCoverageMatches(merged))return this.result('unknown');
    this.previous=merged;return this.result('confirmed',merged);
   }
   if(cursors.has(page.next_cursor)){this.pending=null;return this.result('unknown');}
   cursors.add(page.next_cursor);options={...options,cursor:page.next_cursor};
   this.pending={options,page:merged,ids,keys,cursors};
  }
  return this.result('partial',this.pending?.page??null);
 }
}

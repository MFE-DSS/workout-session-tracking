/** Headless, memory-only consumer of the approved chronology. No body UI or writer. */
import { AuthSession } from '../auth/authSession';
import { WeightHistoryClient, type WeightHistory, type WeightOutcome } from './weightHistory';
export type WeightResourceState = WeightOutcome | {state:'idle'|'pending'};
const copy = <T>(value:T):T => JSON.parse(JSON.stringify(value));
export class WeightHistoryResource {
  private value:WeightResourceState={state:'idle'};
  private revision:number;
  private sequence=0;
  private cursors=new Set<string>();
  private flight:Promise<WeightResourceState>|null=null;
  constructor(private readonly auth:AuthSession,private readonly client:WeightHistoryClient){this.revision=auth.revision;}
  get state():WeightResourceState{
    if(this.revision!==this.auth.revision){this.value={state:'idle'};this.revision=this.auth.revision;this.sequence++;this.flight=null;this.cursors.clear();}
    return copy(this.value);
  }
  refresh():Promise<WeightResourceState>{return this.read();}
  loadNext():Promise<WeightResourceState>{
    const state=this.state;
    if(this.flight)return this.flight;
    if(state.state!=='confirmed'||state.value.next_cursor===null)return Promise.resolve(state);
    return this.read(state.value.next_cursor,state.value);
  }
  private read(cursor?:string,previous?:WeightHistory):Promise<WeightResourceState>{
    void this.state;
    const revision=this.auth.revision,sequence=++this.sequence;
    if(!previous)this.cursors.clear();
    const cursors=new Set(this.cursors);if(cursor!==undefined)cursors.add(cursor);
    this.value={state:'pending'};
    const current=()=>revision===this.auth.revision&&sequence===this.sequence;
    const task:Promise<WeightResourceState>=this.client.read(cursor===undefined?{}:{cursor}).then((result):WeightResourceState=>{
      if(!current())return {state:'cancelled'};
      let next:WeightResourceState=result.state==='cancelled'?{state:'idle'}:result;
      if(result.state==='confirmed'&&previous){
        const incoming=result.value;
        const ids=new Set(previous.entries.map(e=>e.measurement_id));
        if(incoming.owner_id!==previous.owner_id||(incoming.next_cursor!==null&&cursors.has(incoming.next_cursor))||incoming.entries.some(e=>ids.has(e.measurement_id))){
          next={state:'unknown'};
        }else next={state:'confirmed',value:{...incoming,state:'AVAILABLE',entries:[...previous.entries,...incoming.entries]}};
      }
      this.cursors=cursors;
      this.value=copy(next);
      return this.state;
    }).catch(():WeightResourceState=>{
      if(!current())return {state:'cancelled'};
      this.value={state:'unknown'};
      return this.state;
    }).finally(()=>{if(this.flight===task)this.flight=null;});
    this.flight=task;
    return task;
  }
}

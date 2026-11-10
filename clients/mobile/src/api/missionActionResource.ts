/** Memory-only Today reads. Previous facts are display-only until re-confirmed. */
import { AuthSession } from '../auth/authSession';
import { jsonCopy } from './firstPlanV3';
import { MissionActionClient, type MissionAction, type MissionOutcome, type MissionPath } from './missionAction';

export type MissionResourceState = MissionOutcome | {state:'idle'} |
 {state:'pending';previous?:MissionAction} |
 (Exclude<MissionOutcome,{state:'confirmed'}|{state:'cancelled'|'unknown'}>&{previous?:MissionAction}) |
 {state:'unknown';previous?:MissionAction};

export class MissionActionResource {
 private value:MissionResourceState={state:'idle'};
 private generation:number;
 private sequence=0;
 private selected:MissionPath='FIRST_USE';
 private host:boolean;
 constructor(private readonly auth:AuthSession,private readonly client:MissionActionClient,host=false){
  this.generation=auth.revision;this.host=host;
 }
 private syncIdentity(){
  if(this.generation!==this.auth.revision){this.generation=this.auth.revision;this.selected='FIRST_USE';this.sequence++;this.value={state:'idle'};}
 }
 get path(){this.syncIdentity();return this.selected;}
 get state():MissionResourceState{this.syncIdentity();return jsonCopy(this.value);}
 invalidate(){this.syncIdentity();this.sequence++;this.value={state:'idle'};}
 selectPath(path:MissionPath){
  this.syncIdentity();if(path!=='FIRST_USE'&&path!=='HISTORICAL')throw Error('invalid_mission_path');
  if(path!==this.selected){this.selected=path;this.invalidate();}
 }
 setHost(host:boolean){
  if(typeof host!=='boolean')throw Error('invalid_mission_host');
  this.syncIdentity();if(this.host!==host){this.host=host;this.invalidate();}
 }
 async refresh():Promise<MissionResourceState>{
  const prior=this.state;
  const previous=prior.state==='confirmed'?prior.value:'previous' in prior?prior.previous:undefined;
  const generation=this.generation,sequence=++this.sequence,path=this.selected,host=this.host;
  const active=()=>generation===this.auth.revision&&sequence===this.sequence&&path===this.selected&&host===this.host;
  this.value=previous?{state:'pending',previous:jsonCopy(previous)}:{state:'pending'};
  try {
   const result=await this.client.read(path,host,active);
   if(!active())return{state:'cancelled'};
   if(result.state==='cancelled')this.value={state:'idle'};
   else if(result.state==='confirmed')this.value=jsonCopy(result);
   else this.value=previous?{...result,previous:jsonCopy(previous)}:result;
  }catch{
   if(!active())return{state:'cancelled'};
   this.value=previous?{state:'unknown',previous:jsonCopy(previous)}:{state:'unknown'};
  }
  return this.state;
 }
}

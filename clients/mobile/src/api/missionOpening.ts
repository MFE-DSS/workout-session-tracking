/** Selection guard only. The original journals/controllers remain command owners. */
import type {MissionAction} from './missionAction';
import type {MissionResourceState} from './missionActionResource';
export type LocalOpening={kind:'START'|'CLOSE'|'SOURCE'}|null;
export function localOpeningState(input:{legacyStartUnknown:boolean;closePending:boolean;v3:{intent:{state:string}|null;source:{pending?:unknown}}|null}):LocalOpening{
 if(input.legacyStartUnknown||input.v3?.intent?.state==='submitted'||input.v3?.intent?.state==='unknown')return{kind:'START'};
 if(input.closePending)return{kind:'CLOSE'};
 if(input.v3?.source.pending)return{kind:'SOURCE'};
 return null;
}
export function missionActionCurrent(action:MissionAction,read:MissionResourceState,local:LocalOpening):boolean{
 return local===null&&read.state==='confirmed'&&JSON.stringify(action)===JSON.stringify(read.value);
}

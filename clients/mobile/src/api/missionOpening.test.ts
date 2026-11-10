import {localOpeningState,missionActionCurrent} from './missionOpening';
import {firstUse,historical} from '../../test/missionActionHarness';
import {decodeMissionAction} from './missionAction';
const confirmed=()=>({state:'confirmed' as const,value:decodeMissionAction(firstUse(),7,'FIRST_USE',true)!});
test('durable V3 unknown start and source operations take priority over a recommendation',()=>{
 expect(localOpeningState({legacyStartUnknown:false,closePending:false,v3:{intent:{state:'unknown'},source:{pending:{}}}})).toEqual({kind:'START'});
 expect(localOpeningState({legacyStartUnknown:false,closePending:false,v3:{intent:{state:'created'},source:{pending:{}}}})).toEqual({kind:'SOURCE'});
 expect(localOpeningState({legacyStartUnknown:false,closePending:true,v3:null})).toEqual({kind:'CLOSE'});
});
test('an acknowledged or denied V3 request is not a fresh unresolved start',()=>{
 for(const state of ['created','denied','cancelled'])expect(localOpeningState({legacyStartUnknown:false,closePending:false,v3:{intent:{state},source:{}}})).toBeNull();
});
test('previous, changed selection and local uncertainty cannot authorize a stale pressed action',()=>{
 const r=confirmed();expect(missionActionCurrent(r.value,r,null)).toBe(true);
 expect(missionActionCurrent(r.value,{state:'pending',previous:r.value},null)).toBe(false);
 expect(missionActionCurrent(r.value,{state:'unknown',previous:r.value},null)).toBe(false);
 expect(missionActionCurrent(r.value,confirmed(),{kind:'SOURCE'})).toBe(false);
 expect(missionActionCurrent(r.value,{state:'confirmed',value:{...r.value,observed_at:'2026-11-10T20:00:00Z'}},null)).toBe(false);
 expect(missionActionCurrent(r.value,{state:'confirmed',value:decodeMissionAction(historical(),7,'HISTORICAL',true)!},null)).toBe(false);
});

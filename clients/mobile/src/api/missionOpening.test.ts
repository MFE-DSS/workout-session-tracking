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
test('legacy uncertainty occupies only the existing MISSION snapshot and has no replay command',()=>{
 const {markLegacyStart,legacyStartMarker,clearLegacyStart}=require('./missionOpening');
 const {initialState}=require('../domain/workout');const marked=markLegacyStart(initialState,'actual-template',123);
 expect(legacyStartMarker(marked)).toEqual({version:'legacy-start-uncertainty/1.0.0',template_slug:'actual-template',requested_at_ms:123});
 expect(clearLegacyStart(marked)).toEqual(initialState);expect(initialState.mission_opening).toBeUndefined();
 expect(()=>markLegacyStart({...initialState,phase:'SET'},'x',123)).toThrow();
});
test('a confirmed exclusion remains in the existing snapshot across an offline restart',()=>{
 const {blockLegacyResume,legacyResumeBlocked,clearLegacyResumeBlock}=require('./missionOpening');const {initialState}=require('../domain/workout');
 const state={...initialState,phase:'SET',plan:{session_id:11}};const blocked=blockLegacyResume(state);
 expect(legacyResumeBlocked(JSON.parse(JSON.stringify(blocked)))).toBe(true);expect(clearLegacyResumeBlock(blocked)).toEqual(state);
});

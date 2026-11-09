import {parseCalibrationMass,calibrationStage,calibrationUnit} from './calibrationModel';
test.each(['',' ', 'NaN','Infinity','-1','0x10','1e3','17kg'])('missing or ambiguous setting %s never becomes a suggested zero',value=>expect(parseCalibrationMass(value)).toBeNull());
test('decimal comma is an entered fact, with no per-implement conversion',()=>{expect(parseCalibrationMass('8,5')?.value).toBe(8.5);expect(calibrationUnit('PER_IMPLEMENT')).toBe('kg par haltère');expect(calibrationUnit('MACHINE_DISPLAY_KG')).toBe('kg affichés');});
test('new setting revokes trial view even if an old observation exists',()=>{expect(calibrationStage({allowed_actions:['CONFIRM_CONTEXT'],result:{state:'OBSERVED'},progress:{observed_attempt_count:1,preparation:{}}} as any)).toBe('decision');});
test('absence of current permission preserves history without granting instructions',()=>{expect(calibrationStage({allowed_actions:[],result:null,progress:{observed_attempt_count:1}} as any)).toBe('decision');});

test('an observed attempt resumes at decision so explicit retry is reachable',()=>{
 expect(calibrationStage({allowed_actions:['RECORD_TRIAL'],result:{state:'OBSERVED'},progress:{observed_attempt_count:1,preparation:{},setting_choice:{}}} as any)).toBe('decision');
});

import {parseCalibrationOccurrence,resumableCalibrationDraft} from './calibrationModel';
test('actual local date/time is validated without silently using entry time',()=>{
 expect(parseCalibrationOccurrence('2026-02-30','10:00')).toBeNull();expect(parseCalibrationOccurrence('','')).toBeNull();
 const value=parseCalibrationOccurrence('2026-11-08','09:17');expect(value).not.toBeNull();expect(new Date(value!).getDate()).toBe(8);expect(new Date(value!).getHours()).toBe(9);
});
test('unsent actual observations resume only for their owner-bound encounter',()=>{
 const draft={encounter_ref:'a',stage:'observation',reps:'7',completed:false,successful:null,quality:'UNKNOWN',discomfort:'NO_CONCERN',stopReason:'TIME_LIMIT',trialAt:'2026-11-08T08:17:00Z'};
 expect(resumableCalibrationDraft(draft,'a')).toEqual(draft);expect(resumableCalibrationDraft(draft,'b')).toBeNull();
});

test('after explicit retry the fresh server permission reaches trial despite prior OBSERVED state',()=>{
 expect(calibrationStage({allowed_actions:['INITIATE_TRIAL'],result:{state:'OBSERVED'},progress:{observed_attempt_count:1,preparation:{},setting_choice:{}}} as any)).toBe('trial');
});

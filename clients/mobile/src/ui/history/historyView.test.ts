import {weightGeometry,setFact,periodLabel} from './historyView';
import {weightPage} from '../../../test/accountDataHarness';
test('weight geometry uses measured dates, leaves invalid gaps and keeps one isolated point',()=>{
 const a=weightPage().entries[0],rows=[{...a,measurement_id:1,measured_at:'2026-11-01T00:00:00Z'}, {...a,measurement_id:2,measured_at:'2026-11-02T00:00:00Z',value:null,quality:'INVALID_NONFINITE' as const,raw_value_repr:'inf'}];
 expect(weightGeometry(rows,300,90)).toEqual([{id:1,x:150,y:45}]);expect(weightGeometry([],300,90)).toEqual([]);
});
test('typed settings stay machine display versus per implement, and missing facts never become prescriptions',()=>{
 expect(setFact({completed:true,reps:9,observation:{setting:{value:20},context:{load_semantics:'PER_IMPLEMENT'}}})).toBe('20 kg par haltère · 9 rép.');
 expect(setFact({completed:true,reps:10,observation:{setting:{value:17.5},context:{load_semantics:'MACHINE_DISPLAY_KG'}}})).toBe('17,5 kg affichés · 10 rép.');
 expect(setFact({completed:false,reps:null,observation:null})).toBe('Aucun fait enregistré');
 expect(setFact({completed:false,reps:4,weight_kg:null})).toBe('Charge inconnue · 4 rép. · non complétée');
});
test('period label retains explicit interval and timezone, all is not a fabricated start date',()=>{
 expect(periodLabel({period:'all',time_zone:'Europe/Paris',from:null,until:'2026-11-10T12:00:00Z'})).toContain('Europe/Paris');
 expect(periodLabel({period:'all',time_zone:'UTC',from:null,until:'2026-11-10T12:00:00Z'})).toContain('jusqu’au');
});
test('weight axes identify the exact plotted date/value extent without including invalid evidence',()=>{
 const {weightExtent}=require('./historyView'),a=weightPage().entries[0];
 expect(weightExtent([{...a,value:72.5,measured_at:'2026-11-01T00:00:00Z'},{...a,measurement_id:12,value:71.8,measured_at:'2026-11-09T00:00:00Z'},{...a,measurement_id:13,value:null,quality:'INVALID_NONFINITE',raw_value_repr:'inf'}])).toEqual({low:71.8,high:72.5,from:'2026-11-01T00:00:00Z',until:'2026-11-09T00:00:00Z'});
 expect(weightExtent([])).toBeNull();
});

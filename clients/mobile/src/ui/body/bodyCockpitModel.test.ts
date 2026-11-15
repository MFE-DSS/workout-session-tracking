import type {BodyEntry,BodyKey} from '../../api/bodyMeasurements';
import {bodyObservations,compareObservations,defaultObservation,chronology} from './bodyCockpitModel';
function entry(id:number,day:string,value:number|null,quality='KNOWN',state='CURRENT',precision='DAY_UTC_CONVENTION'):BodyEntry {
 return {root_ref:id,measurement_id:id,revision:1,state,date_precision:precision,measured_at:day+'T00:00:00',recorded_at:'2026-11-14T12:00:00',fields:{weight_kg:{value,quality,unit:'kg',raw_value_repr:null,provenance:{origin:'USER_DECLARED',acquisition:'MANUAL_ENTRY',source_ref:'body:'+id}}}} as BodyEntry;
}
const key:BodyKey='weight_kg';
test('current heads only; legacy and unknown dates stay readable, never plotted or compared',()=>{
 const rows=bodyObservations([entry(1,'2026-11-01',72),entry(2,'2026-11-02',800,'LEGACY_OUTSIDE_CURRENT_BOUNDS'),entry(3,'2026-11-03',71,'KNOWN','SUPERSEDED'),entry(4,'2026-11-04',70,'KNOWN','CURRENT','UNKNOWN')],key);
 expect(rows.map(r=>r.entry.measurement_id)).toEqual([1,2,4]);expect(chronology(rows,300,120).points.map(p=>p.observation.entry.measurement_id)).toEqual([1]);
 expect(compareObservations(rows[0],rows[1])).toBeNull();expect(compareObservations(rows[0],rows[2])).toBeNull();
});
test('same-day observations share x; no latest intraday fact is invented',()=>{
 const rows=bodyObservations([entry(1,'2026-11-09',72),entry(2,'2026-11-11',71.6),entry(3,'2026-11-11',71.4)],key),plot=chronology(rows,300,120);
 expect(plot.points[1].x).toBe(plot.points[2].x);expect(defaultObservation(rows)).toBeNull();
});
test('comparison is B minus A over exact calendar days, no favourable direction or automatic prior',()=>{
 const rows=bodyObservations([entry(1,'2026-11-09',72),entry(2,'2026-11-11',71.4)],key);
 expect(compareObservations(rows[0],rows[1])).toEqual({difference:-0.6,days:2,unit:'kg',from:'2026-11-09',through:'2026-11-11'});
 expect(compareObservations(rows[1],rows[0])).toBeNull();expect(compareObservations(rows[1],rows[1])).toBeNull();
});
test('only same field/unit compared; missing never zero',()=>{
 const row=bodyObservations([entry(1,'2026-11-01',72)],key)[0];
 expect(compareObservations(row,{...row,key:'waist_cm',entry:entry(2,'2026-11-02',73)})).toBeNull();
 expect(bodyObservations([entry(2,'2026-11-02',null,'MISSING')],key)).toEqual([]);
});
test('one exact latest day selected without server recording time',()=>{
 const rows=bodyObservations([entry(1,'2026-11-11',71.4),entry(2,'2026-11-09',72)],key);
 expect(defaultObservation(rows)?.entry.measurement_id).toBe(1);
});
test('one observation has point/scale, no invented trend or division by zero',()=>{
 const plot=chronology(bodyObservations([entry(1,'2026-11-11',71.4)],key),300,120);
 expect(plot.points).toHaveLength(1);expect(Number.isFinite(plot.points[0].x)).toBe(true);expect(Number.isFinite(plot.points[0].y)).toBe(true);expect(plot.ticks.length).toBeGreaterThan(1);
});

import React from 'react';
import type {BodyEntry,BodySpec} from '../../api/bodyMeasurements';
import {MeasurementCorrectionSheet} from './MeasurementCorrectionSheet';
import {AcquisitionInstrument} from './AcquisitionInstrument';
import type {BodyForm} from './measurementInputModel';
export {measurementValues,measurementLabel,type BodyForm} from './measurementInputModel';
export function MeasurementSheet(p:{specs:BodySpec[];initial?:BodyEntry;reference?:BodyEntry;busy:boolean;onSave:(form:BodyForm)=>void;onClose:()=>void}){
 return !p.initial&&p.specs.length===1?<AcquisitionInstrument {...p}/>:<MeasurementCorrectionSheet {...p}/>;
}

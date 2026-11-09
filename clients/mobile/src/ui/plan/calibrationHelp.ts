/** Verbatim, integrity-checked presentation of the existing procedure; never permission. */
import {CryptoDigestAlgorithm,digestStringAsync} from 'expo-crypto';
import type {CapabilitiesV3} from '../../domain/planV3Types';
import {compatibleCalibrationProfile,PILOT_CANDIDATE} from '../../api/calibrationProfilesV2';
export type CalibrationHelpStage='identify'|'setting'|'familiarization'|'trial'|'observation'|'decision'|'concern';
export type CalibrationHelpSection={id:string;title:string;text:string};
export type CalibrationHelpProjection={state:'available';source_ref:string;sha256:string;sections:CalibrationHelpSection[];primarySectionIds:string[]}
 |{state:'unavailable';reason:'PROCEDURE_UNAVAILABLE'};
const PILOT={source_ref:"docs/science/sci-p02-initial-policy/first-use-calibration-bootstrap/OPERATIONAL_PROTOCOL.md",sha256:"1fa83ccc817d98f15438b46c2e50d5ce475d6852d9a9a07cc3903c5bfab7a15f"};
const EXTENSIONS={source_ref:"docs/science/sci-p02-initial-policy/calibration-six-extensions/OPERATIONAL_PROTOCOL.md",sha256:"e85a2bf108a9afeaa15049b1233217b6c7dd98ecd2de78efa1cbe4b221add228"};
const PILOT_SECTIONS=['1. Ouvrir et identifier','2. Comprendre le dispositif et se familiariser','3. Essayer et observer','4. Décider','5. Préoccupation, retrait et limites','6. Vers le plan'];
const COMMON='Conditions communes et portée',SEQUENCE='Séquence réelle',STOP='Arrêt, réessai et retrait',LIMITS='Sources et frontière de preuve';
/** Includes every applicable common/stop section, with a stage focus; selection performs no mutation. */
export async function projectCalibrationHelp(caps:CapabilitiesV3|null,candidateId:string|null,stage:CalibrationHelpStage='identify'):Promise<CalibrationHelpProjection> {
 const unavailable:CalibrationHelpProjection={state:'unavailable',reason:'PROCEDURE_UNAVAILABLE'};
 const profile=candidateId===null?null:compatibleCalibrationProfile(candidateId);
 if(!caps||(candidateId!==null&&!profile))return unavailable;
 const isPilot=candidateId===PILOT_CANDIDATE||(candidateId===null&&!caps.calibration_inventory);
 const expected=isPilot?PILOT:EXTENSIONS;
 const material=isPilot?caps.calibration_protocol_material:caps.calibration_inventory?.protocol_material;
 if(!material||material.source_ref!==expected.source_ref||material.sha256!==expected.sha256||typeof material.text!=='string')return unavailable;
 try{if(await digestStringAsync(CryptoDigestAlgorithm.SHA256,material.text)!==expected.sha256)return unavailable;}catch{return unavailable;}
 const text=material.text;
 const headings=[...text.matchAll(/^## ([^\r\n]+)\r?$/gm)];
 const sections:CalibrationHelpSection[]=headings.map((m,i)=>({id:m[1],title:m[1],text:text.slice(m.index,headings[i+1]?.index??text.length)}));
 const required=isPilot?PILOT_SECTIONS:[COMMON,SEQUENCE,...['chest-press-machine','rowing-chest-supported','romanian-deadlift-halteres','tirage-poulie-haute-prise-neutre','elevations-laterales-machine','releves-mollets-debout-machine'],STOP,LIMITS];
 if(required.some(id=>sections.filter(s=>s.id===id).length!==1))return unavailable;
 const ids=isPilot?(candidateId===null?[PILOT_SECTIONS[0],PILOT_SECTIONS[4],PILOT_SECTIONS[5]]:PILOT_SECTIONS)
  :candidateId===null?[COMMON,STOP,LIMITS]:[COMMON,SEQUENCE,candidateId,STOP,LIMITS];
 const primary=candidateId===null?(isPilot?(stage==='concern'?4:0):(stage==='concern'?STOP:COMMON)):isPilot?(stage==='identify'?0:['setting','familiarization'].includes(stage)?1:['trial','observation'].includes(stage)?2:stage==='decision'?3:4)
  :stage==='concern'?STOP:stage==='identify'?COMMON:stage==='decision'?SEQUENCE:candidateId??COMMON;
 return {state:'available',source_ref:material.source_ref,sha256:material.sha256,sections:ids.map(id=>sections.find(s=>s.id===id)!),primarySectionIds:[isPilot?PILOT_SECTIONS[primary as number]:primary as string].filter(id=>ids.includes(id))};
}

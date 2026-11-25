import React,{act} from 'react';
import {createRoot,type Root} from 'test-renderer';
import {historical} from '../../../test/missionActionHarness';
import {decodeMissionAction,type HistoricalMission} from '../../api/missionAction';
import {MissionCockpitScreen} from './MissionCockpitScreen';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
let root:Root;
beforeEach(()=>{root=createRoot();});
afterEach(async()=>{await act(async()=>root.unmount());});
function fixture():HistoricalMission {
 const base=historical(),raw={...base,payload:{...base.payload,scope:{exercise_count:7,work_set_count:21,first_exercise:{name:'Développé synthétique',set_scheme:'3x 8-12'}}}};
 const value=decodeMissionAction(raw,7,'HISTORICAL',true);
 if(value?.state!=='HISTORICAL_READY')throw Error('invalid canonical synthetic testimony');
 return value.payload;
}
const byId=(id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0]?.props;
const content=()=>root.container.queryAll((n:any)=>typeof n.props.children==='string').map((n:any)=>n.props.children).join(' ');
async function press(id:string){const p=byId(id);expect(p).toBeDefined();await act(async()=>p.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1}));}
function ports(){return{onStart:jest.fn(),onOpenLab:jest.fn(),onSecondaryOpened:jest.fn()};}
test('preparation reveals only the received first movement without starting or logging another action',async()=>{
 const mission=fixture(),p=ports();await act(async()=>root.render(React.createElement(MissionCockpitScreen,{mission,...p})));
 expect(content()).toContain('Server phrase');
 const labels=root.container.queryAll((n:any)=>n.props.accessibilityLabel).map((n:any)=>n.props.accessibilityLabel);
 expect(labels).toContain('21 séries de travail');expect(labels).toContain('7 exercices');
 expect(byId('mission-preparation-content')).toBeUndefined();
 await press('mission-prepare');expect(content()).toContain('Développé synthétique');expect(content()).toContain('3 × 8–12');
 expect(byId('start').accessibilityLabel).toBe('Démarrer');
 expect(p.onStart).not.toHaveBeenCalled();expect(p.onSecondaryOpened).not.toHaveBeenCalled();
 await press('mission-prepare');expect(byId('mission-preparation-content')).toBeUndefined();
 await press('start');expect(p.onStart).toHaveBeenCalledWith('test-template');
});
test('null explanation metadata and unknown zones never become a measured or recovered claim',async()=>{
 const mission=fixture();mission.zones=[{zone:'unmapped-test',label:'Unknown source zone'}];
 await act(async()=>root.render(React.createElement(MissionCockpitScreen,{mission,...ports()})));
 expect(byId('mission-zones')).toBeUndefined();expect(content()).not.toMatch(/Mesuré|null|récupér|disponibilité musculaire/i);
 await press('mission-why');expect(content()).not.toContain('14 jours');
});
test('a new source identity closes previous preparation and dispatches only the new exact slug',async()=>{
 const p=ports(),mission=fixture();await act(async()=>root.render(React.createElement(MissionCockpitScreen,{mission,...p})));
 await press('mission-prepare');
 const next={...mission,template:{...mission.template,slug:'next-template',name:'Autre séance'},scope:{...mission.scope,first_exercise:{name:'Autre mouvement',set_scheme:null}}};
 await act(async()=>root.render(React.createElement(MissionCockpitScreen,{mission:next,...p})));
 expect(byId('mission-preparation-content')).toBeUndefined();expect(content()).not.toContain('Développé synthétique');
 await press('start');expect(p.onStart.mock.calls).toEqual([['next-template']]);
});
test('busy historical control cannot dispatch primary or alternative starts',async()=>{
 const mission=fixture(),p=ports();mission.alternatives=[{slug:'other',name:'Alternative exacte',phrase:'Autre raison',executable:true}];
 await act(async()=>root.render(React.createElement(MissionCockpitScreen,{mission,busy:true,...p})));
 expect(byId('start').accessibilityState.disabled).toBe(true);
 await press('start');await press('mission-why');await press('mission-alternative-other');expect(p.onStart).not.toHaveBeenCalled();
});
test('alternative retains its executable permission and exact source slug',async()=>{
 const mission=fixture(),p=ports();mission.alternatives=[{slug:'other',name:'Alternative exacte',phrase:'Autre raison',executable:true},{slug:'blocked',name:'Non lançable',phrase:'Source limitée',executable:false}];
 await act(async()=>root.render(React.createElement(MissionCockpitScreen,{mission,...p})));
 await press('mission-why');expect(p.onSecondaryOpened).toHaveBeenCalledTimes(1);
 await press('mission-alternative-blocked');expect(p.onStart).not.toHaveBeenCalled();
 await press('mission-alternative-other');expect(p.onStart.mock.calls).toEqual([['other']]);
});
test('a limiting fact already carried by the server explanation is not repeated in disclosure',async()=>{
 const mission=fixture();mission.reason.reasons=['Server phrase','Mais Quadriceps : déjà servi.'];mission.reason.limiting=['Quadriceps : déjà servi.'];
 await act(async()=>root.render(React.createElement(MissionCockpitScreen,{mission,...ports()})));await press('mission-why');
 expect(content().split('Quadriceps : déjà servi.').length-1).toBe(1);
});
test('a repeated server zone cannot draw two windows for the same location',async()=>{
 const mission=fixture();mission.zones=[{zone:'pecs',label:'Pectoraux'},{zone:'pecs',label:'Pectoraux'},{zone:'unmapped',label:'Absent'}];
 await act(async()=>root.render(React.createElement(MissionCockpitScreen,{mission,...ports()})));
 expect(root.container.queryAll((n:any)=>n.props.testID==='window-bodymap')).toHaveLength(1);
});

test('template novelty is scoped to its retained completed history, never to all muscles',async()=>{
 const mission=fixture();mission.reason.phrase='Jamais fait.';
 await act(async()=>root.render(React.createElement(MissionCockpitScreen,{mission,...ports()})));
 expect(content()).toContain('Ce modèle de séance : aucun passage terminé retrouvé.');
 expect(content()).not.toContain('Jamais fait.');
 await press('mission-why');
 expect(content()).toContain('Explication héritée — couverture et récupération non qualifiées');
 expect(content()).toContain('Jamais fait.');
 expect(content()).toContain('Séances terminées retenues ; identité du modèle, sans preuve sur ses muscles.');
});
test('legacy measured and horizon labels describe mapped recorded work without claiming physiological measurement or dated bounds',async()=>{
 const mission=fixture();mission.reason.provenance='mesurée';mission.reason.horizon='14 derniers jours';
 await act(async()=>root.render(React.createElement(MissionCockpitScreen,{mission,...ports()})));
 await press('mission-why');
 expect(content()).toContain('Séries de travail complétées enregistrées · 14 derniers jours');
 expect(content()).toContain('Fenêtre du moteur sur la date de début des séances ; bornes datées non fournies par cette lecture.');
 expect(content()).toContain('Cartographie dans l’historique retenu : aucune zone inconnue signalée par le moteur.');
 expect(content()).not.toMatch(/(?:^| )mesurée(?: |$)/);
 expect(content()).toContain('Aucune disponibilité musculaire qualifiée.');
});

test('partial novelty keeps its source uncertainty for the selected model and alternative',async()=>{
 const mission=fixture(),suffix=' Lecture partielle : un exercice n’a pas pu être classé.';
 mission.reason.phrase='Jamais fait.'+suffix;mission.reason.provenance='partielle';
 mission.alternatives=[{slug:'partial',name:'Modèle partiel',phrase:'Jamais fait.'+suffix,executable:true}];
 await act(async()=>root.render(React.createElement(MissionCockpitScreen,{mission,...ports()})));
 expect(content()).toContain('Ce modèle de séance : aucun passage terminé retrouvé.'+suffix);
 expect(content()).not.toContain('Jamais fait.');
 await press('mission-why');
 expect(content()).toContain('Cartographie partielle dans l’historique retenu : au moins un exercice non classé.');
 expect(content()).toContain('Trace de l’alternative : Jamais fait.'+suffix);
});

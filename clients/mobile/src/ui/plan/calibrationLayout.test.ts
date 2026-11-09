import React,{act} from 'react';
import {createRoot} from 'test-renderer';
import {readFileSync} from 'fs';
import {resolve} from 'path';
import {createHash} from 'crypto';
import {PlanV3FirstUseScreen} from './PlanV3FirstUseScreen';
import {FirstUseV3Controller} from '../../api/firstUseV3';
import {BackHandler,Keyboard} from 'react-native';
jest.mock('react-native-safe-area-context',()=>({useSafeAreaInsets:()=>({top:47,bottom:34,left:0,right:0})}));
jest.mock('expo-crypto',()=>({CryptoDigestAlgorithm:{SHA256:'SHA-256'},digestStringAsync:async(_algorithm:string,text:string)=>require('crypto').createHash('sha256').update(text).digest('hex')}));
const source_ref='docs/science/sci-p02-initial-policy/calibration-six-extensions/OPERATIONAL_PROTOCOL.md';
const text=readFileSync(resolve(__dirname,'../../../../../',source_ref),'utf8');
const profiles=[{candidate_id:'chest-press-machine',display_name:'Chest press',realization_ref:'machine',initial_guidance_supported:true,load_semantics:'MACHINE_DISPLAY_KG'}, {candidate_id:'romanian-deadlift-halteres',display_name:'Soulevé de terre',realization_ref:'dumbbells',initial_guidance_supported:true,load_semantics:'PER_IMPLEMENT'}];
const caps=()=>({controlled_test_available:true,supported_realizations:profiles,calibration_inventory:{protocol_material:{source_ref,text,sha256:createHash('sha256').update(text).digest('hex')}}});
const blank={encounter_ref:'owned',draft_ref:'fact',stage:'observation',candidate:'chest-press-machine',place:'room',device:'A',instruction:'manual',setup:'seat',load:'17',observedLoad:'',reps:'',completed:null,successful:'UNSET',quality:null,discomfort:null,stopReason:null,trialAt:'',trialDate:'',trialTime:''};
function controller(draft?:any){return {active:true,loading:false,notice:null,state:{owner_id:1,source:{encounter_ref:'owned',...(draft?{calibration_draft:draft}:{})}},capabilities:caps(),saveCalibrationDraft:async()=>{},calibrationDraft:()=>draft??null,newCalibrationDraftRef:()=> 'fact',readCalibration:async()=>{},recordCalibration:async(_o:any)=>true,encounter:{encounter_ref:'owned',source_revision:'rev',result:{state:'SUPPORTED_INITIAL_EXPLORATION',phase:'TRIAL'},allowed_actions:['RECORD_TRIAL'],progress:{context:{canonical_exercise_id:'chest-press-machine',equipment_ref:'A',context_ref:'room',load_semantics:'MACHINE_DISPLAY_KG'},preparation:{},setting_choice:{setting:{kind:'MASS_KG',unit:'kg',value:17}},observations:[],observed_attempt_count:0}}} as any;}
const click=async(node:any)=>act(async()=>{node.props.onClick({nativeEvent:{},stopPropagation(){},currentTarget:1,target:1});});
const byId=(root:any,id:string)=>root.container.queryAll((n:any)=>n.props.testID===id)[0];
const byLabel=(root:any,label:string)=>root.container.queryAll((n:any)=>n.props.accessibilityLabel===label)[0];
async function mount(c:any){const root=createRoot();await act(async()=>root.render(React.createElement(PlanV3FirstUseScreen,{controller:c,onExit(){},onPreferences(){}})));return root;}
async function resume(root:any){await click(byId(root,'plan-v3-resume-calibration'));}

test('entry gives the owned encounter the single compact priority and keeps management under details',async()=>{
 const root=await mount(controller());
 expect(root.container.queryAll((n:any)=>n.props.testID==='calibration-primary-action')).toHaveLength(1);
 expect(byId(root,'plan-v3-resume-calibration').props.accessibilityLabel).toBe('Reprendre');
 expect(root.container.queryAll((n:any)=>n.props.children==='Observations conservées')).toHaveLength(0);
 expect(root.container.queryAll((n:any)=>n.props.children==='Rencontre conservée')).toHaveLength(1);
 expect(byId(root,'plan-v3-open-proposal')).toBeUndefined();
 await click(byId(root,'calibration-entry-details'));
 expect(byId(root,'plan-v3-open-proposal')).toBeDefined();
 await act(async()=>root.unmount());
});
test('observation has two local sections, no positive defaults, and sends the same explicit facts only on save',async()=>{
 const c=controller({...blank}),reported:any[]=[];c.recordCalibration=async(o:any)=>{reported.push(o);return true;};
 const root=await mount(c);await resume(root);
 expect(byLabel(root,'Continuer').props.accessibilityState.disabled).toBe(true);
 expect(byLabel(root,'Enregistrer ces faits')).toBeUndefined();
 expect(byLabel(root,'Contrôle acceptable rapporté')).toBeUndefined();
 await act(async()=>byId(root,'calibration-setting-input').props.onChangeText('18'));
 await act(async()=>byLabel(root,'Répétitions réellement faites').props.onChangeText('7'));
 await click(byLabel(root,'Essai interrompu'));await click(byLabel(root,'Réussite inconnue'));
 await click(byLabel(root,'Continuer'));
 expect(reported).toEqual([]);
 expect(byLabel(root,'Enregistrer ces faits').props.accessibilityState.disabled).toBe(true);
 await click(byLabel(root,'Contrôle inconnu'));await click(byLabel(root,'Gêne inconnue'));await click(byLabel(root,'Limite de temps'));
 await click(byLabel(root,'Indiquer une date et une heure'));
 await act(async()=>byLabel(root,'Date de l’essai').props.onChangeText('2026-11-08'));
 await act(async()=>byLabel(root,'Heure de l’essai').props.onChangeText('09:17'));
 await click(byId(root,'account-back'));
 expect(byId(root,'calibration-setting-input').props.value).toBe('18');
 await click(byLabel(root,'Continuer'));await click(byLabel(root,'Enregistrer ces faits'));
 expect(reported).toEqual([{kind:'CALIBRATION_EVENT_REPORTED',stop_reason:'TIME_LIMIT',event:{kind:'ATTEMPT_OBSERVED',setting:{kind:'MASS_KG',unit:'kg',value:18},reps:7,completed:false,successful:null,technique:'UNKNOWN',discomfort:'UNKNOWN',occurred_at:new Date(2026,10,8,9,17).toISOString()}}]);
 await act(async()=>root.unmount());
});
test.each([undefined,'feeling'])('old and new complete trial drafts resume at feeling without renewing the occurrence (%s)',async(observationSection)=>{
 const draft={...blank,observedLoad:'8',reps:'10',completed:true,successful:false,quality:'UNKNOWN',trialAt:'2026-11-08T08:17:00Z',...(observationSection?{observationSection}:{})};
 const root=await mount(controller(draft));await resume(root);
 expect(byLabel(root,'Enregistrer ces faits')).toBeDefined();
 expect(byId(root,'calibration-occurrence').props.children).toEqual(['Heure indiquée : ',new Date('2026-11-08T08:17:00Z').toLocaleString()]);
 expect(byLabel(root,'Contrôle inconnu').props.accessibilityState.selected).toBe(true);
 await click(byId(root,'account-back'));expect(byId(root,'calibration-setting-input').props.value).toBe('8');
 await act(async()=>root.unmount());
});
test('an exact committed receipt takes priority over a restored local observation substep',async()=>{
 const c=controller({...blank,observedLoad:'17',reps:'10',completed:true,successful:true,observationSection:'feeling',committed_event_ref:'accepted-fact'}),root=await mount(c);await resume(root);
 expect(byLabel(root,'Enregistrer ces faits')).toBeUndefined();expect(byLabel(root,'Continuer')).toBeUndefined();
 await act(async()=>root.unmount());
});
test('help is applicable before opening, has verbatim stop sections, and never opens or acknowledges an encounter',async()=>{
 const c=controller(),commands:any[]=[];c.openCalibration=async(...args:any[])=>commands.push(args);c.recordCalibration=async(o:any)=>commands.push(o);
 const root=await mount(c);await click(byId(root,'plan-v3-first-calibration'));await click(byLabel(root,'Chest press'));await click(byId(root,'calibration-help-open'));
 expect(root.container.queryAll((n:any)=>n.props.testID==='calibration-help-section').map((n:any)=>n.props.children).every((s:string)=>text.includes(s))).toBe(true);
 expect(root.container.queryAll((n:any)=>n.props.children===text.slice(text.indexOf('## Arrêt, réessai et retrait'),text.indexOf('## Sources et frontière de preuve')))).toHaveLength(1);
 expect(commands).toEqual([]);
 await click(byId(root,'calibration-help-close'));
 await click(byLabel(root,'Soulevé de terre'));await click(byId(root,'calibration-help-open'));
 const sections=root.container.queryAll((n:any)=>n.props.testID==='calibration-help-section').map((n:any)=>n.props.children);
 expect(sections.some((s:string)=>s.startsWith('## romanian-deadlift-halteres'))).toBe(true);
 expect(sections.some((s:string)=>s.startsWith('## chest-press-machine'))).toBe(false);
 expect(commands).toEqual([]);await act(async()=>root.unmount());
});

test('a pending operation and its reconciliation stay visible outside details',async()=>{
 const c=controller();c.state.source.pending={kind:'calibration-event',request_id:'same'};c.retryPendingExplicitly=async()=>{};c.load=async()=>{};
 const root=await mount(c);expect(byId(root,'plan-v3-read-sources')).toBeDefined();expect(byLabel(root,'Répéter explicitement la même action')).toBeDefined();
 expect(byId(root,'plan-v3-resume-calibration')).toBeUndefined();
 expect(root.container.queryAll((n:any)=>n.props.testID==='calibration-primary-action')).toHaveLength(1);
 expect(byId(root,'plan-v3-open-proposal')).toBeUndefined();await act(async()=>root.unmount());
});
test('late integrity result cannot display an old candidate or an expired owner help',async()=>{
 let finish!:(value:string)=>void;
 const digest=jest.spyOn(require('expo-crypto'),'digestStringAsync').mockImplementationOnce(()=>new Promise<string>(done=>{finish=done;}));
 const c=controller(),root=await mount(c);await click(byId(root,'plan-v3-first-calibration'));await click(byLabel(root,'Chest press'));await click(byId(root,'calibration-help-open'));
 await click(byId(root,'calibration-help-close'));await click(byLabel(root,'Soulevé de terre'));c.active=false;
 await act(async()=>{finish(createHash('sha256').update(text).digest('hex'));});
 expect(root.container.queryAll((n:any)=>n.props.testID==='calibration-help-section')).toHaveLength(0);
 digest.mockRestore();await act(async()=>root.unmount());
});
test('withdrawal preserves historical facts and past-fact entry without restoring a physical instruction',async()=>{
 const c=controller();c.encounter.result={state:'WITHDRAWN',phase:'DECIDE'};c.encounter.progress.observations=[{event_id:'past',reps:7,setting:{kind:'MASS_KG',unit:'kg',value:8},technique:'UNKNOWN',discomfort:'UNKNOWN'}];
 const root=await mount(c);await resume(root);
 expect(byLabel(root,'Pause · conserver mes observations')).toBeDefined();expect(byLabel(root,'Retirer le guidage')).toBeDefined();
 expect(byId(root,'plan-v3-loaded-trial')).toBeUndefined();expect(byLabel(root,'Accepter ce réglage provisoire exact')).toBeUndefined();
 await click(byLabel(root,'Historique'));expect(root.container.queryAll((n:any)=>n.props.children==='7 répétitions rapportées')).toHaveLength(1);
 await click(byLabel(root,'Noter un essai déjà réalisé'));expect(byId(root,'calibration-setting-input').props.value).toBe('');expect(byLabel(root,'Continuer').props.accessibilityState.disabled).toBe(true);
 await act(async()=>root.unmount());
});

test('leaving an in-flight resume cannot reopen the encounter on a late response',async()=>{
 const c=controller();let finish!:()=>void;c.readCalibration=()=>new Promise<void>(done=>{finish=done;});
 const root=await mount(c);await click(byId(root,'plan-v3-resume-calibration'));await click(byId(root,'account-back'));
 await act(async()=>finish());
 expect(byId(root,'plan-v3-resume-calibration')).toBeDefined();expect(byId(root,'calibration-instrument')).toBeUndefined();
 await act(async()=>root.unmount());
});

test('keyboard dismissal precedes local back and never sends an observation',async()=>{
 const listeners:Record<string,()=>void>={},add=jest.spyOn(Keyboard,'addListener').mockImplementation(((event:string,fn:()=>void)=>{listeners[event]=fn;return {remove(){}};}) as any),dismiss=jest.spyOn(Keyboard,'dismiss').mockImplementation(()=>{});
 const c=controller({...blank,observationSection:'feeling'}),reported:any[]=[];c.recordCalibration=async(o:any)=>{reported.push(o);return true;};
 const root=await mount(c);await resume(root);listeners.keyboardDidShow();await click(byId(root,'account-back'));
 expect(dismiss).toHaveBeenCalledTimes(1);expect(byLabel(root,'Enregistrer ces faits')).toBeDefined();
 listeners.keyboardDidHide();await click(byId(root,'account-back'));expect(byLabel(root,'Continuer')).toBeDefined();expect(reported).toEqual([]);
 await act(async()=>root.unmount());add.mockRestore();dismiss.mockRestore();
});
test('real controller retains both local sections across restart and closes the exact draft on a lost response receipt',async()=>{
 let stored:any=null,ids=0,recorded=0;
 const journal:any={history:async()=>[],read:async()=>stored,claim:async(s:any)=>{stored=structuredClone(s);return true;},save:async(s:any)=>{stored=structuredClone(s);}};
 const capabilities=caps(),view={...controller().encounter,result:null,authority:null,allowed_actions:[]};
 const ports:any={ownerId:1,journal,current:()=>true,newId:()=>`id-${++ids}`,sessions:{handoff:async()=>({state:'confirmed',value:{handoff:null}})},plan:{capabilities:async()=>({state:'confirmed',value:capabilities})},blueprint:{read:async()=>({state:'confirmed',value:{source_revision:2,receipts:{sources:[],snapshots:[],evaluations:[]}}})},calibration:{read:async()=>({state:'confirmed',value:view}),record:async()=>{recorded++;return {state:'unknown'};}}};
 const first=new FirstUseV3Controller(ports);await first.restore();
 stored={...stored,source:{encounter_ref:'owned',declarations:{source_revision:1}}};await first.restore();
 await first.saveCalibrationDraft({...blank,observedLoad:'8',reps:'7',completed:false,successful:null,quality:'UNKNOWN',discomfort:'UNKNOWN',stopReason:'TIME_LIMIT',trialAt:'2026-11-08T08:17:00Z',observationSection:'feeling'});
 const c=new FirstUseV3Controller(ports);await c.restore();c.capabilities=capabilities as any;
 const root=await mount(c);await resume(root);
 expect(byLabel(root,'Enregistrer ces faits').props.accessibilityState.disabled).toBe(false);
 await click(byLabel(root,'Enregistrer ces faits'));expect(recorded).toBe(1);
 const pending=c.state!.source.pending as any;
 ports.blueprint.read=async()=>({state:'confirmed',value:{source_revision:2,receipts:{sources:[{request_id:pending.request_id,event_ref:'actual-event',kind:'CALIBRATION_EVENT_REPORTED',source_revision:2}],snapshots:[],evaluations:[]}}});
 await act(async()=>{await c.load();await root.render(React.createElement(PlanV3FirstUseScreen,{controller:c,onExit(){},onPreferences(){}}));});
 expect(c.calibrationDraft('owned')).toMatchObject({observationSection:'feeling',committed_event_ref:'actual-event',stage:'decision',observedLoad:'8',successful:null,trialAt:'2026-11-08T08:17:00Z'});
 expect(byLabel(root,'Enregistrer ces faits')).toBeUndefined();expect(recorded).toBe(1);
 await act(async()=>root.unmount());
});

test('returning from another candidate keeps the owned encounter identity at entry',async()=>{
 const root=await mount(controller());await click(byId(root,'plan-v3-first-calibration'));await click(byLabel(root,'Soulevé de terre'));await click(byId(root,'account-back'));
 expect(root.container.queryAll((n:any)=>n.props.children==='Chest press')).toHaveLength(1);
 expect(root.container.queryAll((n:any)=>n.props.children==='Soulevé de terre')).toHaveLength(0);
 await act(async()=>root.unmount());
});

test('R1 hardware back leaves choose locally then yields at entry to the shell',async()=>{
 let hardwareBack!:Parameters<typeof BackHandler.addEventListener>[1];
 const listener=jest.spyOn(BackHandler,'addEventListener').mockImplementation((_event,callback)=>{hardwareBack=callback;return {remove(){}};});
 const root=await mount(controller());await click(byId(root,'plan-v3-first-calibration'));
 await act(async()=>{expect(hardwareBack({type:'hardwareBackPress',timeStamp:1})).toBe(true);});
 expect(byId(root,'plan-v3-resume-calibration')).toBeDefined();
 await act(async()=>{expect(hardwareBack({type:'hardwareBackPress',timeStamp:2})).toBe(false);});
 expect(byId(root,'calibration-instrument')).toBeUndefined();
 await act(async()=>root.unmount());listener.mockRestore();
});
test('R2 leaving a pending history selection cannot reopen its encounter after select resolves',async()=>{
 const c=controller();c.state.source.declarations={observation_progress:[{kind:'CALIBRATION_ENCOUNTER_OPENED',episode_ref:'history',context:{canonical_exercise_id:'chest-press-machine',equipment_ref:'History A'}}]};
 let finish!:(value:boolean)=>void;c.selectCalibration=()=>new Promise<boolean>(done=>{finish=done;});
 const root=await mount(c);await click(byId(root,'plan-v3-first-calibration'));await click(byLabel(root,'Chest press'));
 await click(byLabel(root,'Reprendre · History A'));await click(byId(root,'account-back'));await act(async()=>finish(true));
 expect(byId(root,'plan-v3-resume-calibration')).toBeDefined();expect(byId(root,'calibration-instrument')).toBeUndefined();
 await act(async()=>root.unmount());
});
test('R2 leaving a pending context opening cannot reopen pilot after the response',async()=>{
 const c=controller();c.state.source.declarations={blueprint:{population_scope:{value:'ADULT_NON_CLINICAL'},limitations:{state:'KNOWN',value:[]}}};
 let finish!:()=>void;c.openCalibration=()=>new Promise<void>(done=>{finish=done;});
 const root=await mount(c);await click(byId(root,'plan-v3-first-calibration'));await click(byLabel(root,'Chest press'));await click(byLabel(root,'Préparer ce mouvement'));
 await act(async()=>byLabel(root,'Lieu ou contexte').props.onChangeText('room'));
 await act(async()=>byLabel(root,'Appareil précis').props.onChangeText('A'));
 await click(byLabel(root,'Confirmer ce contexte'));await click(byId(root,'account-back'));await act(async()=>finish());
 expect(byLabel(root,'Préparer ce mouvement')).toBeDefined();expect(byId(root,'calibration-instrument')).toBeUndefined();
 await act(async()=>root.unmount());
});
test('R2 candidate changes respect the existing busy gate',async()=>{
 const c=controller(),root=await mount(c);await click(byId(root,'plan-v3-first-calibration'));c.loading=true;
 await act(async()=>root.render(React.createElement(PlanV3FirstUseScreen,{controller:c,onExit(){},onPreferences(){}})));
 expect(byLabel(root,'Chest press').props.accessibilityState.disabled).toBe(true);
 await act(async()=>root.unmount());
});
function expectBeforeHelp(root:any,labels:string[]){
 const traversal=root.container.queryAll((n:any)=>typeof n.props.accessibilityLabel==='string').map((n:any)=>n.props.accessibilityLabel);
 const help=traversal.indexOf('Aide');expect(help).toBeGreaterThanOrEqual(0);
 for(const label of labels){expect(traversal.indexOf(label)).toBeGreaterThanOrEqual(0);expect(traversal.indexOf(label)).toBeLessThan(help);}
}
test('R3 choose and minimum traverse choices and required action before help',async()=>{
 const root=await mount(controller());await click(byId(root,'plan-v3-first-calibration'));
 expectBeforeHelp(root,['Chest press','Préparer ce mouvement','Détails']);
 await click(byLabel(root,'Chest press'));await click(byLabel(root,'Préparer ce mouvement'));
 expectBeforeHelp(root,['Je déclare être adulte, dans un cadre non clinique','Je ne déclare aucune limitation','Continuer','Détails']);
 await act(async()=>root.unmount());
});
test('R3 context traverses required fields choices and action before help',async()=>{
 const c=controller();c.state.source.declarations={blueprint:{population_scope:{value:'ADULT_NON_CLINICAL'},limitations:{state:'KNOWN',value:[]}}};
 const root=await mount(c);await click(byId(root,'plan-v3-first-calibration'));await click(byLabel(root,'Chest press'));await click(byLabel(root,'Préparer ce mouvement'));
 expectBeforeHelp(root,['Lieu ou contexte','Appareil précis','Dispositif disponible','Confirmer ce contexte','Détails']);
 await act(async()=>root.unmount());
});
test('R3 encounter traverses mandatory inputs action and secondary controls before help',async()=>{
 const root=await mount(controller({...blank}));await resume(root);
 expectBeforeHelp(root,['Réglage réellement utilisé · kg affichés','Répétitions réellement faites','Essai terminé','Continuer','Pause · conserver mes observations','Détails']);
 await act(async()=>root.unmount());
});
test('R2 a newer candidate selection invalidates an earlier pending history resume',async()=>{
 const c=controller();c.state.source.declarations={observation_progress:[{kind:'CALIBRATION_ENCOUNTER_OPENED',episode_ref:'history',context:{canonical_exercise_id:'chest-press-machine',equipment_ref:'History A'}}]};
 let finish!:(value:boolean)=>void;c.selectCalibration=()=>new Promise<boolean>(done=>{finish=done;});
 const root=await mount(c);await click(byId(root,'plan-v3-first-calibration'));await click(byLabel(root,'Chest press'));
 await click(byLabel(root,'Reprendre · History A'));await click(byLabel(root,'Soulevé de terre'));await act(async()=>finish(true));
 expect(byLabel(root,'Soulevé de terre').props.accessibilityState.selected).toBe(true);expect(byId(root,'calibration-instrument')).toBeUndefined();
 await act(async()=>root.unmount());
});
test('R2 uninterrupted history selection and read still resume the owned encounter',async()=>{
 const c=controller();c.state.source.declarations={observation_progress:[{kind:'CALIBRATION_ENCOUNTER_OPENED',episode_ref:'history',context:{canonical_exercise_id:'chest-press-machine',equipment_ref:'History A'}}]};
 c.selectCalibration=async()=>true;
 const root=await mount(c);await click(byId(root,'plan-v3-first-calibration'));await click(byLabel(root,'Chest press'));await click(byLabel(root,'Reprendre · History A'));
 expect(byId(root,'calibration-instrument')).toBeDefined();expect(byLabel(root,'Pause · conserver mes observations')).toBeDefined();
 await act(async()=>root.unmount());
});
test.each(['fresh','legacy'])('native fix: real draft writer accepts %s mount and resume when observationSection is absent',async(kind)=>{
 let stored:any=null,ids=0;
 const journal:any={history:async()=>[],read:async()=>stored,claim:async(s:any)=>{stored=structuredClone(s);return true;},save:async(s:any)=>{stored=structuredClone(s);}};
 const view={...controller().encounter,result:null,authority:null,allowed_actions:[]};
 const ports:any={ownerId:1,journal,current:()=>true,newId:()=>`native-${++ids}`,sessions:{},plan:{},blueprint:{},calibration:{read:async()=>({state:'confirmed',value:view})}};
 const first=new FirstUseV3Controller(ports);await first.restore();stored={...stored,source:{encounter_ref:'owned'}};await first.restore();
 if(kind==='legacy')await first.saveCalibrationDraft({...blank,observedLoad:'8',reps:'7',completed:false,successful:null,quality:'UNKNOWN',discomfort:'UNKNOWN',stopReason:'TIME_LIMIT',trialAt:'2026-11-08T08:17:00Z'});
 const c=new FirstUseV3Controller(ports);await c.restore();c.capabilities=caps() as any;
 const root=await mount(c);
 expect(stored.source.calibration_draft).toBeDefined();
 expect(stored.source.calibration_draft.encounter_ref).toBeNull();
 expect(Object.hasOwn(stored.source.calibration_draft,'observationSection')).toBe(false);
 expect(root.container.queryAll((n:any)=>typeof n.props.children==='string'&&n.props.children.includes('Ton brouillon reste à vérifier'))).toHaveLength(0);
 await resume(root);
 const saved=c.calibrationDraft('owned') as any;
 expect(saved.observationSection).toBe(kind==='legacy'?'feeling':'trial');
 expect(saved.trialAt).toBe(kind==='legacy'?'2026-11-08T08:17:00Z':'');
 expect(saved.successful).toBe(kind==='legacy'?null:'UNSET');
 expect(saved.observedLoad).toBe(kind==='legacy'?'8':'');
 expect(root.container.queryAll((n:any)=>typeof n.props.children==='string'&&n.props.children.includes('Ton brouillon reste à vérifier'))).toHaveLength(0);
 await act(async()=>root.unmount());
});

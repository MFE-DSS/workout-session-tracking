/** Meaning follows the observed unit and context; no fallback converts a setting into mass. */
export function settingDescriptionV3(setting:{kind:string;value:number|null;unit:string}|null|undefined,context:{load_semantics:string}):string{
 if(!setting||setting.value===null)return setting?.kind==='BODYWEIGHT'?'Poids du corps · aucun réglage de masse':'Réglage inconnu';
 const value=String(setting.value);
 if(setting.kind==='MASS_KG'&&setting.unit==='kg'){
  if(context.load_semantics==='TOTAL_EXTERNAL')return value+' kg au total';
  if(context.load_semantics==='PER_IMPLEMENT')return value+' kg par élément';
  if(context.load_semantics==='MACHINE_DISPLAY_KG')return value+' kg affichés par l’appareil';
 }
 if(setting.kind==='NON_MASS_SETTING'&&setting.unit==='setting'&&context.load_semantics==='NON_MASS_SETTING')return value+' · réglage de l’appareil sans unité de masse';
 if(setting.kind==='ASSISTANCE_SETTING'&&context.load_semantics==='ASSISTANCE_SETTING')return value+(setting.unit==='kg'?' kg d’assistance':' · réglage d’assistance');
 return 'Réglage non interprétable par cette version';
}

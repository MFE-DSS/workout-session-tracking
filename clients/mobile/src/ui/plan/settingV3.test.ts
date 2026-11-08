import {settingDescriptionV3} from './settingV3';
test('nonmass, assistance and unknown meanings are never displayed as total kilograms',()=>{
 expect(settingDescriptionV3({kind:'NON_MASS_SETTING',value:3,unit:'setting'},{load_semantics:'NON_MASS_SETTING'})).not.toContain('kg');
 expect(settingDescriptionV3({kind:'MASS_KG',value:14,unit:'kg'},{load_semantics:'PER_IMPLEMENT'})).toBe('14 kg par élément');
 expect(settingDescriptionV3({kind:'MASS_KG',value:17,unit:'kg'},{load_semantics:'MACHINE_DISPLAY_KG'})).toBe('17 kg affichés par l’appareil');
 expect(settingDescriptionV3({kind:'MASS_KG',value:17,unit:'kg'},{load_semantics:'UNKNOWN'})).not.toContain('au total');
});

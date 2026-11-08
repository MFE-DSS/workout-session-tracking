export function runtimeNoticeV3(message:string|null|undefined):string|null {
 if(!message)return null;
 const known:Record<string,string>={
  source_revision_changed:'Les informations ont changé. Relis-les avant de continuer.',
  authority_generation_changed:'La règle applicable a changé. Vérifie à nouveau.',
  calibration_authority_changed:'La règle de cette rencontre a changé. Relis-la avant de continuer.',
  calibration_review_required:'Une revue est nécessaire avant de poursuivre la préparation.',
  calibration_withdrawn:'Le guidage de cette rencontre a été arrêté. Les observations sont conservées.',
  calibration_action_not_permitted:'Cette action n’est pas disponible dans l’état actuel de la rencontre.',
  runtime_not_served:'Ce parcours n’est pas disponible actuellement.',
  authority_not_served:'Le guidage n’est pas disponible actuellement. Les faits restent lisibles.',
  producer_unavailable:'La proposition est indisponible pour le moment.',
  session_open:'Une séance est déjà en cours. Reprends-la d’abord.',
  execution_not_representable:'Ce réglage n’est pas pris en charge par cette version.',
  first_session_already_created:'Ta première séance existe déjà. Vérifie sa reprise.',
  REVALIDATION_REQUIRED:'Une nouvelle vérification est nécessaire avant de poursuivre.',
 };
 return known[message]??(/^[A-Za-z][A-Za-z0-9_]+$/.test(message)?'Cette action reste à vérifier. Relis les informations du compte.':message);
}

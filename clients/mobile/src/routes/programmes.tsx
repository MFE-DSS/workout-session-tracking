/** MOB-01 — PROGRAMMES, not migrated yet (MOB-06 / 07 / 09): templates, personal programs, weekly plan, equipment. */
import React from 'react';

import { PendingSpace } from '../shell/PendingSpace';

export default function Programs() {
  return (
    <PendingSpace
      eyebrow="AUREN · Programmes"
      title="Sur le site, pour l’instant"
      text="Les programmes modèles, tes programmes personnels, ton plan de la semaine et ton équipement arriveront ici."
      webPath="/library"
    />
  );
}

/** MOB-01 — PROGRÈS, not migrated yet (MOB-05): session history, exercise history, measured progress. */
import React from 'react';

import { PendingSpace } from '../shell/PendingSpace';

export default function Progress() {
  return (
    <PendingSpace
      eyebrow="AUREN · Progrès"
      title="Sur le site, pour l’instant"
      text="L’historique de tes séances, celui de chaque exercice et tes progrès mesurés arriveront ici."
      webPath="/progress"
    />
  );
}

/** MOB-01 — PROFIL, not migrated yet (MOB-11 + social, operator 2026-10-31): training profile, measures, squads. */
import React from 'react';

import { useShell } from '../shell/ShellContext';
import { PendingSpace } from '../shell/PendingSpace';

export default function Profile() {
  const shell = useShell();
  if (shell.account) return <>{shell.account}</>;
  return (
    <PendingSpace
      eyebrow="AUREN · Profil"
      title="Sur le site, pour l’instant"
      text="Ton profil d’entraînement, tes mesures et l’espace social — squads et classement — arriveront ici."
      webPath="/profile"
    />
  );
}

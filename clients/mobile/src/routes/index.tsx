/** MOB-01 — AUJOURD'HUI: the MISSION (or its quiet states), exactly as ConnectedApp built it. */
import React from 'react';

import { useShell } from '../shell/ShellContext';

export default function Today() {
  return <>{useShell().today}</>;
}

import type { WorkoutState } from '../../domain/workout';
import { type BodyMapViewPreset, presetForZone } from './viewPresets';

/**
 * COMPLETE (`COMPLETE-SCREEN-V1`) — the zones a session worked, from the sets DONE on this device, by the server
 * recap's own rule (each exercise's primary zone, from the plan). Most sets first, then by name.
 */
export function zonesDone(state: WorkoutState): { zone: string; label: string; sets: number }[] {
  const plan = state.plan!;
  const counts = new Map<string, { zone: string; label: string; sets: number }>();
  for (const s of plan.sets) {
    if (!state.done[s.set_id]) continue;
    const zone = plan.exercises.find((e) => e.se_id === s.se_id)?.zone;
    if (!zone) continue;
    const c = counts.get(zone.zone) ?? { zone: zone.zone, label: zone.label, sets: 0 };
    c.sets += 1;
    counts.set(zone.zone, c);
  }
  return [...counts.values()].sort((a, b) => b.sets - a.sets || a.label.localeCompare(b.label));
}

/**
 * The session's BodyMap for those zones (`BODYMAP-ZONES-V1`), each window naming its count of sets DONE — a fact
 * of the session, never an intensity or an effect. A zone outside the taxonomy draws no window.
 */
export function zonePanelPresets(zones: { zone: string; sets: number }[]): BodyMapViewPreset[] {
  return zones.flatMap((z) => {
    const p = presetForZone(z.zone);
    return p ? [{ ...p, label: `${p.label} · ${z.sets}` }] : [];
  });
}

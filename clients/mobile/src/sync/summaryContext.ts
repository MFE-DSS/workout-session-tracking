import type { SessionHistoryRead } from '../api/types';

/** D-MOB02-3: observed server completions only, never the declared programme or local session. */
export function summaryContext(value: SessionHistoryRead, sessionId: number): string | null {
  if (value.has_more !== false || !Array.isArray(value.sessions)) return null;
  const ids = new Set<number>();
  for (const row of value.sessions) {
    if (!Number.isSafeInteger(row.id) || row.id <= 0 || ids.has(row.id)
      || !Number.isFinite(Date.parse(row.started_at)) || !Number.isFinite(Date.parse(row.ended_at))
      || Date.parse(row.ended_at) < Date.parse(row.started_at)) return null;
    ids.add(row.id);
  }
  const current = value.sessions.find((row) => row.id === sessionId);
  // Until the server lists this completion, the local finish must not become an observed activity.
  if (!current) return null;
  const end = new Date(current.ended_at);
  const start = new Date(end);
  start.setUTCDate(start.getUTCDate() - (start.getUTCDay() + 6) % 7);
  start.setUTCHours(0, 0, 0, 0);
  const count = value.sessions.filter((row) => {
    const ended = Date.parse(row.ended_at);
    return ended >= start.getTime() && ended <= end.getTime();
  }).length;
  const date = (d: Date) => `${String(d.getUTCDate()).padStart(2, '0')}/${String(d.getUTCMonth() + 1).padStart(2, '0')}/${d.getUTCFullYear()}`;
  const time = `${String(end.getUTCHours()).padStart(2, '0')}:${String(end.getUTCMinutes()).padStart(2, '0')}`;
  return `Du ${date(start)} à 00:00 au ${date(end)} à ${time} UTC : ${count} ${count === 1 ? 'séance terminée' : 'séances terminées'} dans l’historique AUREN.`;
}

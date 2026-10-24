/** French number formatting for gym readouts: `52,5`, `10`. */

export function kg(value: number | null): string {
  if (value === null) return '—';
  return Number.isInteger(value) ? String(value) : value.toFixed(1).replace('.', ',');
}

/** The engine writes `52.5 kg · 6-10 reps`; display it the French way. */
export function frenchSummary(text: string): string {
  return text.replace(/(\d)\.(\d)/g, '$1,$2').replace(/(\d)-(\d)/g, '$1–$2');
}

export function scheme(text: string | null): string {
  if (!text) return '';
  return text.replace(/(\d)x\s*/i, '$1 × ').replace(/(\d)-(\d)/g, '$1–$2');
}

export function elapsedLabel(fromMs: number, toMs: number): string {
  const min = Math.max(0, Math.round((toMs - fromMs) / 60000));
  if (min < 60) return `${min} min`;
  return `${Math.floor(min / 60)} h ${String(min % 60).padStart(2, '0')}`;
}

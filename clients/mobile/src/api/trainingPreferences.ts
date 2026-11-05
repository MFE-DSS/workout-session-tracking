/** Declared facts only. No recommendation, inferred defaults, cache or offline queue. */
import { AuthSession } from '../auth/authSession';
import { ApiFailure, type Transport } from './http';

export type TrainingDeclarations = {
  sessions_per_week: number | null;
  focus_priorities: string[] | null;
  available_equipment: string[] | null;
};
type Choice = { value: string; label: string };
export type TrainingDeclarationsSnapshot = {
  contract_version: 1;
  declarations: TrainingDeclarations;
  options: {
    sessions_per_week: { min: number; max: number };
    focus_priorities: Choice[];
    available_equipment: Choice[];
  };
};
export type TrainingDeclarationsOutcome =
  | { state: 'confirmed'; value: TrainingDeclarationsSnapshot }
  | { state: 'rejected'; code: string | null }
  | { state: 'unknown' }
  | { state: 'cancelled' };

const PATH = '/me/training-preferences/declarations';
const strings = (x: unknown): x is string[] => Array.isArray(x) && x.every((v) => typeof v === 'string');
const choices = (x: unknown): x is Choice[] => Array.isArray(x) && x.every((v) => v && typeof v.value === 'string' && typeof v.label === 'string');

function snapshot(raw: unknown): TrainingDeclarationsSnapshot | null {
  const value = raw as TrainingDeclarationsSnapshot | null;
  if (!value || value.contract_version !== 1 || !value.declarations || !value.options) return null;
  const d = value.declarations, o = value.options;
  if (!o.sessions_per_week || !Number.isInteger(o.sessions_per_week.min) || !Number.isInteger(o.sessions_per_week.max) || o.sessions_per_week.min > o.sessions_per_week.max) return null;
  if (!choices(o.focus_priorities) || !choices(o.available_equipment)) return null;
  if (d.sessions_per_week !== null && (!Number.isInteger(d.sessions_per_week) || d.sessions_per_week < o.sessions_per_week.min || d.sessions_per_week > o.sessions_per_week.max)) return null;
  for (const key of ['focus_priorities', 'available_equipment'] as const) {
    const items = d[key];
    if (items !== null && (!strings(items) || items.some((item) => !o[key].some((c) => c.value === item)))) return null;
  }
  return value;
}

export class TrainingPreferencesClient {
  private saving = false;
  constructor(private readonly auth: AuthSession, private readonly call: Transport) {}

  read(): Promise<TrainingDeclarationsOutcome> { return this.request(); }

  async save(input: TrainingDeclarations): Promise<TrainingDeclarationsOutcome> {
    if (this.saving) return { state: 'rejected', code: 'request_in_flight' };
    this.saving = true;
    // Capture before any await: later edits to a form cannot change this request.
    const body = { ...input, focus_priorities: input.focus_priorities?.slice() ?? null,
      available_equipment: input.available_equipment?.slice() ?? null };
    try { return await this.request(body); }
    finally { this.saving = false; }
  }

  private async request(body?: TrainingDeclarations): Promise<TrainingDeclarationsOutcome> {
    const revision = this.auth.revision;
    try {
      const raw = await this.auth.authorized<unknown>((token) => this.call(PATH, {
        token, ...(body ? { method: 'PUT', body } : {}),
      }), { retryUnauthorized: body === undefined });
      if (revision !== this.auth.revision) return { state: 'cancelled' };
      const value = snapshot(raw);
      return value ? { state: 'confirmed', value } : { state: 'unknown' };
    } catch (error) {
      if (revision !== this.auth.revision) return { state: 'cancelled' };
      if (error instanceof ApiFailure && error.kind === 'http' && error.status >= 400 && error.status < 500 && error.status !== 408) return { state: 'rejected', code: error.code };
      return { state: 'unknown' };
    }
  }
}

/** Owned command bytes, distinct from canonical programme storage. */
export const BUILDER_VERSION = 'program-builder/1.0.0' as const;
export const BUILDER_MAX_BYTES = 131072;
export const BUILDER_OPERATIONS = ['CREATE', 'SAVE_TREE', 'RENAME', 'VALIDATE', 'PUBLISH', 'NEW_CYCLE', 'ARCHIVE'] as const;
export type BuilderOperation = typeof BUILDER_OPERATIONS[number];
export type BuilderSelection = {slug: string; name: string; ekb_version: string};
export type BuilderRepTarget = {min_reps: number; max_reps: number; technique: string | null; is_warmup: boolean};
export type BuilderTreeExercise = {position: number; selection: BuilderSelection | null;
  keep: {slot_id: number; slot_digest: string} | null; rep_targets: BuilderRepTarget[] | null; notes: string | null};
export type BuilderTreeSession = {position: number; name: string; kind: 'strength' | 'cardio'; focus: string;
  duration_target_minutes: number | null; notes: string | null; exercises: BuilderTreeExercise[]};
export type BuilderCommand = {contract_version: typeof BUILDER_VERSION; command_id: string;
  operation: BuilderOperation; program_id: number | null; expected_source_digest: string | null;
  payload: {title: string} | {sessions: BuilderTreeSession[]} | Record<string, never>};
export type PreparedBuilderCommand = {owner_id: number; backend_scope: string; command_id: string;
  operation: BuilderOperation; program_id: number | null; expected_source_digest: string | null;
  payload_json: string; request_sha256: string};

export function builderObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
    && [Object.prototype, null].includes(Object.getPrototypeOf(value));
}
export function builderExact(value: unknown, keys: readonly string[]): value is Record<string, unknown> {
  return builderObject(value) && Object.keys(value).length === keys.length
    && keys.every(key => Object.prototype.hasOwnProperty.call(value, key));
}
export const builderId = (value: unknown): value is number =>
  typeof value === 'number' && Number.isSafeInteger(value) && value > 0;
export const builderHash = (value: unknown): value is string => typeof value === 'string' && /^[0-9a-f]{64}$/.test(value);
export const builderKey = (value: unknown): value is string =>
  typeof value === 'string' && /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$/.test(value);
export const builderText = (value: unknown, max: number, empty = false): value is string =>
  typeof value === 'string' && value.length <= max && !/[\uD800-\uDFFF]/u.test(value) && (empty || value.trim().length > 0);
const nullableText = (value: unknown, max: number) => value === null || builderText(value, max, true);
const invalid = (): never => {throw Error('invalid_builder_command');};
const requireValue = (condition: unknown): void => {if (!condition) invalid();};

function selection(value: unknown): boolean {
  return builderExact(value, ['slug', 'name', 'ekb_version'])
    && builderText(value.slug, 96) && builderText(value.name, 255) && builderText(value.ekb_version, 128);
}
function targets(value: unknown): boolean {
  return Array.isArray(value) && value.length >= 1 && value.length <= 6 && value.every(row =>
    builderExact(row, ['min_reps', 'max_reps', 'technique', 'is_warmup'])
    && builderId(row.min_reps) && builderId(row.max_reps) && row.min_reps <= row.max_reps && row.max_reps <= 50
    && nullableText(row.technique, 8) && typeof row.is_warmup === 'boolean');
}
function exercise(value: unknown, position: number): boolean {
  if (!builderExact(value, ['position', 'selection', 'keep', 'rep_targets', 'notes']) || value.position !== position) return false;
  if (value.keep !== null) {
    return value.selection === null && value.rep_targets === null && value.notes === null
      && builderExact(value.keep, ['slot_id', 'slot_digest']) && builderId(value.keep.slot_id) && builderHash(value.keep.slot_digest);
  }
  return selection(value.selection) && targets(value.rep_targets) && nullableText(value.notes, 8192);
}
function sessions(value: unknown): boolean {
  return Array.isArray(value) && value.length <= 7 && value.every((row, i) =>
    builderExact(row, ['position', 'name', 'kind', 'focus', 'duration_target_minutes', 'notes', 'exercises'])
    && row.position === i + 1 && builderText(row.name, 128) && typeof row.kind === 'string' && ['strength', 'cardio'].includes(row.kind)
    && builderText(row.focus, 128, true)
    && (row.duration_target_minutes === null || typeof row.duration_target_minutes === 'number' && Number.isSafeInteger(row.duration_target_minutes))
    && nullableText(row.notes, 8192) && Array.isArray(row.exercises) && row.exercises.length <= 10
    && row.exercises.every((item, index) => exercise(item, index + 1)));
}
export function builderSorted(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(builderSorted);
  if (builderObject(value)) return Object.fromEntries(Object.keys(value).sort().map(key => [key, builderSorted(value[key])]));
  return value;
}
export function builderByteLength(value: string): number {
  let result = 0;
  for (const char of value) {
    const code = char.codePointAt(0)!;
    result += code < 128 ? 1 : code < 2048 ? 2 : code < 65536 ? 3 : 4;
  }
  return result;
}
export function builderCommandJSON(body: unknown): string {
  if (!builderExact(body, ['contract_version', 'command_id', 'operation', 'program_id', 'expected_source_digest', 'payload'])) return invalid();
  requireValue(body.contract_version === BUILDER_VERSION && builderKey(body.command_id)
    && BUILDER_OPERATIONS.includes(body.operation as BuilderOperation));
  const create = body.operation === 'CREATE';
  requireValue(create ? body.program_id === null && body.expected_source_digest === null
    : builderId(body.program_id) && builderHash(body.expected_source_digest));
  if (create || body.operation === 'RENAME') {
    requireValue(builderExact(body.payload, ['title']) && builderText(body.payload.title, 128));
  } else if (body.operation === 'SAVE_TREE') {
    requireValue(builderExact(body.payload, ['sessions']) && sessions(body.payload.sessions));
  } else requireValue(builderExact(body.payload, []));
  const result = JSON.stringify(builderSorted(body));
  requireValue(builderByteLength(result) <= BUILDER_MAX_BYTES);
  return result;
}
export function builderBackendScope(value: unknown): value is string {
  if (typeof value !== 'string' || value.length === 0 || value.length > 2048) return false;
  try {
    const url = new URL(value);
    return ['https:', 'http:'].includes(url.protocol) && !url.username && !url.password && !url.hash && !url.search
      && url.toString().replace(/\/+$/, '') === value;
  } catch {return false;}
}
export async function prepareBuilderCommand(owner: number, backend: string, body: unknown,
  sha: (value: string) => Promise<string>): Promise<PreparedBuilderCommand> {
  requireValue(builderId(owner) && builderBackendScope(backend));
  const payload_json = builderCommandJSON(body);
  const decoded = JSON.parse(payload_json) as BuilderCommand;
  const request_sha256 = await sha(payload_json);
  requireValue(builderHash(request_sha256));
  return {owner_id: owner, backend_scope: backend, command_id: decoded.command_id,
    operation: decoded.operation, program_id: decoded.program_id, expected_source_digest: decoded.expected_source_digest,
    payload_json, request_sha256};
}
export async function verifyPreparedBuilderCommand(value: unknown,
  sha: (value: string) => Promise<string>): Promise<PreparedBuilderCommand> {
  if (!builderExact(value, ['owner_id', 'backend_scope', 'command_id', 'operation', 'program_id',
    'expected_source_digest', 'payload_json', 'request_sha256']) || !builderId(value.owner_id)
    || !builderBackendScope(value.backend_scope) || typeof value.payload_json !== 'string'
    || builderByteLength(value.payload_json) > BUILDER_MAX_BYTES || !builderHash(value.request_sha256)) return invalid();
  let body: unknown;
  try {body = JSON.parse(value.payload_json);} catch {return invalid();}
  const expected = await prepareBuilderCommand(value.owner_id, value.backend_scope, body, sha);
  if (Object.keys(expected).some(key => expected[key as keyof PreparedBuilderCommand] !== value[key])) return invalid();
  return {...expected};
}

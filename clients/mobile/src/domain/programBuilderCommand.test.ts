import {createHash} from 'node:crypto';
import {builderCommandJSON, prepareBuilderCommand} from './programBuilderCommand';

const command = () => ({contract_version: 'program-builder/1.0.0', command_id: 'pb-create-1',
  operation: 'CREATE', program_id: null, expected_source_digest: null,
  payload: {title: 'Programme personnel'}});
const exact = '{"command_id":"pb-create-1","contract_version":"program-builder/1.0.0","expected_source_digest":null,"operation":"CREATE","payload":{"title":"Programme personnel"},"program_id":null}';
const sha = async (s: string) => createHash('sha256').update(s, 'utf8').digest('hex');

test('prepares exact durable bytes and hash without normalizing a title', async () => {
  const body = command();
  expect(builderCommandJSON(body)).toBe(exact);
  const prepared = await prepareBuilderCommand(42, 'https://qa.test.invalid', body, sha);
  expect(prepared).toEqual({owner_id: 42, backend_scope: 'https://qa.test.invalid',
    command_id: 'pb-create-1', operation: 'CREATE', program_id: null,
    expected_source_digest: null, payload_json: exact,
    request_sha256: createHash('sha256').update(exact).digest('hex')});
  body.payload.title = 'Changed after preparation';
  expect(prepared.payload_json).toBe(exact);
});

test.each([
  {...command(), unexpected: true}, {...command(), program_id: 1},
  {...command(), expected_source_digest: 'a'.repeat(64)},
  {...command(), command_id: 'not a key'}, {...command(), payload: {title: 'Name', injected: true}},
])('refuses malformed create intent before preparing storage or HTTP', body => {
  expect(() => builderCommandJSON(body)).toThrow('invalid_builder_command');
});

test('does not invent prescriptions for a selected movement', () => {
  const body = {...command(), operation: 'SAVE_TREE', program_id: 7,
    expected_source_digest: 'a'.repeat(64), payload: {sessions: [{position: 1, name: 'A',
      kind: 'strength', focus: '', duration_target_minutes: null, notes: null, exercises: [{
        position: 1, selection: {slug: 'movement', name: 'Movement', ekb_version: '1'}, keep: null,
        rep_targets: [], notes: null}]}]}};
  expect(() => builderCommandJSON(body)).toThrow('invalid_builder_command');
  body.payload.sessions[0].exercises[0].rep_targets = [{min_reps: 8, max_reps: 12, technique: null, is_warmup: false}] as never[];
  expect(builderCommandJSON(body)).toContain('"min_reps":8');
});

test('keeps an original slot by its identity and digest without copying old numeric values', () => {
  const body = {...command(), operation: 'SAVE_TREE', program_id: 7,
    expected_source_digest: 'a'.repeat(64), payload: {sessions: [{position: 1, name: 'A',
      kind: 'strength', focus: '', duration_target_minutes: null, notes: null, exercises: [{
        position: 1, selection: null, keep: {slot_id: 9, slot_digest: 'b'.repeat(64)},
        rep_targets: null, notes: null}]}]}};
  expect(builderCommandJSON(body)).toContain('"slot_id":9');
});

test.each([0, -1, 1.5, Number.NaN])('rejects invalid owner partition %s', async owner => {
  await expect(prepareBuilderCommand(owner, 'https://qa.test.invalid', command(), sha)).rejects.toThrow();
});

test('rejects a coercible object as session kind instead of hashing an invalid wire value', () => {
  const body = {...command(), operation: 'SAVE_TREE', program_id: 7,
    expected_source_digest: 'a'.repeat(64), payload: {sessions: [{position: 1, name: 'A',
      kind: {toString: () => 'strength'}, focus: '', duration_target_minutes: null, notes: null, exercises: []}]}};
  expect(() => builderCommandJSON(body)).toThrow('invalid_builder_command');
});

test('rejects isolated UTF16 surrogates that cannot be encoded as canonical UTF8', () => {
  expect(() => builderCommandJSON({...command(), payload: {title: '\ud800'}})).toThrow('invalid_builder_command');
});

test('keeps the existing eight-character bound for a newly declared technique', () => {
  const body = {...command(), operation: 'SAVE_TREE', program_id: 7,
    expected_source_digest: 'a'.repeat(64), payload: {sessions: [{position: 1, name: 'A',
      kind: 'strength', focus: '', duration_target_minutes: null, notes: null, exercises: [{
        position: 1, selection: {slug: 'movement', name: 'Movement', ekb_version: '1'}, keep: null,
        rep_targets: [{min_reps: 8, max_reps: 12, technique: 'TOO-LONG9', is_warmup: false}], notes: null}]}]}};
  expect(() => builderCommandJSON(body)).toThrow('invalid_builder_command');
});

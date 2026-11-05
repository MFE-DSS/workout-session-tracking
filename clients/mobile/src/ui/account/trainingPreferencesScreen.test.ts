import React, { act } from 'react';
import { Alert } from 'react-native';
import { createRoot, type Root } from 'test-renderer';
import { TrainingPreferencesScreen } from './TrainingPreferencesScreen';
import fixture from './review/trainingDeclarations.fixture.json';
import type { TrainingDeclarationsSnapshot } from '../../api/trainingPreferences';

jest.mock('react-native-safe-area-context', () => ({
  useSafeAreaInsets: () => ({ top: 47, bottom: 34, left: 0, right: 0 }),
}));
let root: Root;
beforeEach(() => { root = createRoot(); });
afterEach(async () => { await act(async () => root.unmount()); jest.restoreAllMocks(); });
const snapshot = fixture as TrainingDeclarationsSnapshot;
function node(id: string) { const nodes = root.container.queryAll((n) => n.props.testID === id); expect(nodes.length).toBeGreaterThan(0); return nodes[0].props; }
const click = async (id: string) => { await act(async () => node(id).onClick({ nativeEvent: {}, stopPropagation() {}, currentTarget: 1, target: 1 })); };

test('availability asks only cadence and preserves existing equipment facts in its full replacement', async () => {
  const saved: any[] = [];
  const client = { read: async () => ({ state: 'confirmed' as const, value: { ...snapshot, declarations: { ...snapshot.declarations, available_equipment: ['machine'] } } }),
    save: async (d: any) => { saved.push(d); return { state: 'confirmed' as const, value: { ...snapshot, declarations: d } }; } };
  await act(async () => root.render(React.createElement(TrainingPreferencesScreen, { client, onClose() {}, onReconnect() {} })));
  expect(root.container.queryAll((n) => String(n.props.testID ?? '').startsWith('preferences-equipment-'))).toHaveLength(0);
  await click('preferences-frequency-4');
  expect(node('preferences-frequency-4').accessibilityState.selected).toBe(true);
  await click('preferences-next'); await click('preferences-focus-arms'); await click('preferences-save');
  expect(saved).toEqual([{ sessions_per_week: 4, available_equipment: ['machine'], focus_priorities: ['arms'] }]);
  expect(root.container.queryAll((n) => n.props.children === 'Préférences enregistrées.').length).toBeGreaterThan(0);
});

test('a lost save exposes only explicit rereading and never a second write', async () => {
  let writes = 0;
  const client = { read: async () => ({ state: 'confirmed' as const, value: snapshot }),
    save: async () => { writes++; return { state: 'unknown' as const }; } };
  await act(async () => root.render(React.createElement(TrainingPreferencesScreen, { client, onClose() {}, onReconnect() {} })));
  await click('preferences-frequency-4'); await click('preferences-next'); await click('preferences-save');
  expect(writes).toBe(1); expect(root.container.queryAll((n) => n.props.testID === 'preferences-save')).toHaveLength(0);
  await click('preferences-reload'); expect(writes).toBe(1);
  expect(node('preferences-save')).toBeDefined();
});

test('return from page2 keeps the draft; exiting page1 requires a real discard choice', async () => {
  const close = jest.fn(); let registered: (() => void) | null = null;
  const confirm = jest.spyOn(Alert, 'alert').mockImplementation(() => undefined);
  const client = { read: async () => ({ state: 'confirmed' as const, value: snapshot }), save: async () => ({ state: 'unknown' as const }) };
  await act(async () => root.render(React.createElement(TrainingPreferencesScreen, { client, onClose: close, onReconnect() {}, registerExit: (fn) => { registered = fn; } })));
  await click('preferences-frequency-4'); await click('preferences-next');
  act(() => registered?.());
  expect(node('preferences-frequency-4').accessibilityState.selected).toBe(true); expect(confirm).not.toHaveBeenCalled();
  act(() => registered?.());
  expect(close).not.toHaveBeenCalled(); expect(confirm).toHaveBeenCalledTimes(1);
  const choices = confirm.mock.calls[0][2]!;
  act(() => choices.find((c) => c.style === 'destructive')?.onPress?.());
  expect(close).toHaveBeenCalledTimes(1);
});

test('a discard confirmation retained from a previous client cannot close a new owner editor', async () => {
  const close = jest.fn(); const confirm = jest.spyOn(Alert, 'alert').mockImplementation(() => undefined);
  const a = { read: async () => ({ state: 'confirmed' as const, value: snapshot }), save: async () => ({ state: 'unknown' as const }) };
  await act(async () => root.render(React.createElement(TrainingPreferencesScreen, { client: a, onClose: close, onReconnect() {} })));
  await click('preferences-frequency-4'); await click('account-back');
  const discard = confirm.mock.calls[0][2]!.find((c) => c.style === 'destructive')!;
  const b = { ...a };
  await act(async () => root.render(React.createElement(TrainingPreferencesScreen, { client: b, onClose: close, onReconnect() {} })));
  act(() => discard.onPress?.()); expect(close).not.toHaveBeenCalled();
});

test('the existing full web profile remains available even when native preference loading fails', async () => {
  const open = jest.fn();
  const client = { read: async () => ({ state: 'unknown' as const }), save: async () => ({ state: 'unknown' as const }) };
  await act(async () => root.render(React.createElement(TrainingPreferencesScreen, { client, onClose() {}, onReconnect() {}, onWebProfile: open })));
  await click('preferences-web-profile'); expect(open).toHaveBeenCalledTimes(1);
});

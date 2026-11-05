import React, { act } from 'react';
import { createRoot, type Root } from 'test-renderer';
import { LoginScreen } from '../LoginScreen';
import { SignupScreen, PasswordScreen } from './AccountForms';
jest.mock('react-native-safe-area-context', () => ({
  useSafeAreaFrame: () => ({ width: 390, height: 844 }),
  useSafeAreaInsets: () => ({ top: 47, bottom: 34, left: 0, right: 0 }),
  SafeAreaProvider: ({ children }: { children: React.ReactNode }) => children,
  SafeAreaFrameContext: require('react').createContext({ width: 390, height: 844 }),
  SafeAreaInsetsContext: require('react').createContext({ top: 47, bottom: 34, left: 0, right: 0 }),
}));
let root: Root;
beforeEach(() => { root = createRoot(); });
afterEach(async () => { await act(async () => root.unmount()); });
function find(predicate: (n: { props: Record<string, any> }) => boolean) { const nodes = root.container.queryAll(predicate); expect(nodes.length).toBeGreaterThan(0); return nodes[0].props; }
async function change(label: string, value: string) { await act(async () => find((n) => n.props.accessibilityLabel === label && typeof n.props.onChangeText === 'function').onChangeText(value)); }
function action(id: string) { const p = find((n) => n.props.testID === id); return () => p.onClick({ nativeEvent: {}, stopPropagation: () => undefined, currentTarget: 1, target: 1 }); }

test('branded entry uses the locked mark and keeps one login submission per immediate double press', async () => {
  const submitted = jest.fn(); const signup = jest.fn();
  await act(async () => root.render(React.createElement(LoginScreen, { error: null, busy: false, onSubmit: submitted, onCreateAccount: signup })));
  expect(root.container.queryAll((n) => n.props.testID === 'entry-auren-mark').length).toBeGreaterThan(0);
  await change('Identifiant', 'athlete'); await change('Mot de passe', 'test-only');
  await act(async () => { const press = action('login'); press(); press(); });
  expect(submitted).toHaveBeenCalledTimes(1);
  await act(async () => action('entry-signup')()); expect(signup).toHaveBeenCalledTimes(1);
});

test('signup mismatch keeps the form without sending and a corrected double press sends one canonical body', async () => {
  const submitted = jest.fn();
  await act(async () => root.render(React.createElement(SignupScreen, { busy: false, outcome: null, onSubmit: submitted, onBack: () => undefined, onLogin: () => undefined })));
  await change('Identifiant', 'athlete'); await change('Mot de passe', 'test-only-password'); await change('Confirmer le mot de passe', 'different');
  await act(async () => action('signup-submit')()); expect(submitted).not.toHaveBeenCalled();
  await change('Confirmer le mot de passe', 'test-only-password');
  await act(async () => { const press = action('signup-submit'); press(); press(); });
  expect(submitted).toHaveBeenCalledTimes(1);
  expect(submitted).toHaveBeenCalledWith({ username: 'athlete', password: 'test-only-password', password_confirm: 'test-only-password', email: '' });
});

test('unknown signup outcome proposes login verification and never sends another creation', async () => {
  const submitted = jest.fn(); const verify = jest.fn();
  await act(async () => root.render(React.createElement(SignupScreen, { busy: false, outcome: { state: 'unknown' }, onSubmit: submitted, onBack: () => undefined, onLogin: verify })));
  await act(async () => action('signup-verify')());
  expect(verify).toHaveBeenCalledTimes(1); expect(submitted).not.toHaveBeenCalled();
  expect(root.container.queryAll((n) => n.props.testID === 'signup-submit')).toHaveLength(0);
});

test('password consumer uses current/new/confirmation and never repeats an uncertain mutation', async () => {
  const submitted = jest.fn(); const relogin = jest.fn();
  const props = { busy: false, outcome: null, onSubmit: submitted, onBack: () => undefined, onLogin: relogin };
  await act(async () => root.render(React.createElement(PasswordScreen, props)));
  await change('Mot de passe actuel', 'old-test'); await change('Nouveau mot de passe', 'new-test-password'); await change('Confirmer le mot de passe', 'new-test-password');
  await act(async () => { const press = action('password-submit'); press(); press(); });
  expect(submitted).toHaveBeenCalledTimes(1);
  expect(submitted).toHaveBeenCalledWith({ current_password: 'old-test', new_password: 'new-test-password', new_password_confirm: 'new-test-password' });
  await act(async () => root.render(React.createElement(PasswordScreen, { ...props, outcome: { state: 'unknown' } })));
  await act(async () => action('password-verify')());
  expect(relogin).toHaveBeenCalledTimes(1); expect(submitted).toHaveBeenCalledTimes(1);
});


test('review bench exposes the actual password confirmation instead of account creation', async () => {
  const { AccountReviewBoard } = require('./review/AccountReviewBoard');
  process.env.EXPO_PUBLIC_REVIEW_CASE = 'password';
  try {
    await act(async () => root.render(React.createElement(AccountReviewBoard)));
    await change('Mot de passe actuel', 'old-test'); await change('Nouveau mot de passe', 'new-test-password'); await change('Confirmer le mot de passe', 'new-test-password');
    await act(async () => action('password-submit')());
    expect(root.container.queryAll((n) => n.props.children === 'Mot de passe mis à jour.').length).toBeGreaterThan(0);
    expect(root.container.queryAll((n) => n.props.children === 'Ton compte est créé.')).toHaveLength(0);
  } finally { delete process.env.EXPO_PUBLIC_REVIEW_CASE; }
});

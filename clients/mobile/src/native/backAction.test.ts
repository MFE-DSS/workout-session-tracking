import { BackContext, backAction } from './backAction';

const at = (c: Partial<BackContext>): BackContext => ({
  screen: 'APP', inWorkout: false, paused: false, sheetOpen: false, ...c,
});

describe('PLAT-01 — Android hardware back', () => {
  it('opens « Quitter la séance » during a set or a rest, never leaves the app', () => {
    expect(backAction(at({ inWorkout: true }))).toBe('exit-sheet');
  });

  it('closes an open sheet and does nothing else', () => {
    expect(backAction(at({ inWorkout: true, sheetOpen: true }))).toBe('close-sheet');
    expect(backAction(at({ sheetOpen: true }))).toBe('close-sheet');
  });

  it('leaves the system decide on the resume screen — the workout is restored at relaunch', () => {
    expect(backAction(at({ inWorkout: true, paused: true }))).toBe('system');
  });

  it('leaves the system decide outside a workout: MISSION, bilan, waiting screens, login, boot', () => {
    expect(backAction(at({}))).toBe('system');
    expect(backAction(at({ screen: 'LOGIN' }))).toBe('system');
    expect(backAction(at({ screen: 'BOOT', inWorkout: true }))).toBe('system');
  });
});

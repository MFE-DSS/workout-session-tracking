import { FIRST_SPACE, OpenContext, SPACES, backInShell, initialSpace } from './shellNav';

const opening = (c: Partial<OpenContext>): OpenContext => ({
  authPending: false, signedIn: true, openWorkout: false, ...c,
});

describe('MOB-01 — where the shell opens', () => {
  it('offers the resume BEFORE any space when a workout is open', () => {
    expect(initialSpace(opening({ openWorkout: true }))).toBe('resume');
  });

  it('opens on the MISSION space otherwise', () => {
    expect(initialSpace(opening({}))).toBe('today');
    expect(FIRST_SPACE).toBe('today');
  });

  it('shows the login and no space without a valid session — even with an open workout', () => {
    expect(initialSpace(opening({ signedIn: false }))).toBe('login');
    expect(initialSpace(opening({ signedIn: false, openWorkout: true }))).toBe('login');
  });

  it('waits on the boot screen while the token is restored', () => {
    expect(initialSpace(opening({ authPending: true, openWorkout: true }))).toBe('boot');
  });
});

describe('MOB-01 — Android back inside the shell', () => {
  it('pops the current screen of a space', () => {
    for (const space of SPACES) expect(backInShell({ space, depth: 2 })).toBe('pop');
  });

  it('brings any other space back to the first one from its root', () => {
    expect(backInShell({ space: 'profile', depth: 0 })).toBe('first-space');
    expect(backInShell({ space: 'programs', depth: 0 })).toBe('first-space');
    expect(backInShell({ space: 'progress', depth: 0 })).toBe('first-space');
  });

  it('leaves the system decide at the root of the first space', () => {
    expect(backInShell({ space: 'today', depth: 0 })).toBe('system');
  });
});

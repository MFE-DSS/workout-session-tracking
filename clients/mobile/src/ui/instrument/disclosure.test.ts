import { disclosureController, type Presentation, REST_AFTER_MS } from './disclosure';

describe('DA-02.4B.2 — disclosure: a gesture reveals, silence rests', () => {
  beforeEach(() => jest.useFakeTimers());
  afterEach(() => jest.useRealTimers());

  const track = () => {
    const seen: Presentation[] = [];
    return { seen, c: disclosureController((p) => seen.push(p)) };
  };

  it('a gesture switches to ADJUSTING at once', () => {
    const { seen, c } = track();
    c.wake();
    expect(seen).toEqual(['adjusting']);
  });

  it('back to REST 1,5 s after the last gesture, not before', () => {
    const { seen, c } = track();
    c.wake();
    jest.advanceTimersByTime(REST_AFTER_MS - 1);
    expect(seen.at(-1)).toBe('adjusting');
    jest.advanceTimersByTime(1);
    expect(seen.at(-1)).toBe('rest');
  });

  it('every new gesture restarts the delay (a drag stays ADJUSTING)', () => {
    const { seen, c } = track();
    c.wake();
    jest.advanceTimersByTime(1000);
    c.wake();
    jest.advanceTimersByTime(1000);
    expect(seen.at(-1)).toBe('adjusting');
    jest.advanceTimersByTime(REST_AFTER_MS - 1000);
    expect(seen.at(-1)).toBe('rest');
    expect(seen.filter((p) => p === 'rest')).toHaveLength(1);
  });

  it('disposing cancels the pending return to REST', () => {
    const { seen, c } = track();
    c.wake();
    c.dispose();
    jest.advanceTimersByTime(REST_AFTER_MS * 2);
    expect(seen).toEqual(['adjusting']);
  });
});

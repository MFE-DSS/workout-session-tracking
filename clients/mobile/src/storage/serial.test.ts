import { createSerialQueue, withRetry } from './serial';

const tick = (ms: number) => new Promise((r) => setTimeout(r, ms));

describe('journal writes never overlap', () => {
  test('a metric write fired during a set commit waits for the commit to finish', async () => {
    const serial = createSerialQueue();
    const events: string[] = [];
    let inside = 0;
    let maxInside = 0;
    const write = (name: string, ms: number) =>
      serial(async () => {
        inside += 1;
        maxInside = Math.max(maxInside, inside);
        events.push(`${name}:start`);
        await tick(ms);
        events.push(`${name}:end`);
        inside -= 1;
      });
    // the exact race seen on the iPhone: commit + two metrics fired together
    await Promise.all([write('commit', 20), write('metric-set-validated', 1), write('metric-notif', 1)]);
    expect(maxInside).toBe(1);
    expect(events).toEqual([
      'commit:start', 'commit:end',
      'metric-set-validated:start', 'metric-set-validated:end',
      'metric-notif:start', 'metric-notif:end',
    ]);
  });

  test('a failed write does not block the next one, and its error still reaches its caller', async () => {
    const serial = createSerialQueue();
    const failing = serial(async () => {
      throw new Error('database is locked');
    });
    await expect(failing).rejects.toThrow('database is locked');
    await expect(serial(async () => 'next')).resolves.toBe('next');
  });

  test('a transient failure is retried; a persistent one is raised, never swallowed', async () => {
    let calls = 0;
    await expect(withRetry(async () => {
      calls += 1;
      if (calls < 2) throw new Error('busy');
      return 'saved';
    }, 3, 1)).resolves.toBe('saved');
    await expect(withRetry(async () => {
      throw new Error('disk full');
    }, 2, 1)).rejects.toThrow('disk full');
  });
});

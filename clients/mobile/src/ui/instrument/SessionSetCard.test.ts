import { CONTRACT_FIXTURES } from '../contract/fixtures';
import { SESSION_CARD, sessionCardLayout } from './SessionSetCard';

const CARDS = CONTRACT_FIXTURES.filter((f) => f.contract === 'SESSION-CARD-R1');

describe('DA-02.7 R1 — the set card, read top to bottom, the instrument under the thumb', () => {
  it('the governed cards exist', () => {
    expect(CARDS.length).toBeGreaterThan(0);
  });

  it.each(CARDS.map((f) => [f.id, f] as const))('%s: the pieces fill the screen exactly, no unintended void', (_, f) => {
    const l = sessionCardLayout(f.width, f.height);
    const c = SESSION_CARD;
    expect(l.fits).toBe(true);
    expect(c.top + c.header + l.split + c.gap + c.pair + c.gap + l.bottomBlock).toBe(f.height);
  });

  it.each(CARDS.map((f) => [f.id, f] as const))('%s: the instrument keeps its governed size, full-bleed', (_, f) => {
    expect(f.width).toBeGreaterThanOrEqual(360); // expanded density: the full grid, the zone names
    expect(SESSION_CARD.instrument).toBe(290);
  });

  it('the instrument and its keys sit at the bottom, above the home indicator only', () => {
    const f = CARDS[0];
    const l = sessionCardLayout(f.width, f.height);
    expect(l.bottomBlock).toBe(SESSION_CARD.instrument + l.keys + SESSION_CARD.bottom);
  });
});

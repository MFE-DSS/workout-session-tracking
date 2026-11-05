import { inspectLegacyJournal } from './legacyInspection';
const mockStatements: string[] = [];
let mockTables: { name: string }[];
const mockClosed = jest.fn();
jest.mock('expo-sqlite', () => ({ openDatabaseAsync: async (name: string, options: unknown) => {
  expect(name).toBe('auren.db'); expect(options).toEqual({ useNewConnection: true });
  return { execAsync: async (sql: string) => { mockStatements.push(sql); }, closeAsync: () => mockClosed(),
    getAllAsync: async (sql: string) => { mockStatements.push(sql); return sql.includes('sqlite_master') ? mockTables : []; },
    getFirstAsync: async (sql: string) => { mockStatements.push(sql); return null; } };
} }));
beforeEach(() => { mockStatements.length = 0; mockClosed.mockClear(); mockTables = ['journal_sets','outbox','active_session'].map((name) => ({ name })); });
test('unknown legacy journal is inspected without schema, inflight reset or any data write', async () => {
  expect(await inspectLegacyJournal()).toEqual({ snapshot: null, sets: [], outbox: [] });
  expect(mockStatements[0]).toBe('PRAGMA query_only = ON');
  expect(mockStatements.slice(1).every((sql) => sql.startsWith('SELECT '))).toBe(true);
  expect(mockClosed).toHaveBeenCalledTimes(1);
});
test('partially missing schema fails mockClosed and still closes the inspection connection', async () => {
  mockTables = [{ name: 'outbox' }];
  await expect(inspectLegacyJournal()).rejects.toThrow('legacy-schema');
  expect(mockClosed).toHaveBeenCalledTimes(1);
});

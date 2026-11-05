import { openOwnershipBook } from './ownershipStore';
const mockCommit = jest.fn();
let mockAfterWrite: () => Promise<void>;
jest.mock('expo-sqlite', () => ({ openDatabaseAsync: async () => ({
  execAsync: async () => undefined,
  withExclusiveTransactionAsync: async (fn: (tx: unknown) => Promise<void>) => {
    await fn({ runAsync: async () => mockAfterWrite(), getFirstAsync: async (sql: string) => sql.includes('legacy_owner') ? { user_id: 7 } : { name: 'auren.db' } });
    mockCommit();
  },
}) }));
beforeEach(() => { mockCommit.mockClear(); mockAfterWrite = async () => undefined; });
test('ownership metadata rejects a stale identity inside the transaction before commit', async () => {
  const book = await openOwnershipBook();
  let current = true;
  mockAfterWrite = async () => { current = false; };
  await expect(book.claimLegacy(7, () => current)).rejects.toMatchObject({ status: 401, code: 'stale_identity' });
  expect(mockCommit).not.toHaveBeenCalled();
});
test('device binding also rolls back if identity changes while its native write waits', async () => {
  const book = await openOwnershipBook();
  let current = true;
  mockAfterWrite = async () => { current = false; };
  await expect(book.bindDevice('a', 7, () => current)).rejects.toMatchObject({ code: 'stale_identity' });
  expect(mockCommit).not.toHaveBeenCalled();
});

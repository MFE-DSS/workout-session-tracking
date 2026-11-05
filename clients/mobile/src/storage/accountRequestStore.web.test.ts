import { openAccountRequestStore } from './accountRequestStore.web';
import { openOwnershipBook } from './ownershipStore.web';
test('web preview keeps retirement consistent with the ownership reader, without claiming native durability', async () => {
  const store = await openAccountRequestStore(), book = await openOwnershipBook();
  const row = await store.reserve(7701,'web-test-only',()=>true);
  expect(await store.claim(row,()=>true)).toBe(true);
  await store.write({...row,phase:'confirmed'},()=>true);
  await store.retire({...row,phase:'confirmed'},()=>true);
  expect(await book.isRetiredOwner(7701)).toBe(true);
  await expect(book.bindDevice('web-device',7701)).rejects.toThrow();
});

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

test('web preview does not regress an authoritative terminal intent',async()=>{
 const store=await openAccountRequestStore(),row=await store.reserve(7702,'web-terminal',()=>true);
 await store.write({...row,phase:'rejected_confirmed'},()=>true);
 await expect(store.write({...row,phase:'unknown'},()=>true)).rejects.toThrow('terminal');
 expect((await store.read(7702))?.phase).toBe('rejected_confirmed');
});

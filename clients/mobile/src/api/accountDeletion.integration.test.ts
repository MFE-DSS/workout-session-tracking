import { accountHarness, deferred, reply } from '../../test/accountDataHarness';
import { SqliteFile } from '../../test/sqliteFile';
import { createAccountRequestStore } from '../storage/accountRequestStore';
import { createOwnershipBook } from '../storage/ownershipStore';
import { resolveJournal } from '../storage/ownership';
import { AccountDeletionClient, type DeletionProducer, type DeletionIntent } from './accountDeletion';
jest.mock('expo-sqlite',()=>({openDatabaseAsync:async()=>{throw Error('use-real-sqlite-port');}}));
let file:SqliteFile;
beforeEach(()=>{file=new SqliteFile();});afterEach(()=>file.close());
function receipt(intent:DeletionIntent,state:string){return {contract_version:'account-deletion/1.0.0',owner_id:intent.ownerId,request_id:intent.requestId,state,
 policy_ref:'SYNTHETIC_TEST_ONLY_NOT_SERVED',confirmed_at:'2026-11-05T12:00:00Z',revocation:'CONFIRMED',data_erasure:'CONFIRMED',restore_protection:'CONFIRMED'};}
test('lost submission survives actual SQLite restart and reconciles without replay or early revocation',async()=>{
 const s=await accountHarness();let sends=0,reads=0,state='PENDING';
 const producer:DeletionProducer={submit:async()=>{sends++;throw Error('lost-response');},read:async(_t,i)=>{reads++;return receipt(i,state);},verify:async()=>true};
 let store=await createAccountRequestStore(file.port());const first=new AccountDeletionClient(s.auth,s.call,store,producer,()=> 'stable-key');
 expect((await first.submit('fixture-secret')).state).toBe('unknown');expect(s.auth.signedIn).toBe(true);
 expect(s.calls.filter(c=>c.path==='/auth/logout')).toHaveLength(0);
 file.reopen();store=await createAccountRequestStore(file.port());const auth=s.newAuth();expect(await auth.refresh()).toBe('ok');
 const resumed=new AccountDeletionClient(auth,s.call,store,producer,()=> 'do-not-use-new-key');
 expect((await resumed.submit('fixture-secret')).state).toBe('unknown');expect(sends).toBe(1);
 expect((await resumed.reconcile()).state).toBe('pending');expect(reads).toBe(1);expect(auth.signedIn).toBe(true);
 state='DELETED';const result=await resumed.reconcile();expect(result.state).toBe('confirmed');
 expect(auth.signedIn).toBe(true);const cleanup=jest.fn(async()=>undefined);expect(await resumed.complete(result,cleanup)).toBe(true);
 expect(cleanup).toHaveBeenCalledWith(7);expect(sends).toBe(1);
 expect(file.db.prepare('SELECT request_id,phase FROM account_request_intents').get()).toEqual({request_id:'stable-key',phase:'confirmed'});
});
test('retired owner cannot recover the mapped journal online or offline after real restart; another owner remains valid',async()=>{
 const s=await accountHarness(),store=await createAccountRequestStore(file.port());let book=await createOwnershipBook(file.port());
 await book.assignJournal(7,'owner-seven.db');await book.bindDevice('device-seven',7);
 await book.assignJournal(8,'owner-eight.db');await book.bindDevice('device-eight',8);
 const producer:DeletionProducer={submit:async(_t,i)=>receipt(i,'DELETED'),read:async(_t,i)=>receipt(i,'DELETED'),verify:async()=>true};
 const client=new AccountDeletionClient(s.auth,s.call,store,producer,()=> 'receipt-key');
 const result=await client.submit('fixture-only');expect(await client.complete(result,async()=>undefined)).toBe(true);
 file.reopen();book=await createOwnershipBook(file.port());
 for(const online of [false,true]){
  const r=await resolveJournal({book,deviceId:'device-seven',online,identity:async()=>({id:7,username:'old'}),inspectLegacy:async()=>{throw Error('must-not-open');},verifySession:async()=>{throw Error('must-not-sync');}});
  expect(r).toEqual({state:'needs-connection'});
 }
 await expect(book.bindDevice('new-device',7)).rejects.toThrow();await expect(book.assignJournal(7,'other.db')).rejects.toThrow();
 const other=await resolveJournal({book,deviceId:'device-eight',online:false,identity:async()=>{throw Error('offline');},inspectLegacy:async()=>{throw Error('no-legacy');},verifySession:async()=>{throw Error('no-sync');}});
 expect(other).toMatchObject({state:'ready',userId:8,name:'owner-eight.db'});
});
test('concurrent consumers on the durable store submit only once',async()=>{
 const s=await accountHarness(),store=await createAccountRequestStore(file.port()),wait=deferred<unknown>();let sends=0;
 const producer:DeletionProducer={submit:async(_t,i)=>{sends++;await wait.promise;return receipt(i,'PENDING');},read:async(_t,i)=>receipt(i,'PENDING'),verify:async()=>true};
 const a=new AccountDeletionClient(s.auth,s.call,store,producer,()=> 'a'),b=new AccountDeletionClient(s.auth,s.call,store,producer,()=> 'b');
 const x=a.submit('fixture-only'),y=b.submit('fixture-only');for(let i=0;i<60;i++)await Promise.resolve();wait.resolve(null);
 await Promise.all([x,y]);expect(sends).toBe(1);expect((await store.read(7))?.phase).toBe('pending');
});
test('an old response cannot retire or clean another account using the same SQLite file',async()=>{
 const s=await accountHarness(),store=await createAccountRequestStore(file.port()),wait=deferred<unknown>();let captured:DeletionIntent|null=null;
 const producer:DeletionProducer={submit:async(_t,i)=>{captured=i;return wait.promise;},read:async()=>null,verify:async()=>true};
 const client=new AccountDeletionClient(s.auth,s.call,store,producer,()=> 'old-request'),flight=client.submit('fixture-only');
 for(let i=0;i<60;i++)await Promise.resolve();expect(captured).not.toBeNull();
 await s.auth.logout();s.setOwner(8);await s.auth.login('other','fixture-only',null);wait.resolve(receipt(captured!,'DELETED'));
 const result=await flight;expect(result.state).toBe('cancelled');const cleanup=jest.fn(async()=>undefined);
 expect(await client.complete(result,cleanup)).toBe(false);expect(cleanup).not.toHaveBeenCalled();
 expect(file.db.prepare('SELECT count(*) AS n FROM owner_retirements').get().n).toBe(0);expect(s.auth.signedIn).toBe(true);
});

const producerFixtures=JSON.parse(require('node:fs').readFileSync(require('node:path').resolve(__dirname,'../../../../docs/fixtures/mob03-deletion-producer.v1.json'),'utf8'));
const producerCases:[string,any][]=producerFixtures.cases.map((c:any)=>[c.scenario,c]);
test.each(producerCases)('server protocol fixture %s remains test-only and does not clean before completion',async(_name,c:any)=>{
 expect(producerFixtures.authority).toBe('SYNTHETIC_TEST_ONLY_NOT_SERVED');
 const s=await accountHarness(),store=await createAccountRequestStore(file.port());
 const producer:DeletionProducer={submit:async()=>c.reply,read:async()=>c.reply,verify:async()=>c.simulated_authority};
 const result=await new AccountDeletionClient(s.auth,s.call,store,producer,()=> 'test-deletion-request').submit('fixture-only');
 expect(result.state).toBe(c.expected);expect(s.auth.signedIn).toBe(true);
 expect(file.db.prepare('SELECT count(*) AS n FROM owner_retirements').get().n).toBe(0);
 expect(s.calls.filter(x=>x.path==='/auth/logout')).toHaveLength(0);
});

test('an older pending poll cannot overwrite a verified completion from another consumer',async()=>{
 const s=await accountHarness(),store=await createAccountRequestStore(file.port()),late=deferred<unknown>(),started=deferred<null>();let polls=0;
 const producer:DeletionProducer={submit:async(_t,i)=>receipt(i,'PENDING'),read:async(_t,i)=>{if(++polls===1){started.resolve(null);return late.promise;}return receipt(i,'DELETED');},verify:async()=>true};
 const first=new AccountDeletionClient(s.auth,s.call,store,producer,()=> 'stable-race');await first.submit('fixture-only');
 const old=first.reconcile();await started.promise;
 const second=new AccountDeletionClient(s.auth,s.call,store,producer),confirmed=await second.reconcile();expect(confirmed.state).toBe('confirmed');
 late.resolve(receipt({ownerId:7,requestId:'stable-race',phase:'pending'},'PENDING'));
 expect((await old).state).toBe('unknown');expect((await store.read(7))?.phase).toBe('confirmed');
 expect(await second.complete(confirmed,async()=>undefined)).toBe(true);
});

test.each([401,404])('status HTTP %s after an uncertain request cannot authorize cleanup or lose durable identity',async(status)=>{
 const s=await accountHarness(),store=await createAccountRequestStore(file.port());
 s.handle(async()=>reply({detail:{error:'status_unavailable'}},status));
 const producer:DeletionProducer={submit:async()=>{throw Error('lost');},read:async(token)=>s.call('/__protocol_test_only__/deletion-status',{token}),verify:async()=>true};
 const client=new AccountDeletionClient(s.auth,s.call,store,producer,()=> 'unchanged-request');
 await client.submit('fixture-only');const result=await client.reconcile(),cleanup=jest.fn(async()=>undefined);
 expect(result.state).toBe('unknown');expect(await client.complete(result,cleanup)).toBe(false);expect(cleanup).not.toHaveBeenCalled();
 expect((await store.read(7))?.requestId).toBe('unchanged-request');expect(s.calls.filter(c=>c.path==='/auth/logout')).toHaveLength(0);
});

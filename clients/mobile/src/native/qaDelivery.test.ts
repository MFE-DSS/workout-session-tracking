/** SDK I/O is mocked; provenance selection and profile guard are real. */
const mockApplicationRead = jest.fn(()=>'0.0.2');
jest.mock('expo-application',()=>({
  get nativeApplicationVersion(){return mockApplicationRead();},nativeBuildVersion:'3',
}));
jest.mock('expo-updates',()=>({runtimeVersion:'runtime-A',updateId:null,isEmbeddedLaunch:true}));
import {observeQADelivery} from './qaDelivery';
const saved={...process.env};
beforeEach(()=>{delete process.env.EXPO_PUBLIC_QA_DELIVERY;mockApplicationRead.mockClear();});
afterAll(()=>{process.env=saved;});
test('non-QA observer has zero SDK reads and zero observation side effects',()=>{
  const sink=jest.fn();
  expect(observeQADelivery(sink)).toBeNull();
  expect(mockApplicationRead).not.toHaveBeenCalled(); expect(sink).not.toHaveBeenCalled();
});
test('new profile captures native and current JS identities with no owner or data',()=>{
  process.env.EXPO_PUBLIC_QA_DELIVERY='1';
  process.env.EXPO_PUBLIC_QA_NATIVE_SHA='a'.repeat(40);
  process.env.EXPO_PUBLIC_QA_JS_SHA='b'.repeat(40);
  const sink=jest.fn();
  const observation=observeQADelivery(sink);
  expect(observation).toEqual({schemaVersion:'qa-client-observation/1.0.0',
    nativeApplicationVersion:'0.0.2',nativeBuildVersion:'3',runtimeVersion:'runtime-A',
    updateId:null,isEmbeddedLaunch:true,nativeSourceSHA:'a'.repeat(40),currentJSSHA:'b'.repeat(40)});
  expect(sink).toHaveBeenCalledWith(observation);
});
test('OTA B changes JS/update identity while retaining immutable native identity A',()=>{
  process.env.EXPO_PUBLIC_QA_DELIVERY='1';
  process.env.EXPO_PUBLIC_QA_NATIVE_SHA='a'.repeat(40);process.env.EXPO_PUBLIC_QA_JS_SHA='b'.repeat(40);
  const updates=require('expo-updates');updates.updateId='actual-update-B';updates.isEmbeddedLaunch=false;
  expect(observeQADelivery(()=>{})).toMatchObject({nativeBuildVersion:'3',nativeSourceSHA:'a'.repeat(40),
    currentJSSHA:'b'.repeat(40),updateId:'actual-update-B',isEmbeddedLaunch:false});
});
test('unknown metadata stays null instead of claiming a native source from JS',()=>{
  process.env.EXPO_PUBLIC_QA_DELIVERY='1';delete process.env.EXPO_PUBLIC_QA_NATIVE_SHA;
  process.env.EXPO_PUBLIC_QA_JS_SHA='invalid';
  expect(observeQADelivery(()=>{})).toMatchObject({nativeSourceSHA:null,currentJSSHA:null});
});

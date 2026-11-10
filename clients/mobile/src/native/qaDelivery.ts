/** No eager native imports: ordinary consumers perform no QA SDK I/O or logging. */
import {qaDeliveryMetadata} from './qaDeliveryMetadata';
export type QADeliveryObservation={
  schemaVersion:'qa-client-observation/1.0.0';
  nativeApplicationVersion:string|null;nativeBuildVersion:string|null;
  runtimeVersion:string|null;updateId:string|null;isEmbeddedLaunch:boolean;
  nativeSourceSHA:string|null;currentJSSHA:string|null;
};
export function observeQADelivery(
  emit:(observation:QADeliveryObservation)=>void=(observation)=>console.info('AUREN_QA_DELIVERY',JSON.stringify(observation)),
):QADeliveryObservation|null {
  if(process.env.EXPO_PUBLIC_QA_DELIVERY!=='1') return null;
  const application:typeof import('expo-application')=require('expo-application');
  const updates:typeof import('expo-updates')=require('expo-updates');
  const observation:QADeliveryObservation={schemaVersion:'qa-client-observation/1.0.0',
    nativeApplicationVersion:application.nativeApplicationVersion,
    nativeBuildVersion:application.nativeBuildVersion,runtimeVersion:updates.runtimeVersion,
    updateId:updates.updateId,isEmbeddedLaunch:updates.isEmbeddedLaunch,...qaDeliveryMetadata()};
  emit(observation);
  return observation;
}

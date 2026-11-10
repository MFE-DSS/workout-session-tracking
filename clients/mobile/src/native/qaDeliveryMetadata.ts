/** Metro inlines EXPO_PUBLIC variables into JS only. Generated from a clean
 * checkout + immutable native receipt by releases.metadata_environment.
 * Never import these values into app.config or native extra/fingerprint.
 */
export function qaDeliveryMetadata() {
  const nativeSHA=process.env.EXPO_PUBLIC_QA_NATIVE_SHA;
  const jsSHA=process.env.EXPO_PUBLIC_QA_JS_SHA;
  const exact=(value:string|undefined)=>value && /^[a-f0-9]{40}$/.test(value)?value:null;
  return {nativeSourceSHA:exact(nativeSHA),currentJSSHA:exact(jsSHA)};
}

import { registerRootComponent } from 'expo';

import App from './App';
import ConnectedApp from './ConnectedApp';
import { CalibrationGallery } from './src/ui/calibration/CalibrationGallery';
import { InstrumentFrameGallery } from './src/ui/instrument/InstrumentFrameGallery';

// D9 — a build that names a backend (`EXPO_PUBLIC_API_URL`) is the connected app;
// without one it stays the N0 lab, on its canonical fixture, offline by design.
// DA-02.2 — EXPO_PUBLIC_GALLERY=calibration mounts the Calibration System's
// acceptance bench instead (design review only; never set in a product build);
// DA-02.3 — EXPO_PUBLIC_GALLERY=frame mounts the Instrument Frame exploration.
// registerRootComponent calls AppRegistry.registerComponent('main', () => App).
function root() {
  if (process.env.EXPO_PUBLIC_GALLERY === 'calibration') return CalibrationGallery;
  if (process.env.EXPO_PUBLIC_GALLERY === 'frame') return InstrumentFrameGallery;
  return process.env.EXPO_PUBLIC_API_URL ? ConnectedApp : App;
}
registerRootComponent(root());

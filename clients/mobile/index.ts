import { registerRootComponent } from 'expo';

import App from './App';
import ConnectedApp from './ConnectedApp';
import { CalibrationGallery } from './src/ui/calibration/CalibrationGallery';

// D9 — a build that names a backend (`EXPO_PUBLIC_API_URL`) is the connected app;
// without one it stays the N0 lab, on its canonical fixture, offline by design.
// DA-02.2 — EXPO_PUBLIC_GALLERY=calibration mounts the Calibration System's
// acceptance bench instead (design review only; never set in a product build).
// registerRootComponent calls AppRegistry.registerComponent('main', () => App).
function root() {
  if (process.env.EXPO_PUBLIC_GALLERY === 'calibration') return CalibrationGallery;
  return process.env.EXPO_PUBLIC_API_URL ? ConnectedApp : App;
}
registerRootComponent(root());

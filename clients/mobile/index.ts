import { registerRootComponent } from 'expo';

import App from './App';
import ConnectedApp from './ConnectedApp';

// D9 — a build that names a backend (`EXPO_PUBLIC_API_URL`) is the connected app;
// without one it stays the N0 lab, on its canonical fixture, offline by design.
// registerRootComponent calls AppRegistry.registerComponent('main', () => App).
registerRootComponent(process.env.EXPO_PUBLIC_API_URL ? ConnectedApp : App);

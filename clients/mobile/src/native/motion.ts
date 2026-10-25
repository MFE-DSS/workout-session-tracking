import { useEffect, useState } from 'react';
import { AccessibilityInfo } from 'react-native';

/** System "Reduce motion": every transition is cut, every screen stays readable. */
export function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    let alive = true;
    AccessibilityInfo.isReduceMotionEnabled().then((v) => alive && setReduced(v));
    const sub = AccessibilityInfo.addEventListener('reduceMotionChanged', setReduced);
    return () => {
      alive = false;
      sub.remove();
    };
  }, []);
  return reduced;
}

export function announce(message: string): void {
  AccessibilityInfo.announceForAccessibility(message);
}

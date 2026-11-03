/**
 * MOB-01 — the native shell: four spaces in the SYSTEM tab bar (operator D1 + D2), AUREN tints, template icons.
 * Mounted by ConnectedApp only outside a workout: the workout is a full-screen path above the tabs (ADR-3).
 */
import { usePathname, useRouter } from 'expo-router';
import { NativeTabs } from 'expo-router/native-tabs';
import React, { useEffect } from 'react';
import { BackHandler } from 'react-native';

import { backInShell, Space } from '../native/shellNav';
import { color } from '../ui/theme';

const ICONS = {
  today: { default: require('../../assets/tabs/today_default.png'), selected: require('../../assets/tabs/today_selected.png') },
  programs: { default: require('../../assets/tabs/programs_default.png'), selected: require('../../assets/tabs/programs_selected.png') },
  progress: { default: require('../../assets/tabs/progress_default.png'), selected: require('../../assets/tabs/progress_selected.png') },
  profile: { default: require('../../assets/tabs/profile_default.png'), selected: require('../../assets/tabs/profile_selected.png') },
};

const SPACE_OF: Record<string, Space> = { '/': 'today', '/programmes': 'programs', '/progres': 'progress', '/profil': 'profile' };

export default function ShellLayout() {
  const router = useRouter();
  const pathname = usePathname();

  // spec « Retour Android dans la coque » — decided by the tested pure function, not by the tab bar's default
  useEffect(() => {
    const sub = BackHandler.addEventListener('hardwareBackPress', () => {
      const action = backInShell({ space: SPACE_OF[pathname] ?? 'today', depth: 0 });
      if (action === 'first-space') {
        router.navigate('/');
        return true;
      }
      if (action === 'pop') {
        router.back();
        return true;
      }
      return false;
    });
    return () => sub.remove();
  }, [pathname, router]);

  return (
    <NativeTabs
      backgroundColor={color.plate}
      iconColor={{ default: color.ink3, selected: color.ink }}
      labelStyle={{ default: { color: color.ink3 }, selected: { color: color.ink } }}
      indicatorColor={color.line}
      labelVisibilityMode="labeled"
    >
      <NativeTabs.Trigger name="index">
        <NativeTabs.Trigger.Icon src={ICONS.today} />
        <NativeTabs.Trigger.Label>Aujourd’hui</NativeTabs.Trigger.Label>
      </NativeTabs.Trigger>
      <NativeTabs.Trigger name="programmes">
        <NativeTabs.Trigger.Icon src={ICONS.programs} />
        <NativeTabs.Trigger.Label>Programmes</NativeTabs.Trigger.Label>
      </NativeTabs.Trigger>
      <NativeTabs.Trigger name="progres">
        <NativeTabs.Trigger.Icon src={ICONS.progress} />
        <NativeTabs.Trigger.Label>Progrès</NativeTabs.Trigger.Label>
      </NativeTabs.Trigger>
      <NativeTabs.Trigger name="profil">
        <NativeTabs.Trigger.Icon src={ICONS.profile} />
        <NativeTabs.Trigger.Label>Profil</NativeTabs.Trigger.Label>
      </NativeTabs.Trigger>
    </NativeTabs>
  );
}

/**
 * MOB-01 — what the connected app hands to the shell (`openspec/changes/native-navigation-shell`, ADR-3).
 *
 * `ConnectedApp` stays the ONE owner of the workout state (journal, outbox, sync): the shell reads, it never keeps a
 * second copy. The MISSION space renders the node `ConnectedApp` already built for it; the other spaces are not
 * migrated yet and only need the way to open the journal sheet and the site.
 */
import React, { createContext, useContext } from 'react';

export type Shell = {
  /** MISSION, or its quiet states (loading, offline, nothing to propose) — built by ConnectedApp */
  today: React.ReactNode;
  openJournal: () => void;
  /** the web app this build talks to (`EXPO_PUBLIC_API_URL`), for the not-yet-migrated spaces */
  siteUrl: string;
  /** Native MOB-03 account settings, independent from the future full training profile. */
  account?: React.ReactNode;
  /** MOB-05A owned read-only history, mounted only by the focused Progress route. */
  progress?: React.ReactNode;
};

const ShellContext = createContext<Shell | null>(null);

export const ShellProvider = ShellContext.Provider;

export function useShell(): Shell {
  const shell = useContext(ShellContext);
  if (!shell) throw new Error('useShell outside ShellProvider');
  return shell;
}

import React, { useEffect, useState } from 'react';
import { Share, Text, View } from 'react-native';

import { buildEvidence, Evidence } from '../lab/evidence';
import { buildIdentity, deviceIdentity } from '../native/deviceInfo';
import type { Journal, Metric, Restored } from '../storage/journalTypes';
import { PrimaryAction, Sheet, SheetRow } from './components';
import { color, space, type } from './theme';

function line(s: Evidence['ux']['g_val_ms']): string {
  return s.n ? `n=${s.n} · médiane ${s.median} ms · p95 ${s.p95} ms · pire ${s.worst} ms` : 'aucune mesure';
}

/**
 * Lab instrumentation — not a product screen. It shows and EXPORTS the
 * PHYSICAL_DEVICE_GATE evidence record: the same schema on every platform
 * (`src/lab/evidence.ts`), operator observations left blank for the operator.
 */
export function LabSheet(props: {
  visible: boolean;
  journal: Journal | null;
  plannedSets: number | null;
  reduceMotionEnabled: boolean;
  onClose: () => void;
  onReset: () => void;
  onSeeded: () => void;
}) {
  const [data, setData] = useState<Restored | null>(null);
  const [metrics, setMetrics] = useState<Metric[]>([]);
  useEffect(() => {
    if (!props.visible || !props.journal) return;
    void props.journal.restore().then(setData).catch(() => undefined);
    void props.journal.metrics().then(setMetrics).catch(() => undefined);
  }, [props.visible, props.journal]);

  const evidence = buildEvidence({
    device: deviceIdentity(),
    build: buildIdentity(),
    metrics,
    journal: data?.sets ?? [],
    outbox: data?.outbox ?? [],
    plannedSets: props.plannedSets,
    reduceMotionEnabled: props.reduceMotionEnabled,
    capturedAtMs: Date.now(),
  });
  const d = evidence.device;

  return (
    <Sheet visible={props.visible} title="Journal local du labo" onClose={props.onClose}>
      <Text style={[type.small, { marginBottom: 8 }]}>
        {props.journal?.kind === 'sqlite'
          ? 'Expo SQLite sur l’appareil. Pas d’API dans N0 : les commandes restent en attente, c’est attendu.'
          : 'Aperçu web : journal EN MÉMOIRE — il ne prouve aucune durabilité.'}
      </Text>
      <SheetRow
        title={`${d.platform} · ${d.model ?? '?'} · OS ${d.os_version ?? '?'}`}
        detail={d.physical ? 'appareil PHYSIQUE — compte pour la porte' : 'simulateur / émulateur — ne compte PAS pour la porte'}
      />
      <SheetRow title={`${evidence.persistence.journal_sets} série(s) au journal`} detail={`${evidence.persistence.outbox_pending} commande(s) en attente · relances restaurées : ${evidence.persistence.relaunch_restores} · échecs d’enregistrement : ${evidence.persistence.commit_failures}`} />
      <SheetRow title="Valider → repos visible (G-VAL)" detail={line(evidence.ux.g_val_ms)} />
      <SheetRow title="Commit local journal + outbox (G-LOCAL)" detail={line(evidence.ux.g_local_ms)} />
      <SheetRow title="Fin de repos détectée — app au premier plan" detail={line(evidence.timer.foreground_end_lateness_ms)} />
      <SheetRow title="Fin de repos détectée — au retour dans l’app" detail={line(evidence.timer.resume_end_lateness_ms)} />
      <SheetRow title="Notification de fin de repos — retard OS (mesure)" detail={`${evidence.native_feedback.rest_notifications_requested} demandée(s) · ${line(evidence.native_feedback.rest_notification_delay_ms)}`} />
      <SheetRow title="Séance" detail={`${evidence.state.sets_validated}/${evidence.state.sets_planned ?? '?'} séries · ${evidence.state.automatic_set_transitions} enchaînements de série · ${evidence.state.automatic_exercise_transitions} d’exercice · ${evidence.state.navigation_decisions} décision(s) de navigation`} />
      <View style={{ marginTop: space.l, gap: 10 }}>
        <PrimaryAction
          tone="quiet"
          label="Exporter la preuve (JSON)"
          onPress={() => {
            void Share.share({ message: JSON.stringify(evidence, null, 2) }).catch(() => undefined);
          }}
        />
        <Text style={[type.small, { color: color.ink3 }]}>
          Preuve de durabilité : valide une série, attends « enregistrée sur l’appareil », force la fermeture de l’app, rouvre-la. La série doit être là.
        </Text>
        <PrimaryAction tone="quiet" label="Rejouer le premier lancement" sublabel="Efface tout : profil, séances, journal" onPress={props.onReset} />
        <PrimaryAction tone="quiet" label="Passer à l’utilisateur avec historique" sublabel="Deux semaines de séances semées" onPress={props.onSeeded} />
      </View>
    </Sheet>
  );
}

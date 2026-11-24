/** Approved MOB06 and DA09 G1, using the existing AUREN controls. */
import React, { useState } from 'react';
import { FlatList, ScrollView, Text, View, useWindowDimensions } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import type { LibraryDetail, LibraryEntry, LibraryQuery } from '../../api/library';
import type { LibraryState } from '../../api/libraryResource';
import type { LibrarySessionIdentity } from '../../storage/libraryPendingOpenings';
import type { LibraryOpeningState } from '../../sync/libraryOpening';
import { AurenMark } from '../brand/AurenMark';
import { SessionBodyMap } from '../bodymap/BodyMapTriptych';
import { presetForZone } from '../bodymap/viewPresets';
import { EmbeddedAction as CalibrationAction } from '../body/EmbeddedAction';
import { LibraryCountStructure, LibraryPrescription, LibraryProgramSequence, LibraryTechniqueSources } from '../cockpit/LibraryStructure';
import { CalibrationChoices, CalibrationLink } from '../plan/calibrationControls';
import { color, space, type } from '../theme';

export type LibraryScreenProps = {
  state: LibraryState;
  opening: LibraryOpeningState;
  query: LibraryQuery;
  existingSession?: LibrarySessionIdentity | null;
  onFilter: (section: LibraryQuery['section']) => void;
  onRefresh: () => void;
  onMore: () => void;
  onSelect: (ref: string) => void;
  onBack: () => void;
  onAskStart: () => void;
  onConfirm: () => void;
  onVerify: () => void;
  onResume: () => void;
  onCancel: (confirmed: boolean) => void;
  onResumeExisting: () => void;
  onBuilder?: () => void;
};

const labels = { programs: 'Mes programmes', core: 'Catalogue', utility: 'Compléments', specialization: 'Spécialisation' };
const statuses = { AVAILABLE: 'Catalogue', DRAFT: 'Brouillon', VALIDATED: 'Validé · non publié', PUBLISHED: 'Publié' };
const previousLabel = (at?: number) => at === undefined
  ? 'Lecture précédente · à actualiser'
  : `Lecture précédente · reçue le ${new Date(at).toLocaleString('fr-FR', {
    year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', timeZoneName: 'short',
  })}`;
const readStatus = (status: string) => {
  if (status === 'pending' || status === 'idle') return 'Lecture de la bibliothèque…';
  if (status === 'changed') return 'La source a changé · actualise la lecture.';
  if (status === 'unavailable') return 'Bibliothèque indisponible.';
  return 'Lecture non confirmée.';
};

function indexEntryMatchesDetail(entry: LibraryEntry, detail: LibraryDetail) {
  const { source, composition, limitations } = detail;
  if (entry.kind !== source.kind || entry.source_status !== source.status || entry.name !== source.name ||
      limitations.includes('PRESCRIPTION_PARTIAL')) return false;

  const counts = entry.counts;
  const exercises = composition.flatMap(row => row.exercises);
  if (counts.sessions !== null && counts.sessions !== composition.length) return false;
  if (counts.exercise_slots !== null && counts.exercise_slots !== exercises.length) return false;
  if (counts.prescribed_sets === null) return true;

  // The index counts work targets for owned programmes and all targets for catalogue sessions.
  const sets = exercises.reduce((total, exercise) => total + (source.kind === 'OWNED_PROGRAM'
    ? exercise.rep_targets.filter(target => !target.is_warmup).length
    : exercise.rep_targets.length), 0);
  return counts.prescribed_sets === sets;
}

function LibrarySources({ detail, entry, width }: { detail: LibraryDetail; entry?: LibraryEntry; width: number }) {
  const [expanded, setExpanded] = useState(false);
  const zones = entry?.zones.state === 'MAPPED'
    ? entry.zones.codes.map(presetForZone).filter(preset => preset !== undefined)
    : [];
  const exercises = detail.composition.flatMap(row => row.exercises);
  const compositionLabel = detail.source.kind === 'OWNED_PROGRAM' && detail.limitations.includes('PRESCRIPTION_PARTIAL')
    ? 'Composition reçue'
    : 'Composition prévue';
  return (
    <View style={{ gap: 6 }}>
      <CalibrationLink testID="library-sources" label="Sources et limites" expanded={expanded} onPress={() => setExpanded(!expanded)} />
      {expanded ? (
        <>
          {detail.composition.filter(row => row.notes).map(row => (
            <Text selectable key={row.source_ref} style={type.small}>{row.name} · {row.notes}</Text>
          ))}
          <LibraryTechniqueSources key={detail.read_revision} exercises={exercises} />
          <Text selectable style={type.small}>
            {compositionLabel} · {detail.source.kind === 'CATALOG_SESSION' ? 'catalogue' : `programme personnel, version ${detail.source.version}`} · source #{detail.source.id}
          </Text>
          <Text selectable style={type.small}>
            Ces prescriptions ne sont pas des séries effectuées. Aucune charge ni masse externe totale n’est déduite du catalogue.
          </Text>
          {exercises.filter(exercise => exercise.notes).map(exercise => (
            <Text selectable key={exercise.id} style={type.small}>{exercise.name} · {exercise.notes}</Text>
          ))}
          {zones.length > 0 ? (
            <View testID="library-zones" style={{ gap: 6 }}>
              <Text style={type.small}>Zones de la lecture de l’index</Text>
              <SessionBodyMap width={width} presets={zones} />
            </View>
          ) : null}
        </>
      ) : null}
    </View>
  );
}

function OpeningControls({ opening, existingSession, onVerify, onResume, onCancel, onResumeExisting, onRefresh, sourceName }: {
  opening: LibraryOpeningState;
  existingSession?: LibrarySessionIdentity | null;
  onVerify: () => void;
  onResume: () => void;
  onCancel: (confirmed: boolean) => void;
  onResumeExisting: () => void;
  sourceName?: string;
  onRefresh: () => void;
}) {
  const [cancelFor, setCancelFor] = useState<string | null>(null);
  const { phase, pending, owned, code } = opening;
  const unresolved = phase === 'unknown' || (phase === 'owned_found' && Boolean(pending));
  const intention = pending?.local_id ?? phase;
  const cancel = cancelFor === intention;
  if (phase === 'unknown' || phase === 'owned_found') {
    return (
      <View style={{ gap: 8 }}>
        {unresolved ? (
          <>
            <Text accessibilityRole="header" style={type.bodyStrong}>Départ à vérifier</Text>
            <Text selectable style={type.small}>
              Création initiale inconnue{sourceName ? ` · ${sourceName}` : ''}
            </Text>
          </>
        ) : null}
        {phase === 'owned_found' ? (
          <View style={{ gap: 4 }}>
            <Text accessibilityRole="header" style={type.bodyStrong}>Séance déjà ouverte</Text>
            <CalibrationAction
              testID="library-resume-found"
              label={owned ? `Reprendre la séance #${owned.session_id} · ${owned.session_profile === 'PLAN_V3' ? 'PLAN' : 'journal'}` : 'Reprendre cette séance'}
              onPress={onResume}
            />
          </View>
        ) : (
          <CalibrationAction testID="library-verify" primary label="Vérifier le départ" onPress={onVerify} />
        )}
        {unresolved ? (
          <CalibrationLink
            testID="library-cancel-options"
            label="Options de l’intention"
            expanded={cancel}
            onPress={() => setCancelFor(cancel ? null : intention)}
          />
        ) : null}
        {unresolved && cancel ? (
          <View>
            <Text selectable style={type.small}>Cela n’annule aucune séance sur le serveur.</Text>
            <CalibrationLink testID="library-cancel-confirm" label="Annuler l’intention sur cet appareil" onPress={() => onCancel(true)} />
          </View>
        ) : null}
      </View>
    );
  }
  const refusal = code === 'session_open'
    ? 'une séance est déjà ouverte'
    : code === 'stale_selection' ? 'la sélection a changé. Actualise la bibliothèque.' : 'conditions de départ non réunies';
  return (
    <View style={{ gap: 4 }}>
      {phase === 'refused' && code === 'stale_selection' ? <CalibrationLink testID="library-refresh-refusal" label="Actualiser la bibliothèque" onPress={onRefresh} /> : null}
      {phase === 'hydrating' || phase === 'submitting' ? (
        <Text accessibilityLiveRegion="polite" style={type.small}>{phase === 'hydrating' ? 'Vérification locale…' : 'Départ en cours…'}</Text>
      ) : null}
      {phase === 'unavailable' ? (
        <>
          <Text style={type.small}>Vérification indisponible · aucun nouveau départ.</Text>
          <CalibrationAction testID="library-verify" label="Vérifier la séance ouverte" onPress={onVerify} />
        </>
      ) : null}
      {existingSession ? (
        <View style={{ gap: 4 }}>
          <Text style={type.small}>Séance #{existingSession.session_id} déjà ouverte</Text>
          <CalibrationAction testID="library-resume-existing" label="Reprendre" onPress={onResumeExisting} />
        </View>
      ) : null}
      {phase === 'refused' && code === 'session_open' ? (
        <CalibrationAction testID="library-verify" label="Vérifier la séance ouverte" onPress={onVerify} />
      ) : null}
      {phase === 'refused' ? <Text selectable accessibilityLiveRegion="polite" style={type.small}>Départ refusé · {refusal}</Text> : null}
      {phase === 'created' || phase === 'resumed' ? (
        <Text accessibilityLiveRegion="polite" style={type.small}>Séance ouverte dans le journal possédé</Text>
      ) : null}
    </View>
  );
}

export function LibraryScreen(p: LibraryScreenProps) {
  const insets = useSafeAreaInsets();
  const { width, fontScale } = useWindowDimensions();
  const [filters, setFilters] = useState(false);
  const { state, opening } = p;
  const { index, detail, view, selectedRef } = state;
  const page = index.value;
  const data = detail.value;
  const prescriptionPartial = data?.limitations.includes('PRESCRIPTION_PARTIAL') ?? false;
  const selection = data?.selection;
  const session = data && data.source.kind !== 'OWNED_PROGRAM' ? data.composition[0] : undefined;
  const indexEntry = data && page?.owner_id === data.owner_id &&
    index.status === 'confirmed' && !index.previous && detail.status === 'confirmed' && !detail.previous
    ? page.entries.find(entry => entry.source_ref === selectedRef)
    : undefined;
  const selectedEntry = indexEntry && data && indexEntryMatchesDetail(indexEntry, data) ? indexEntry : undefined;
  const pendingRef = opening.pending?.source_ref;
  const pendingName = pendingRef && pendingRef === selectedRef && data
    ? data.source.name
    : page?.entries.find(entry => entry.source_ref === pendingRef)?.name;
  const canStart = detail.status === 'confirmed' && !detail.previous && session !== undefined &&
    session.source_ref === selectedRef && (data?.source.status === 'AVAILABLE' || data?.source.status === 'PUBLISHED') &&
    Boolean(selection?.selection_ref) && selection?.domain_launchable === true &&
    selection.native_support.state === 'SUPPORTED' && !p.existingSession &&
    (opening.phase === 'idle' || opening.phase === 'refused') &&
    opening.code !== 'session_open' && opening.code !== 'stale_selection';

  const header = (
    <View style={{ gap: 8 }}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
        {view !== 'INDEX'
          ? <CalibrationLink testID="library-back" label="Retour" onPress={p.onBack} />
          : <Text accessibilityRole="header" style={type.bodyStrong}>Programmes</Text>}
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
          <AurenMark size={20} color={color.ink} />
          <Text style={type.eyebrow}>AUREN</Text>
        </View>
        {view === 'INDEX' ? (
          <CalibrationLink testID="library-filter" label="Filtrer" expanded={filters} onPress={() => setFilters(!filters)} />
        ) : null}
      </View>
      <OpeningControls
        opening={opening} existingSession={p.existingSession} sourceName={pendingName}
        onVerify={p.onVerify} onResume={p.onResume} onCancel={p.onCancel} onResumeExisting={p.onResumeExisting} onRefresh={p.onRefresh}
      />
    </View>
  );
  const padding = { paddingHorizontal: space.gutter, paddingTop: insets.top + 8, paddingBottom: insets.bottom + 12, gap: 16 };

  if (view === 'INDEX') {
    return (
      <FlatList<LibraryEntry>
        style={{ flex: 1, backgroundColor: color.field }}
        contentInsetAdjustmentBehavior="never"
        contentContainerStyle={padding}
        keyboardShouldPersistTaps="handled"
        data={page?.entries ?? []}
        keyExtractor={entry => entry.source_ref}
        initialNumToRender={8}
        ListHeaderComponent={
          <View style={{ gap: 8 }}>
            {header}
            {p.onBuilder ? <CalibrationLink testID="library-builder" label="Mes brouillons · Créer un programme" onPress={p.onBuilder} /> : null}
            {filters ? (
              <CalibrationChoices
                label="Sources" value={p.query.section} options={[
                  { value: 'all', label: 'Tout' }, { value: 'programs', label: 'Mes programmes' },
                  { value: 'core', label: 'Catalogue' }, { value: 'utility', label: 'Compléments' },
                  { value: 'specialization', label: 'Spécialisation' },
                ]} onChange={p.onFilter}
              />
            ) : null}
            {index.previous ? <Text testID="library-previous" style={type.small}>{previousLabel(index.receivedAtMs)}</Text> : null}
            {index.status !== 'confirmed' ? <Text accessibilityLiveRegion="polite" style={type.small}>{readStatus(index.status)}</Text> : null}
            {p.query.section === 'all' && index.status === 'confirmed' && !page?.entries.some(entry => entry.kind === 'OWNED_PROGRAM')
              ? <Text style={type.small}>Aucun programme personnel.</Text> : null}
          </View>
        }
        renderItem={({ item, index: position }) => (
          <View style={{ paddingBottom: 8, borderBottomWidth: 1, borderBottomColor: color.line }}>
            {position === 0 || page?.entries[position - 1]?.section !== item.section ? (
              <Text testID={`library-section-${item.section}`} accessibilityRole="header" style={[type.eyebrow, { paddingBottom: 8 }]}>
                {labels[item.section]}
              </Text>
            ) : null}
            {item.kind === 'OWNED_PROGRAM' ? <Text style={type.small}>{statuses[item.source_status]} · programme personnel</Text> : null}
            <CalibrationLink
              testID={`library-entry-${item.source_ref}`}
              label={item.name}
              disabled={index.status !== 'confirmed' || index.previous}
              onPress={() => p.onSelect(item.source_ref)}
            />
            <LibraryCountStructure entry={item} />
          </View>
        )}
        ListEmptyComponent={index.status === 'confirmed' ? (
          <Text style={type.body}>{p.query.section === 'programs' ? 'Aucun programme personnel.' : 'Aucune séance dans cette sélection.'}</Text>
        ) : undefined}
        ListFooterComponent={
          <View style={{ gap: 4 }}>
            {page?.next_cursor && index.status === 'confirmed' ? <CalibrationLink label="Suite de la bibliothèque" onPress={p.onMore} /> : null}
            <CalibrationLink testID="library-refresh" label="Actualiser" disabled={index.status === 'pending'} onPress={p.onRefresh} />
          </View>
        }
      />
    );
  }

  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: color.field }} contentInsetAdjustmentBehavior="never"
      keyboardShouldPersistTaps="handled" contentContainerStyle={padding}
    >
      {header}
      {detail.previous ? <Text style={type.small}>{previousLabel(detail.receivedAtMs)}</Text> : null}
      {detail.status !== 'confirmed' ? <Text accessibilityLiveRegion="polite" style={type.small}>{readStatus(detail.status)}</Text> : null}
      {data?.source.kind === 'OWNED_PROGRAM' ? (
        <>
          <View style={{ gap: 6 }}>
            <Text style={type.small}>{statuses[data.source.status]} · programme personnel</Text>
            <Text selectable accessibilityRole="header" style={type.bodyStrong}>{data.source.name}</Text>
            {selectedEntry ? (
              <View style={{ gap: 6 }}>
                <Text style={type.small}>Résumé de la bibliothèque</Text>
                <LibraryCountStructure entry={selectedEntry} />
              </View>
            ) : null}
          </View>
          <View style={{ gap: 8 }}>
            <Text accessibilityRole="header" style={type.bodyStrong}>{prescriptionPartial ? 'Séances du programme' : 'Séances prévues'}</Text>
            {prescriptionPartial ? <Text style={type.small}>Prescription partielle</Text> : null}
            <LibraryProgramSequence
              key={selectedRef} sessions={data.composition} prescriptionPartial={prescriptionPartial}
              disabled={detail.status !== 'confirmed' || detail.previous} onSelect={p.onSelect}
            />
          </View>
        </>
      ) : null}
      {data && session ? (
        <View testID="library-selected-session" style={{ gap: 12 }}>
          <View style={{
            flexDirection: 'column',
            alignItems: 'stretch', gap: 8, paddingLeft: 12, borderLeftWidth: 2, borderLeftColor: color.signal,
          }}>
            <View style={{ minWidth: 0, gap: 4 }}>
              <Text style={type.small}>
                {data.source.kind === 'CATALOG_SESSION' ? 'Modèle du catalogue' : statuses[data.source.status]}
              </Text>
              <Text selectable accessibilityRole="header" style={[type.bodyStrong, { fontSize: 22, lineHeight: 26 }]}>{data.source.name}</Text>
            </View>
            {view !== 'CONFIRM' && selection?.selection_ref ? (
              <CalibrationAction testID="library-ask-start" label="Démarrer la séance" primary disabled={!canStart} onPress={p.onAskStart} />
            ) : null}
          </View>
          {selection?.native_support.state !== 'SUPPORTED' && selection ? <Text style={type.small}>Exécution native indisponible pour cette séance.</Text> : null}
          {selection && !selection.domain_launchable ? <Text style={type.small}>Cette séance n’est pas publiée pour le départ.</Text> : null}
          {view === 'CONFIRM' ? (
            <View style={{ gap: 8 }}>
              <Text style={type.small}>Les conditions actuelles seront vérifiées avant création.</Text>
              <CalibrationAction testID="library-confirm-start" label="Confirmer le départ" primary disabled={!canStart} onPress={p.onConfirm} />
              <CalibrationLink label="Annuler" onPress={p.onBack} />
            </View>
          ) : null}
          <View style={{ gap: 4 }}>
            <Text accessibilityRole="header" style={type.bodyStrong}>Prescription de la séance</Text>
            <Text testID="library-context" style={type.small}>Matériel non confirmé</Text>
            {prescriptionPartial ? <Text style={type.small}>Prescription partielle</Text> : null}
            <LibraryPrescription key={session.source_ref} exercises={session.exercises} />
          </View>
        </View>
      ) : null}
      {data ? (
        <LibrarySources key={selectedRef} detail={data} entry={selectedEntry} width={Math.max(1, width - 2 * space.gutter)} />
      ) : null}
    </ScrollView>
  );
}

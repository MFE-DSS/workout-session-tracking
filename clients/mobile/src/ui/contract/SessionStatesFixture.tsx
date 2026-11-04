/** MOB-02 : vrais composants sur données canoniques figées, revue uniquement, jamais un backend simulé de production.
 * Le vrai ConnectedApp et ses frontières sont exercés séparément par les tests de consommateur.
 */
import React from 'react';
import { View } from 'react-native';
import { SafeAreaFrameContext, SafeAreaInsetsContext } from 'react-native-safe-area-context';
import { sessionPerformance } from '../../domain/performance';
import { reduce } from '../../domain/workout';
import { setCommand, substituteCommand } from '../../storage/outbox';
import { reconcileSubstitutions } from '../../sync/substitutionState';
import { serverStateFromOutbox } from '../../sync/serverState';
import { summaryContext } from '../../sync/summaryContext';
import { BootScreen } from '../BootScreen';
import { CompleteScreen } from '../CompleteScreen';
import { ExecutionScreen, ExecutionHandlers } from '../ExecutionScreen';
import { MissionScreen } from '../MissionScreen';
import { ResumeScreen } from '../ResumeScreen';
import { color } from '../theme';
import { completedState } from './CompleteScreenFixture';
import { executionStateAt } from './ExecutionScreenFixture';
import { missionAt } from './MissionScreenFixture';

export type SessionReviewState = 'boot' | 'start-busy' | 'resume-one' | 'resume-busy' | 'sub-pending' | 'sub-refused' | 'bilan-no-frequency' | 'bilan-details';
const NOOP = () => undefined;
const BEFORE = process.env.EXPO_PUBLIC_MOB02_REVIEW_REVISION === 'before';
const HANDLERS: ExecutionHandlers = { onAdjust: NOOP, onSetValue: NOOP, onValidatePressIn: NOOP,
  onValidate: NOOP, onShift: NOOP, onSkip: NOOP, onRequestSubstitute: NOOP, onOpenLab: NOOP,
  onRestPainted: NOOP, onSecondaryOpened: NOOP, onExitRequested: NOOP, onSkipSet: NOOP };

export function SessionStatesFixture(p: { width: number; height: number; scenario: SessionReviewState }) {
  let body: React.ReactNode;
  if (p.scenario === 'boot') body = BEFORE ? null : <BootScreen />;
  else if (p.scenario === 'start-busy') body = <MissionScreen mission={missionAt('main')} busy
    onStart={NOOP} onOpenLab={NOOP} onSecondaryOpened={NOOP} today={new Date('2026-10-31T12:00:00Z')} />;
  else if (p.scenario === 'resume-one' || p.scenario === 'resume-busy') body = <ResumeScreen name="Push A" subtitle={null}
    busy={p.scenario === 'resume-busy'} position={{ exerciseIndex: 1, exerciseTotal: 7, setsDone: 1, setsTotal: 21,
      exerciseName: 'Développé' }} note={null} onResume={NOOP} onOpenJournal={NOOP} />;
  else if (p.scenario === 'bilan-no-frequency' || p.scenario === 'bilan-details') {
    const state = completedState('push-a');
    const rows = state.plan!.sets.slice(0, 3).map((set, index) => {
      const command = setCommand(`review-set-${index}`, state.plan!.session_id, set.set_id, 40, 8,
        { epochMs: state.completedMs!, estimated: false });
      return { ...command, payload: JSON.stringify(command.payload), created_at_ms: index + 1, attempts: 1,
        state: (['acked', 'pending', 'failed'] as const)[index] };
    });
    const delivery = serverStateFromOutbox(rows);
    body = <CompleteScreen state={state} performance={sessionPerformance(state.plan!, state.done, state.requiresSync)}
      history={p.scenario === 'bilan-details' ? null : []} sessionsPerWeek={null}
      serverStateOf={(id) => delivery[id] ?? 'unknown'} contextLine={BEFORE || p.scenario === 'bilan-details' ? null : summaryContext({ has_more: false, sessions: [{
        id: state.plan!.session_id, template_slug: state.plan!.template_slug,
        started_at: new Date(state.startedMs!).toISOString(), ended_at: new Date(state.completedMs!).toISOString(),
      }] }, state.plan!.session_id)} next={null} reducedMotion onClose={NOOP} onOpenLab={NOOP} />;
  } else {
    const initial = executionStateAt('push-a', 0, 'set');
    const ex = initial.state.plan!.exercises[0];
    const name = ex.substitutes[0];
    if (!name) throw new Error('La fixture canonique ne propose aucun remplacement');
    let state = reduce(initial.state, { type: 'REQUEST_SUBSTITUTE', seId: ex.se_id, substitute: name });
    if (p.scenario === 'sub-refused' && !BEFORE) {
      const command = substituteCommand('review-refused', state.plan!.session_id, ex.se_id, name);
      state = reconcileSubstitutions(state, [{ ...command, payload: JSON.stringify(command.payload),
        created_at_ms: 1, attempts: 1, state: 'failed' }]);
    }
    const refused = p.scenario === 'sub-refused';
    body = <ExecutionScreen state={state} nowMs={initial.nowMs} reducedMotion {...HANDLERS}
      offline={!refused} substitutionStateOf={() => refused ? 'failed' : 'pending'}
      statusNote={refused ? { text: BEFORE ? '1 enregistrement à vérifier — gardé sur l’appareil'
        : 'Le remplacement n’a pas été accepté.', alert: true } : null} />;
  }
  return <SafeAreaFrameContext.Provider value={{ x: 0, y: 0, width: p.width, height: p.height }}>
    <SafeAreaInsetsContext.Provider value={{ top: 47, bottom: 34, left: 0, right: 0 }}>
      <View testID="mob02-state" style={{ width: p.width, height: p.height, backgroundColor: color.field, overflow: 'hidden' }}>{body}</View>
    </SafeAreaInsetsContext.Provider>
  </SafeAreaFrameContext.Provider>;
}

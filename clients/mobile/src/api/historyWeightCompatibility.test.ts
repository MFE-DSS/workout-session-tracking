import type {WeightEntry} from './weightHistory';
import type {WeightWindowState} from './trainingHistoryResource';

// The existing history/chart consumers retain their strict legacy input type.
// This assignment must compile even while BODY has its own source-aware port.
function legacyEntries(state:WeightWindowState):WeightEntry[]{return state.entries;}
test('legacy history window stays usable by unchanged historical consumers',()=>{
 expect(legacyEntries({status:'confirmed',previous:false,coverage:'COMPLETE',canContinue:false,entries:[]})).toEqual([]);
});

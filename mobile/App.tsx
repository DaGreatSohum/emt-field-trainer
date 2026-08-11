import { StatusBar } from 'expo-status-bar';
import { useEffect, useMemo, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

const configuredApiUrl = process.env.EXPO_PUBLIC_API_URL;
if (!__DEV__ && (!configuredApiUrl || !configuredApiUrl.startsWith('https://'))) {
  throw new Error('Production builds require an HTTPS EXPO_PUBLIC_API_URL.');
}
const API_URL = (configuredApiUrl || 'http://127.0.0.1:8000/api').replace(/\/$/, '');

type Scenario = {
  key: string;
  title: string;
  category: string;
  difficulty: string;
  attempted: boolean;
  score: number | null;
  completed: boolean;
};

type Message = {
  id: string;
  role: 'trainer' | 'student' | 'feedback';
  text: string;
};

type Session = {
  attemptId: string;
  attemptToken: string;
  scenario: Scenario;
  step: number;
  totalSteps: number;
  messages: Message[];
};

type Result = {
  score: number;
  evaluation: string;
  matched: string[];
  missed: string[];
};

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || 'Request failed.');
  return body;
}

export default function App() {
  const [screen, setScreen] = useState<'home' | 'session' | 'result'>('home');
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [disclaimer, setDisclaimer] = useState('');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [answer, setAnswer] = useState('');
  const [session, setSession] = useState<Session | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const scrollRef = useRef<ScrollView>(null);

  const loadScenarios = async () => {
    setLoading(true);
    try {
      const data = await api<{ scenarios: Scenario[]; disclaimer: string }>('/scenarios/');
      setScenarios(data.scenarios);
      setDisclaimer(data.disclaimer);
    } catch (error) {
      Alert.alert('Cannot reach training server', `${(error as Error).message}\n\nAPI: ${API_URL}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadScenarios();
  }, []);

  const filtered = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!term) return scenarios;
    return scenarios.filter((item) =>
      `${item.title} ${item.category} ${item.difficulty}`.toLowerCase().includes(term),
    );
  }, [query, scenarios]);

  const startScenario = async (scenario: Scenario) => {
    setLoading(true);
    try {
      const data = await api<{
        attempt_id: string;
        attempt_token: string;
        dispatch: string;
        prompt: string;
        step: number;
        total_steps: number;
      }>(`/scenarios/${scenario.key}/start/`, { method: 'POST' });
      setSession({
        attemptId: data.attempt_id,
        attemptToken: data.attempt_token,
        scenario,
        step: data.step,
        totalSteps: data.total_steps,
        messages: [
          { id: 'dispatch', role: 'trainer', text: `DISPATCH\n${data.dispatch}` },
          { id: 'prompt-1', role: 'trainer', text: data.prompt },
        ],
      });
      setAnswer('');
      setResult(null);
      setScreen('session');
    } catch (error) {
      Alert.alert('Unable to start', (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!session || !answer.trim() || loading) return;
    const responseText = answer.trim();
    const turnId = `${session.step}-${session.messages.length}`;
    const studentMessage: Message = {
      id: `student-${turnId}`,
      role: 'student',
      text: responseText,
    };
    setAnswer('');
    setSession({ ...session, messages: [...session.messages, studentMessage] });
    setLoading(true);
    try {
      const data = await api<{
        completed: boolean;
        overall_score: number;
        feedback: string;
        prompt?: string;
        step?: number;
        total_steps?: number;
        evaluation?: string;
        matched: string[];
        missed: string[];
      }>(`/attempts/${session.attemptId}/respond/`, {
        method: 'POST',
        headers: { 'X-Attempt-Token': session.attemptToken },
        body: JSON.stringify({ response: responseText }),
      });
      const feedbackMessage: Message = {
        id: `feedback-${turnId}`,
        role: 'feedback',
        text: data.feedback,
      };
      if (data.completed) {
        setSession({
          ...session,
          step: session.totalSteps,
          messages: [...session.messages, studentMessage, feedbackMessage],
        });
        setResult({
          score: data.overall_score,
          evaluation: data.evaluation || '',
          matched: data.matched,
          missed: data.missed,
        });
        await loadScenarios();
      } else {
        setSession({
          ...session,
          step: data.step || session.step + 1,
          totalSteps: data.total_steps || session.totalSteps,
          messages: [
            ...session.messages,
            studentMessage,
            feedbackMessage,
            { id: `prompt-${turnId}`, role: 'trainer', text: data.prompt || '' },
          ],
        });
        setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);
      }
    } catch (error) {
      setAnswer(responseText);
      Alert.alert('Response not saved', (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const goHome = () => {
    setScreen('home');
    setSession(null);
    setResult(null);
    setAnswer('');
  };

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar style="light" />
      {screen === 'home' ? (
        <HomeScreen
          scenarios={filtered}
          query={query}
          onQuery={setQuery}
          loading={loading}
          disclaimer={disclaimer}
          onStart={startScenario}
          onRefresh={loadScenarios}
        />
      ) : null}
      {screen === 'session' && session ? (
        <SessionScreen
          session={session}
          answer={answer}
          setAnswer={setAnswer}
          loading={loading}
          onSubmit={submitAnswer}
          onBack={goHome}
          scrollRef={scrollRef}
          result={result}
          onRetry={() => startScenario(session.scenario)}
        />
      ) : null}
      {screen === 'result' && session && result ? (
        <ResultScreen result={result} scenario={session.scenario} onHome={goHome} onRetry={() => startScenario(session.scenario)} />
      ) : null}
    </SafeAreaView>
  );
}

function HomeScreen({
  scenarios,
  query,
  onQuery,
  loading,
  disclaimer,
  onStart,
  onRefresh,
}: {
  scenarios: Scenario[];
  query: string;
  onQuery: (text: string) => void;
  loading: boolean;
  disclaimer: string;
  onStart: (scenario: Scenario) => void;
  onRefresh: () => void;
}) {
  return (
    <View style={styles.flex}>
      <View style={styles.header}>
        <View style={styles.brandRow}>
          <View style={styles.starBadge}><Text style={styles.star}>✚</Text></View>
          <View>
            <Text style={styles.brand}>EMT FIELD TRAINER</Text>
            <Text style={styles.headerSub}>Interactive EMT scenario training</Text>
          </View>
        </View>
        <Text style={styles.greeting}>Ready for your next call?</Text>
        <Text style={styles.intro}>Choose a scenario and work through an adaptive, field-style patient encounter.</Text>
        <View style={styles.search}>
          <Text style={styles.searchIcon}>⌕</Text>
          <TextInput
            value={query}
            onChangeText={onQuery}
            placeholder="Search scenarios or categories"
            placeholderTextColor="#778294"
            style={styles.searchInput}
            autoCapitalize="none"
          />
        </View>
      </View>
      <ScrollView contentContainerStyle={styles.listContent}>
        <View style={styles.sectionRow}>
          <Text style={styles.sectionTitle}>Training scenarios</Text>
          <Text style={styles.count}>{scenarios.length} available</Text>
        </View>
        {loading && scenarios.length === 0 ? <ActivityIndicator size="large" color="#e64045" /> : null}
        {!loading && scenarios.length === 0 ? (
          <Pressable style={styles.empty} onPress={onRefresh}>
            <Text style={styles.emptyTitle}>No scenarios found</Text>
            <Text style={styles.emptyText}>Change your search or tap to retry the server.</Text>
          </Pressable>
        ) : null}
        {scenarios.map((scenario) => (
          <Pressable key={scenario.key} style={styles.scenarioCard} onPress={() => onStart(scenario)}>
            <View style={[styles.categoryStripe, categoryColor(scenario.category)]} />
            <View style={styles.scenarioBody}>
              <View style={styles.cardTop}>
                <View style={styles.grow}>
                  <Text style={styles.category}>{scenario.category.toUpperCase()}</Text>
                  <Text style={styles.scenarioTitle}>{scenario.title}</Text>
                </View>
                {scenario.attempted ? (
                  <View style={styles.scorePill}><Text style={styles.scoreText}>{scenario.score}%</Text></View>
                ) : (
                  <View style={styles.newPill}><Text style={styles.newText}>NEW</Text></View>
                )}
              </View>
              <View style={styles.metaRow}>
                <Text style={styles.meta}>{scenario.difficulty}</Text>
                <Text style={styles.startText}>{scenario.attempted ? 'Try again  ›' : 'Start  ›'}</Text>
              </View>
            </View>
          </Pressable>
        ))}
        <View style={styles.disclaimer}>
          <Text style={styles.disclaimerTitle}>TRAINING USE ONLY</Text>
          <Text style={styles.disclaimerText}>{disclaimer}</Text>
        </View>
      </ScrollView>
    </View>
  );
}

function SessionScreen({
  session,
  answer,
  setAnswer,
  loading,
  onSubmit,
  onBack,
  scrollRef,
  result,
  onRetry,
}: {
  session: Session;
  answer: string;
  setAnswer: (text: string) => void;
  loading: boolean;
  onSubmit: () => void;
  onBack: () => void;
  scrollRef: React.RefObject<ScrollView | null>;
  result: Result | null;
  onRetry: () => void;
}) {
  return (
    <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <View style={styles.sessionHeader}>
        <Pressable style={styles.backButton} onPress={onBack}><Text style={styles.backText}>‹</Text></Pressable>
        <View style={styles.sessionHeadText}>
          <Text style={styles.sessionTitle}>{session.scenario.title}</Text>
          <Text style={styles.sessionMeta}>{session.scenario.category} · {session.scenario.difficulty} · Step {session.step} of {session.totalSteps}</Text>
        </View>
        <View style={styles.livePill}><View style={styles.liveDot} /><Text style={styles.liveText}>LIVE</Text></View>
      </View>
      <View style={styles.progressTrack}>
        <View style={[styles.progressFill, { width: `${(session.step / session.totalSteps) * 100}%` }]} />
      </View>
      <ScrollView ref={scrollRef} style={styles.chat} contentContainerStyle={styles.chatContent} keyboardShouldPersistTaps="handled">
        <Text style={styles.chatDate}>FIELD SIMULATION</Text>
        {session.messages.map((message) => (
          <View key={message.id} style={[
            styles.bubble,
            message.role === 'student' ? styles.studentBubble : message.role === 'feedback' ? styles.feedbackBubble : styles.trainerBubble,
          ]}>
            <Text style={message.role === 'student' ? styles.studentText : styles.bubbleText}>{message.text}</Text>
          </View>
        ))}
        {loading ? <ActivityIndicator style={styles.chatLoader} color="#e64045" /> : null}
      </ScrollView>
      {result ? (
        <View style={styles.completionToast}>
          <Text style={styles.completionEyebrow}>ENCOUNTER COMPLETE</Text>
          <Text style={styles.completionScore}>{result.score}%</Text>
          <Text style={styles.completionText}>{result.evaluation}</Text>
          <View style={styles.completionActions}>
            <Pressable style={styles.completionPrimary} onPress={onRetry}>
              <Text style={styles.completionPrimaryText}>Repeat</Text>
            </Pressable>
            <Pressable style={styles.completionSecondary} onPress={onBack}>
              <Text style={styles.completionSecondaryText}>All scenarios</Text>
            </Pressable>
          </View>
        </View>
      ) : null}
      <View style={styles.composer}>
        <TextInput
          value={answer}
          onChangeText={setAnswer}
          placeholder="Describe what you would do…"
          placeholderTextColor="#7b8490"
          multiline
          style={styles.composerInput}
          editable={!loading && !result}
        />
        <Pressable
          style={[styles.sendButton, (!answer.trim() || loading || Boolean(result)) && styles.sendDisabled]}
          disabled={!answer.trim() || loading || Boolean(result)}
          onPress={onSubmit}
        >
          <Text style={styles.sendText}>↑</Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

function ResultScreen({
  result,
  scenario,
  onHome,
  onRetry,
}: {
  result: Result;
  scenario: Scenario;
  onHome: () => void;
  onRetry: () => void;
}) {
  return (
    <ScrollView style={styles.flex} contentContainerStyle={styles.resultContent}>
      <Text style={styles.resultEyebrow}>SCENARIO COMPLETE</Text>
      <Text style={styles.resultTitle}>{scenario.title}</Text>
      <View style={styles.scoreCircle}>
        <Text style={styles.bigScore}>{result.score}</Text>
        <Text style={styles.percent}>%</Text>
      </View>
      <Text style={styles.evaluation}>{result.evaluation}</Text>
      <View style={styles.resultCard}>
        <Text style={styles.resultCardTitle}>Final-step strengths</Text>
        <Text style={styles.resultDetail}>{result.matched.length ? result.matched.join(' · ') : 'No expected concepts matched.'}</Text>
      </View>
      <View style={[styles.resultCard, styles.reviewCard]}>
        <Text style={styles.reviewTitle}>Review before your next attempt</Text>
        <Text style={styles.resultDetail}>{result.missed.length ? result.missed.join(' · ') : 'No missed items — excellent work.'}</Text>
      </View>
      <Pressable style={styles.primaryButton} onPress={onRetry}><Text style={styles.primaryButtonText}>Repeat scenario</Text></Pressable>
      <Pressable style={styles.secondaryButton} onPress={onHome}><Text style={styles.secondaryButtonText}>Back to scenarios</Text></Pressable>
      <Text style={styles.protocolNote}>Independent educational scenario · Training use only</Text>
    </ScrollView>
  );
}

const categoryColor = (category: string) => ({
  backgroundColor:
    category === 'Cardiac' ? '#e64045' :
    category === 'Respiratory' ? '#2b78c5' :
    category === 'Trauma' ? '#e78a2f' :
    category === 'Neurologic' ? '#7057b8' :
    category === 'Toxicology' ? '#269579' : '#3d6c91',
});

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#12283d' },
  flex: { flex: 1, backgroundColor: '#f3f6f8' },
  grow: { flex: 1 },
  header: { backgroundColor: '#12283d', paddingHorizontal: 20, paddingTop: 12, paddingBottom: 24 },
  brandRow: { flexDirection: 'row', alignItems: 'center' },
  starBadge: { width: 38, height: 38, borderRadius: 12, backgroundColor: '#e64045', alignItems: 'center', justifyContent: 'center', marginRight: 11 },
  star: { color: '#fff', fontSize: 23, fontWeight: '800' },
  brand: { color: '#fff', letterSpacing: 1.4, fontSize: 13, fontWeight: '900' },
  headerSub: { color: '#a9bbc9', fontSize: 12, marginTop: 2 },
  greeting: { color: '#fff', fontSize: 27, fontWeight: '900', marginTop: 25, letterSpacing: -0.6 },
  intro: { color: '#c5d1db', lineHeight: 20, fontSize: 14, marginTop: 7, maxWidth: 370 },
  search: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderRadius: 14, marginTop: 18, minHeight: 48, paddingHorizontal: 14 },
  searchIcon: { fontSize: 24, color: '#596879', marginRight: 8 },
  searchInput: { flex: 1, color: '#18283a', fontSize: 15, paddingVertical: 12 },
  listContent: { padding: 18, paddingBottom: 40 },
  sectionRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  sectionTitle: { color: '#172b3e', fontSize: 18, fontWeight: '800' },
  count: { color: '#718091', fontSize: 12, fontWeight: '600' },
  scenarioCard: { flexDirection: 'row', overflow: 'hidden', backgroundColor: '#fff', borderRadius: 16, marginBottom: 12, borderWidth: 1, borderColor: '#e2e8ed', shadowColor: '#142638', shadowOpacity: 0.05, shadowRadius: 10, shadowOffset: { width: 0, height: 4 }, elevation: 2 },
  categoryStripe: { width: 6 },
  scenarioBody: { padding: 15, flex: 1 },
  cardTop: { flexDirection: 'row', alignItems: 'flex-start' },
  category: { color: '#758292', fontSize: 10, fontWeight: '800', letterSpacing: 1 },
  scenarioTitle: { color: '#162b3e', fontSize: 17, fontWeight: '800', marginTop: 4 },
  scorePill: { backgroundColor: '#e8f6ef', borderRadius: 10, paddingHorizontal: 9, paddingVertical: 6 },
  scoreText: { color: '#197450', fontSize: 12, fontWeight: '800' },
  newPill: { backgroundColor: '#edf3f8', borderRadius: 10, paddingHorizontal: 9, paddingVertical: 6 },
  newText: { color: '#3a617e', fontSize: 10, fontWeight: '900', letterSpacing: 0.8 },
  metaRow: { flexDirection: 'row', alignItems: 'center', marginTop: 13 },
  meta: { color: '#748190', fontSize: 12 },
  dot: { color: '#a4aeba', marginHorizontal: 7 },
  startText: { marginLeft: 'auto', color: '#d7353b', fontSize: 12, fontWeight: '800' },
  empty: { backgroundColor: '#fff', borderRadius: 16, padding: 28, alignItems: 'center' },
  emptyTitle: { color: '#172b3e', fontWeight: '800', fontSize: 17 },
  emptyText: { color: '#718091', textAlign: 'center', marginTop: 6 },
  disclaimer: { backgroundColor: '#e9eef2', borderRadius: 14, padding: 15, marginTop: 8 },
  disclaimerTitle: { color: '#52606d', fontSize: 10, letterSpacing: 1, fontWeight: '900' },
  disclaimerText: { color: '#65727f', fontSize: 11, lineHeight: 17, marginTop: 5 },
  sessionHeader: { height: 68, backgroundColor: '#12283d', flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14 },
  backButton: { width: 38, height: 38, borderRadius: 12, backgroundColor: '#203a51', alignItems: 'center', justifyContent: 'center' },
  backText: { color: '#fff', fontSize: 30, lineHeight: 32 },
  sessionHeadText: { flex: 1, marginLeft: 12 },
  sessionTitle: { color: '#fff', fontSize: 16, fontWeight: '800' },
  sessionMeta: { color: '#aab9c6', fontSize: 11, marginTop: 3 },
  livePill: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#203a51', paddingHorizontal: 8, paddingVertical: 6, borderRadius: 10 },
  liveDot: { width: 7, height: 7, borderRadius: 4, backgroundColor: '#63d39a', marginRight: 5 },
  liveText: { color: '#cfe9dc', fontSize: 9, fontWeight: '900', letterSpacing: 0.8 },
  progressTrack: { height: 4, backgroundColor: '#d9e0e5' },
  progressFill: { height: 4, backgroundColor: '#e64045' },
  chat: { flex: 1, backgroundColor: '#f3f6f8' },
  chatContent: { padding: 16, paddingBottom: 24 },
  chatDate: { alignSelf: 'center', color: '#83909d', fontSize: 10, letterSpacing: 1.2, fontWeight: '800', marginVertical: 7 },
  bubble: { maxWidth: '88%', paddingHorizontal: 15, paddingVertical: 12, borderRadius: 17, marginTop: 10 },
  trainerBubble: { backgroundColor: '#fff', alignSelf: 'flex-start', borderBottomLeftRadius: 5, borderWidth: 1, borderColor: '#e0e6eb' },
  studentBubble: { backgroundColor: '#173d5b', alignSelf: 'flex-end', borderBottomRightRadius: 5 },
  feedbackBubble: { backgroundColor: '#e7f5ed', alignSelf: 'flex-start', borderBottomLeftRadius: 5, borderWidth: 1, borderColor: '#c7e8d5' },
  bubbleText: { color: '#263b4d', fontSize: 15, lineHeight: 22 },
  studentText: { color: '#fff', fontSize: 15, lineHeight: 22 },
  chatLoader: { marginTop: 16 },
  composer: { backgroundColor: '#fff', borderTopWidth: 1, borderTopColor: '#dfe5e9', flexDirection: 'row', alignItems: 'flex-end', padding: 10 },
  composerInput: { flex: 1, minHeight: 45, maxHeight: 110, backgroundColor: '#f0f3f5', borderRadius: 15, color: '#1c3042', paddingHorizontal: 14, paddingTop: 12, paddingBottom: 10, fontSize: 15 },
  sendButton: { width: 45, height: 45, borderRadius: 15, backgroundColor: '#e64045', alignItems: 'center', justifyContent: 'center', marginLeft: 8 },
  sendDisabled: { backgroundColor: '#b8c0c7' },
  sendText: { color: '#fff', fontSize: 24, fontWeight: '800' },
  completionToast: { position: 'absolute', right: 14, bottom: 76, width: 310, maxWidth: '92%', zIndex: 5, padding: 16, borderRadius: 16, backgroundColor: '#f2fbf6', borderWidth: 1, borderColor: '#b9daca', shadowColor: '#10283c', shadowOpacity: 0.2, shadowRadius: 18, shadowOffset: { width: 0, height: 8 }, elevation: 8 },
  completionEyebrow: { color: '#16815b', fontSize: 10, fontWeight: '900', letterSpacing: 1.2 },
  completionScore: { color: '#12283d', fontSize: 27, fontWeight: '900', marginTop: 5 },
  completionText: { color: '#49685a', fontSize: 12, lineHeight: 18, marginTop: 4 },
  completionActions: { flexDirection: 'row', gap: 8, marginTop: 12 },
  completionPrimary: { flex: 1, paddingVertical: 10, alignItems: 'center', borderRadius: 10, backgroundColor: '#e64045' },
  completionPrimaryText: { color: '#fff', fontWeight: '900' },
  completionSecondary: { flex: 1, paddingVertical: 10, alignItems: 'center', borderRadius: 10, backgroundColor: '#fff', borderWidth: 1, borderColor: '#bdd4c8' },
  completionSecondaryText: { color: '#254157', fontWeight: '800' },
  resultContent: { backgroundColor: '#f3f6f8', minHeight: '100%', alignItems: 'center', padding: 24, paddingTop: 44 },
  resultEyebrow: { color: '#d6383e', fontWeight: '900', fontSize: 11, letterSpacing: 1.5 },
  resultTitle: { color: '#162b3e', fontSize: 26, fontWeight: '900', marginTop: 9, textAlign: 'center' },
  scoreCircle: { width: 138, height: 138, borderRadius: 69, backgroundColor: '#173d5b', alignItems: 'center', justifyContent: 'center', flexDirection: 'row', marginTop: 25, borderWidth: 8, borderColor: '#dbe7ed' },
  bigScore: { color: '#fff', fontSize: 48, fontWeight: '900' },
  percent: { color: '#bcd0dd', fontSize: 20, fontWeight: '800', marginTop: 17 },
  evaluation: { color: '#506170', fontSize: 15, lineHeight: 22, textAlign: 'center', marginVertical: 22, maxWidth: 360 },
  resultCard: { width: '100%', backgroundColor: '#e8f6ef', borderRadius: 15, padding: 16, borderWidth: 1, borderColor: '#cae8d7', marginBottom: 11 },
  reviewCard: { backgroundColor: '#fff3e6', borderColor: '#f1d8b8' },
  resultCardTitle: { color: '#197450', fontSize: 14, fontWeight: '900' },
  reviewTitle: { color: '#9c5a18', fontSize: 14, fontWeight: '900' },
  resultDetail: { color: '#536270', fontSize: 13, lineHeight: 20, marginTop: 6 },
  primaryButton: { width: '100%', backgroundColor: '#e64045', borderRadius: 14, paddingVertical: 15, alignItems: 'center', marginTop: 8 },
  primaryButtonText: { color: '#fff', fontWeight: '900', fontSize: 15 },
  secondaryButton: { width: '100%', borderRadius: 14, paddingVertical: 15, alignItems: 'center', marginTop: 8, borderWidth: 1, borderColor: '#cbd4da' },
  secondaryButtonText: { color: '#254157', fontWeight: '800', fontSize: 15 },
  protocolNote: { color: '#85919b', fontSize: 11, marginTop: 16 },
});

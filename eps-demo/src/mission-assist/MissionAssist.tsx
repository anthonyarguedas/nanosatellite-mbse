import { useEffect, useId, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import catalogueData from '../data/missions.json';
import { acceptAltitude, queryProblem, searchLexical } from './retrieval';
import type { MissionAnalogue, MissionCatalogue, MissionMatch, MissionSearchResult, RetrievalMethod } from './types';
import './mission-assist.css';

const catalogue = catalogueData as MissionCatalogue;
export const MISSION_QUERY_EXAMPLES = [
  { label: 'Vegetation imaging', text: 'Image vegetation across the Earth to monitor land cover and agriculture, then downlink the camera observations.' },
  { label: 'Ionosphere radar', text: 'Receive scattered ground radar signals from plasma irregularities in the polar ionosphere and store the measurements for later downlink.' },
  { label: 'Rainfall radar', text: 'Demonstrate a compact radar in a small satellite to measure precipitation and rain clouds from Earth orbit.' },
  { label: 'Unrelated input', text: 'Suggest a tomato pasta recipe for dinner with basil and cheese.' },
];

function Parameter({ label, value, unit = '' }: { label: string; value: string | number | [number, number] | null; unit?: string }) {
  return <div><dt>{label}</dt><dd>{value === null ? <span className="ma-missing">Missing</span>
    : `${Array.isArray(value) ? `${value[0]} to ${value[1]}` : value}${unit}`}</dd></div>;
}

function AnalogueCard({ match, onApply }: { match: MissionAnalogue; onApply: (match: MissionMatch) => void }) {
  const [accepted, setAccepted] = useState(false);
  const [applied, setApplied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mission = match.mission;
  const altitude = mission.orbit.altitudeKm;
  const scalar = altitude && typeof altitude.value === 'number';
  const apply = () => {
    if (!accepted || !scalar) return;
    try {
      onApply(acceptAltitude(match));
      setApplied(true);
    } catch (problem) {
      setError(problem instanceof Error ? problem.message : 'The altitude could not be applied.');
    }
  };
  return <article className="ma-card">
    <header><div><span className={`ma-status ma-${mission.status}`}>{mission.status === 'flown' ? 'Flown mission' : 'Design study'}</span>
      <h4>{mission.name}</h4></div><span className="ma-score">cosine {match.score.toFixed(3)}</span></header>
    <p className="ma-identity">{mission.identity}</p>
    <p>{mission.description}</p>
    <p className="ma-epoch">{mission.epoch}. {mission.statusDetail}</p>
    <dl className="ma-parameters">
      <Parameter label="Source altitude" value={altitude?.value ?? null} unit=" km" />
      <Parameter label="Orbit context" value={mission.orbit.orbitType?.value ?? null} />
      <Parameter label="Inclination" value={mission.orbit.inclinationDeg?.value ?? null} unit="°" />
    </dl>
    {altitude && <p className="ma-meaning">{altitude.meaning}</p>}
    {match.method === 'lexical-tfidf' && <p className="ma-terms">Shared terms: {match.matchedTerms.join(', ')}</p>}
    <details><summary>Evidence and missing data</summary>
      <p className="ma-identity">Record {mission.id}, revision {mission.revision}. Catalogue {match.catalogueRevision}.</p>
      {Object.entries(mission.orbit).map(([field, parameter]) => <p key={field} className="ma-evidence-field"><strong>{field}</strong>: {parameter
        ? <>“{parameter.original}” ({parameter.sourceIds.join(', ')}). {parameter.meaning}</> : 'Missing from this reviewed record.'}</p>)}
      <p className="ma-identity">Description sources: {mission.descriptionSourceIds.join(', ')}.</p>
      {mission.sources.map(source => <section className="ma-source" key={source.id}>
        <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a>
        <p>{source.id}. {source.location}. {source.revision}. Retrieved {source.retrievedAt}.</p>
        {source.quotes.map(quote => <blockquote key={quote}>{quote}</blockquote>)}
      </section>)}
      <ul>{mission.caveats.map(caveat => <li key={caveat}>{caveat}</li>)}</ul>
    </details>
    {scalar ? <div className="ma-accept">
      <label><input type="checkbox" checked={accepted} onChange={event => { setAccepted(event.target.checked); setApplied(false); }} />
        I accept this source altitude as a circular study assumption for my mission.</label>
      <button type="button" disabled={!accepted} onClick={apply}>Accept {altitude.value} km altitude</button>
      {applied && <p role="status">Altitude acceptance sent. Recompute the affected analyses.</p>}
    </div> : <p className="ma-missing">{altitude ? 'Altitude range retained. Select a circular study altitude through separate orbit analysis. No midpoint is applied.'
      : 'No sourced altitude is available to apply.'}</p>}
    {error && <p role="alert">{error}</p>}
  </article>;
}

export interface MissionAssistProps {
  onApply: (match: MissionMatch) => void;
  initialQuery?: string;
  onQueryChange?: (query: string) => void;
}

/** Lazy-load this component inside the mission inspector. It never edits workspace state. */
export function MissionAssist({ onApply, initialQuery = '', onQueryChange }: MissionAssistProps) {
  const id = useId();
  const [query, setQuery] = useState(initialQuery);
  const [method, setMethod] = useState<RetrievalMethod>('semantic-qwen');
  const [result, setResult] = useState<MissionSearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const request = useRef<AbortController | null>(null);
  const version = useRef(0);
  useEffect(() => () => { version.current++; request.current?.abort(); }, []);
  const invalidate = () => {
    version.current++;
    request.current?.abort();
    setResult(null); setError(null); setBusy(false);
  };
  useEffect(() => {
    version.current++; request.current?.abort();
    setResult(null); setError(null); setBusy(false); setQuery(initialQuery);
  }, [initialQuery]);
  const changeQuery = (value: string) => { invalidate(); setQuery(value); onQueryChange?.(value); };
  const search = async (event: FormEvent) => {
    event.preventDefault();
    invalidate();
    const current = version.current;
    const controller = new AbortController();
    request.current = controller;
    setBusy(true);
    try {
      const problem = queryProblem(query);
      const next: MissionSearchResult = problem
        ? { status: 'abstained', matches: [], reason: problem, method }
        : method === 'lexical-tfidf' ? searchLexical(query, catalogue)
          : await (await import('./semantic')).searchSemantic(query, catalogue, controller.signal);
      if (current === version.current) setResult(next);
    } catch (problem) {
      if (current === version.current) setError(method === 'semantic-qwen'
        ? `Semantic retrieval is unavailable. Start the optional local Qwen service or explicitly select lexical mode. ${problem instanceof Error ? problem.message : ''}`
        : `Lexical retrieval could not run. ${problem instanceof Error ? problem.message : ''}`);
    } finally {
      if (current === version.current) setBusy(false);
    }
  };
  return <section className="mission-assist" aria-labelledby={`${id}-title`}>
    <header className="ma-title"><span className="ma-kicker">MISSION ANALOGUES</span><h3 id={`${id}-title`}>Start from your ConOps</h3></header>
    <p>Describe your objective and payload in plain English. Similar missions can supply sourced parameter alternatives. Text alone cannot determine a unique orbit.</p>
    <form onSubmit={search}>
      <label htmlFor={`${id}-query`}>Mission concept of operations</label>
      <textarea id={`${id}-query`} rows={4} maxLength={2000} value={query} onChange={event => changeQuery(event.target.value)} placeholder="What will the spacecraft observe or relay? How will the payload and ground contacts operate?" />
      <div className="ma-examples">{MISSION_QUERY_EXAMPLES.map(example => <button type="button" key={example.label} onClick={() => changeQuery(example.text)}>{example.label}</button>)}</div>
      <label htmlFor={`${id}-method`}>Retrieval method</label>
      <select id={`${id}-method`} value={method} onChange={event => { invalidate(); setMethod(event.target.value as RetrievalMethod); }}>
        <option value="semantic-qwen">Semantic embeddings + cosine (local Qwen service)</option>
        <option value="lexical-tfidf">Lexical TF-IDF vectors + cosine (offline demo)</option>
      </select>
      <p className="ma-method">{method === 'semantic-qwen' ? 'Optional loopback service, pinned Qwen3 0.6B model. Inference stays on this computer. No API key or external text upload. First request loads the cached model.'
        : 'Word overlap, not semantic embeddings. Runs immediately in this browser. No model download, service or network request.'}</p>
      <button className="ma-search" type="submit" disabled={busy}>{busy ? 'Retrieving local analogues…' : 'Find mission analogues'}</button>
    </form>
    <p className="ma-warning">Similarity is an uncalibrated rank, not a probability or proof of suitability. Launch availability, revisit, resolution and orbital constraints require independent assessment. Orbit labels are context only. This EPS demo uses circular geometry without SSO, J2, beta angle or seasonal propagation.</p>
    {busy && <p role="status">Loading the local model or comparing descriptions. Orbit parameters have not changed.</p>}
    {error && <p className="ma-error" role="alert">{error}</p>}
    {result && <div aria-live="polite"><p className="ma-result-label">{result.method === 'semantic-qwen' ? 'Semantic Qwen cosine' : 'Lexical TF-IDF cosine'} · {result.reason}</p>
      {result.matches.map(match => <AnalogueCard key={`${version.current}-${match.mission.id}`} match={match} onApply={onApply} />)}
    </div>}
    <p className="ma-footnote">{catalogue.missions.length} reviewed records. Acceptance changes altitude only through the host application. Other mission fields remain unchanged.</p>
  </section>;
}

export default MissionAssist;

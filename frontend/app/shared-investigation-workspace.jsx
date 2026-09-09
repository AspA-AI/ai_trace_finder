"use client";

import { useEffect, useMemo, useState } from "react";

const peopleApi = "/api/investigations";
const businessApi = "/api/business-investigations";
const tabs = ["Overview", "Evidence", "Verification", "Profile"];
const states = ["VERIFIED", "PROBABLE", "UNKNOWN", "CONTRADICTED", "REJECTED"];

const human = (value) => String(value || "").replaceAll("_", " ").toLowerCase().replace(/^./, (letter) => letter.toUpperCase());
const pct = (value) => `${Math.round((Number(value) || 0) * 100)}%`;
const values = (value) => Array.isArray(value) ? value.join(", ") : value || "—";
const apiFor = (type) => type === "business" ? businessApi : peopleApi;

async function json(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) throw new Error(`Request failed (HTTP ${response.status})`);
  return response.json();
}

async function loadCase(item) {
  const base = apiFor(item.type);
  const [input, sources, observations, verification, profile] = await Promise.all([
    json(`${base}/${item.id}/input`),
    json(`${base}/${item.id}/sources`),
    json(`${base}/${item.id}/observations`),
    json(`${base}/${item.id}/verification`),
    item.type === "people" ? json(`${base}/${item.id}/profile`) : Promise.resolve(null),
  ]);
  return { input: input.input || {}, sources, observations, verification, profile };
}

function Icon({ name }) {
  const paths = {
    cases: <><path d="M4 7.5h16v12H4z"/><path d="M8 7.5V5h8v2.5"/></>,
    graph: <><circle cx="5" cy="12" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="m7.2 11 8.6-4M7.2 13l8.6 4"/></>,
    evaluation: <><path d="M5 19V9M12 19V5M19 19v-7"/><path d="M3 19h18"/></>,
    search: <><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 4.5 4.5"/></>,
  };
  return <svg className="shared-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>;
}

function Badge({ children, tone = "neutral" }) { return <span className={`shared-badge ${tone}`}><i />{children}</span>; }

function InputChips({ input, type }) {
  const fields = type === "business"
    ? [["Company", input.company_name], ["Industry", input.industry], ["Domains", input.domains], ["Locations", input.locations], ["Founders", input.founders], ["Products", input.products], ["Additional clues", input.additional_clues]]
    : [["Name", input.name], ["Occupation", input.occupation], ["Usernames", input.usernames], ["Employers", input.employers], ["Locations", input.locations], ["Websites", input.websites], ["GitHub", input.github_handle], ["Additional clues", input.additional_clues]];
  return <div className="shared-input"><small>Investigation input used</small><div>{fields.filter(([, value]) => value && (!Array.isArray(value) || value.length)).map(([label, value]) => <span key={label}><b>{label}</b>{values(value)}</span>)}</div></div>;
}

function SourceReason({ source }) {
  const reasons = source.relevance_reasons || [];
  if (source.is_relevant === false) return reasons.length ? `Filtered: ${reasons.map(human).join(", ")}.` : "Filtered because it did not contain enough target-specific signal.";
  return reasons.length ? `Included: ${reasons.map(human).join(", ")}.` : "Included for downstream evidence extraction.";
}

function SourceDrawer({ source, close }) {
  if (!source) return null;
  return <div className="shared-backdrop" onClick={close}><aside className="shared-drawer" onClick={(event) => event.stopPropagation()}><button className="shared-close" onClick={close}>×</button><small>Captured source</small><h2>{source.title || source.domain || "Source"}</h2><a href={source.url} target="_blank" rel="noreferrer">Open original source ↗</a><hr/><small>Relevance</small><strong>{pct(source.relevance_score)} · {source.is_relevant === false ? "Filtered" : "Relevant"}</strong><p>{SourceReason({ source })}</p><small>Source URL</small><code>{source.url}</code><small>Source ID</small><code>{source.source_id}</code></aside></div>;
}

function Overview({ item, data, openSource }) {
  const accepted = (data.verification?.results || []).filter((result) => ["VERIFIED", "PROBABLE"].includes(result.state)).length;
  const links = (data.verification?.results || []).filter((result) => result.comparison_type === "identity_link");
  const relevant = data.sources.filter((source) => source.is_relevant !== false).length;
  const semantic = data.verification?.dual_track?.semantic_profile;
  return <div className="shared-view"><InputChips input={data.input} type={item.type}/><div className="shared-kpi-grid"><article><small>Source relevance</small><strong>{relevant} / {data.sources.length}</strong><span>{data.sources.length ? pct(relevant / data.sources.length) : "0%"} included</span></article><article><small>Accepted links</small><strong>{accepted}</strong><span>{links.length - accepted} uncertain or contradicted</span></article><article><small>Deterministic track</small><strong>{data.verification?.dual_track?.deterministic_verdict || "Not run"}</strong><span>{data.verification?.dual_track ? pct(data.verification.dual_track.deterministic_confidence) + " confidence" : "Awaiting analysis"}</span></article><article><small>Independent semantic track</small><strong>{semantic?.verdict ? human(semantic.verdict) : "Not run"}</strong><span>{semantic ? human(semantic.confidence_label) + " confidence" : "Full-evidence review pending"}</span></article></div><section className="shared-explanation"><div><small>Why this result?</small><h3>{item.status === "resolved" || item.status === "verified" ? "A connected profile is emerging" : "The evidence remains open"}</h3><p>{data.verification?.dual_track?.semantic_reasoning || data.profile?.decision_explanation?.summary || item.reason || "The system has preserved the evidence, but it does not have enough independent support to make a safe conclusion."}</p></div><div><small>Recommended next step</small><p>{data.verification?.dual_track?.suggested_action || "Add a stronger identifier, official domain, username, or cross-link to narrow the investigation."}</p></div></section><div className="shared-section-heading"><div><small>Evidence trail</small><h2>Sources connected to this investigation</h2></div><span>{data.sources.length} sources · {data.observations.length} observations</span></div><div className="shared-source-list">{data.sources.slice(0, 8).map((source) => <button key={source.source_id || source.url} onClick={() => openSource(source)}><span className="shared-source-mark">{(source.domain || "S")[0].toUpperCase()}</span><span><strong>{source.title || source.domain || "Captured source"}</strong><small>{source.domain || source.url}</small></span><span className="shared-source-reason">{SourceReason({ source })}</span><b>{pct(source.relevance_score)}</b>↗</button>)}</div></div>;
}

function Evidence({ item, data, openSource }) {
  return <div className="shared-view"><InputChips input={data.input} type={data.input.company_name ? "business" : "people"}/><div className="shared-section-heading"><div><small>Source register</small><h2>Every captured source</h2></div><span>Relevance is separate from identity verification</span></div><div className="shared-evidence-table"><div className="shared-evidence-row head"><span>Source</span><span>Relevance</span><span>Reason</span><span /></div>{data.sources.map((source) => <button className="shared-evidence-row" key={source.source_id || source.url} onClick={() => openSource(source)}><span><strong>{source.title || source.domain || "Captured source"}</strong><small>{source.url}</small></span><span><Badge tone={source.is_relevant === false ? "muted" : "good"}>{source.is_relevant === false ? "Filtered" : "Relevant"}</Badge><small>{pct(source.relevance_score)}</small></span><span>{SourceReason({ source })}</span><b>↗</b></button>)}</div></div>;
}

function Verification({ data }) {
  const results = data.verification?.results || [];
  const dual = data.verification?.dual_track;
  const counts = Object.fromEntries(states.map((state) => [state, results.filter((result) => result.state === state).length]));
  return <div className="shared-view"><InputChips input={data.input} type="people"/><div className="shared-state-grid">{states.map((state) => <div key={state}><small>{state}</small><strong>{counts[state] || 0}</strong><span>{state === "VERIFIED" ? "Accepted evidence relationships" : state === "UNKNOWN" ? "Needs stronger evidence" : "Recorded comparisons"}</span></div>)}</div><div className="shared-track-grid"><section><small>Deterministic analysis</small><h2>{dual?.deterministic_verdict || "Not available"}</h2><p>{dual?.deterministic_reasoning?.join(" ") || "The source comparison track has not produced a saved explanation."}</p></section><section><small>Independent semantic analysis</small><h2>{dual?.semantic_verdict ? human(dual.semantic_verdict) : "Not available"}</h2><p>{dual?.semantic_reasoning || "The full-evidence semantic analysis has not been saved."}</p></section></div>{results.length ? <div className="shared-relationship-list">{results.slice(0, 30).map((result, index) => <details key={index}><summary><Badge tone={result.state === "VERIFIED" ? "good" : result.state === "PROBABLE" ? "warn" : "muted"}>{result.state}</Badge><span>{human(result.comparison_type)}</span><b>{pct(result.confidence_score)}</b></summary><p>{(result.reason_codes || []).map(human).join(", ") || "No reason codes recorded."}</p></details>)}</div> : <div className="shared-empty">No verification relationships are saved for this investigation yet.</div>}</div>;
}

function Profile({ item, data }) {
  const dual = data.verification?.dual_track;
  const semantic = dual?.semantic_profile;
  const attributes = semantic?.attributes || [];
  return <div className="shared-view"><InputChips input={data.input} type={item.type}/>{semantic ? <><section className="shared-profile-hero"><div className="shared-profile-avatar">{(semantic.likely_name || data.input.name || data.input.company_name || "?").split(" ").map((part) => part[0]).join("").slice(0, 2)}</div><div><small>Evidence-supported working profile</small><h2>{semantic.likely_name || data.input.name || data.input.company_name}</h2><p>{semantic.headline || "A cautious synthesis of the saved public evidence."}</p></div><Badge tone={semantic.verdict === "likely_same_person" || semantic.verdict === "likely_same_business" ? "good" : "warn"}>{human(semantic.verdict)}</Badge></section><p className="shared-profile-summary">{semantic.profile_summary}</p><div className="shared-attribute-grid">{attributes.map((attribute, index) => <article key={`${attribute.field}-${index}`}><small>{human(attribute.field)}</small><strong>{values(attribute.value)}</strong><span>{human(attribute.confidence_label)} confidence</span><p>{attribute.caveat || "Source-grounded claim."}</p></article>)}</div><section className="shared-explanation"><div><small>Agent reasoning</small><p>{semantic.reasoning}</p></div><div><small>Suggested next step</small><p>{dual.suggested_action || "Review the supporting sources before treating this profile as confirmed."}</p></div></section></> : <div className="shared-empty"><h2>No profile synthesis yet</h2><p>The evidence is saved, but an independent profile has not been generated for this case.</p></div>}</div>;
}

function GraphView({ item, data }) {
  const sources = data.sources.slice(0, 12);
  return <div className="shared-view"><div className="shared-section-heading"><div><small>ENTITY GRAPH</small><h2>{item.label} evidence network</h2></div><span>{sources.length} source nodes shown</span></div><div className="shared-inline-note">This graph uses the selected investigation’s own {item.type} evidence. Select a source node below to review its original content and verification context.</div><div className="shared-network"><div className="shared-network-target"><strong>{item.label}</strong><small>Investigation target</small></div>{sources.map((source, index) => <div className="shared-network-node" key={source.source_id || source.url} style={{ "--node-index": index }}><i>{(source.domain || "S")[0].toUpperCase()}</i><strong>{source.domain || source.title || "Source"}</strong><small>{source.is_relevant === false ? "Filtered evidence" : "Relevant evidence"}</small></div>)}</div><div className="shared-graph-actions"><a href={`/graph?investigation_id=${item.id}`}>Open detailed graph view ↗</a><span>Source nodes are fetched from the {item.type} evidence provider.</span></div></div>;
}

function EvaluationView({ mode }) {
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { json("/api/evaluations/comparison").then(setReport).catch((err) => setError(err.message)); }, []);
  const rows = report?.comparison_table || [];
  return <div className="shared-view"><div className="shared-section-heading"><div><small>EVALUATION WORKSPACE</small><h2>{mode === "business" ? "Business evaluation" : "People evaluation"}</h2></div><span>Independent benchmark evidence</span></div>{error && <div className="shared-error">{error}</div>}{!report && !error ? <div className="shared-loading"><i/>Loading evaluation report…</div> : <><div className="shared-inline-note">Evaluation is loaded independently from the selected {mode} investigation data. It compares baseline behavior with TRACE’s evidence-first analysis.</div><div className="shared-evaluation-table"><div className="shared-evaluation-row head"><span>Metric</span><span>Simple baseline</span><span>TRACE</span><span>Change</span></div>{rows.map((row) => <div className="shared-evaluation-row" key={row.metric}><strong>{row.metric}</strong><span>{pct(row.simple_baseline)}</span><span className="good-text">{pct(row.agent_solution)}</span><b>{row.change_points > 0 ? "+" : ""}{Number(row.change_points || 0).toFixed(2)} pts</b></div>)}</div><a className="shared-graph-actions" href="/evaluation">Open full evaluation report ↗</a></>}</div>;
}

export default function SharedInvestigationWorkspace({ initialMode = "people" }) {
  const [mode, setMode] = useState(initialMode);
  const [view, setView] = useState("investigations");
  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState(null);
  const [tab, setTab] = useState("Overview");
  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [drawer, setDrawer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadCases = () => { const stamp = Date.now(); return Promise.all([json(`${peopleApi}?refresh=${stamp}`), json(`${businessApi}?refresh=${stamp}`)]).then(([people, businesses]) => { const mapped = [...(Array.isArray(people) ? people : []).map((item) => ({ ...item, id: item.investigation_id, type: "people", label: item.name || "Unnamed person" })), ...(Array.isArray(businesses) ? businesses : []).map((item) => ({ ...item, id: item.investigation_id, type: "business", label: item.company_name || "Unnamed business" }))].sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0)); setItems(mapped); setSelected((current) => current && mapped.some((item) => item.id === current.id) ? mapped.find((item) => item.id === current.id) : mapped.find((item) => item.type === mode) || mapped[0] || null); setLoading(false); }).catch((err) => { setError(err.message); setLoading(false); }); };
  useEffect(() => { loadCases(); }, []);
  useEffect(() => { if (!selected) return; setData(null); setError(""); loadCase(selected).then(setData).catch((err) => setError(`This investigation could not be loaded. ${err.message}`)); }, [selected]);
  const visible = useMemo(() => items.filter((item) => item.type === mode && `${item.label} ${item.id} ${item.reason || ""}`.toLowerCase().includes(query.toLowerCase())), [items, mode, query]);
  const totals = useMemo(() => ({ cases: items.filter((item) => item.type === mode).length, sources: items.filter((item) => item.type === mode).reduce((sum, item) => sum + (item.source_count || 0), 0), accepted: items.filter((item) => item.type === mode).reduce((sum, item) => sum + (item.verified_link_count || 0), 0), unresolved: items.filter((item) => item.type === mode).reduce((sum, item) => sum + (item.unresolved_comparison_count || 0), 0) }), [items, mode]);
  const switchMode = (next) => { setMode(next); setView("investigations"); setTab("Overview"); setDrawer(null); setSelected(items.find((item) => item.type === next) || null); };
  const switchView = (next) => { setView(next); setDrawer(null); };
  const status = selected?.status === "resolved" || selected?.status === "verified" ? "Resolved" : selected ? "Needs review" : "No cases";
  return <main className="shared-app"><aside className="shared-sidebar"><div className="shared-brand"><div>⌁</div><span><strong>TRACE</strong><small>Evidence workspace</small></span></div><div className="shared-workspace-switch"><span className="shared-avatar">A</span><span><small>Workspace</small><strong>Atlas Research</strong></span><b>⌄</b></div><nav><small>WORKSPACE</small><button className={mode === "people" ? "active" : ""} onClick={() => switchMode("people")}><Icon name="cases"/>People investigations <em>{items.filter((item) => item.type === "people").length}</em></button><button className={mode === "business" ? "active" : ""} onClick={() => switchMode("business")}><Icon name="cases"/>Business investigations <em>{items.filter((item) => item.type === "business").length}</em></button><a href="/graph"><Icon name="graph"/>Entity graph</a><a href="/evaluation"><Icon name="evaluation"/>Evaluation</a></nav><div className="shared-sidebar-bottom"><span><i/>Evidence integrity<small>All systems operational</small></span><span><b>RZ</b>Research analyst</span></div></aside><section className="shared-main"><header className="shared-topbar"><span>Workspace <b>/</b> <strong>{mode === "business" ? "Business investigations" : "People investigations"}</strong></span><span>⌁ Evidence-first mode</span></header><div className="shared-content"><header className="shared-page-heading"><div><small>{mode === "business" ? "BUSINESS RESEARCH DESK" : "PEOPLE RESEARCH DESK"}</small><h1>{mode === "business" ? "Organization investigations" : "People investigations"}</h1><p>Build an auditable picture from public evidence. Every claim stays connected to its source.</p></div><a className="shared-primary" href={mode === "business" ? "/business-investigations/new" : "/investigations/new"}>＋ New {mode === "business" ? "business" : "people"} investigation</a></header><div className="shared-metrics"><div><small>Active investigations</small><strong>{totals.cases}</strong><span>Live from saved cases</span></div><div><small>Sources captured</small><strong>{totals.sources}</strong><span>Across this workspace</span></div><div><small>Accepted links</small><strong className="good-text">{totals.accepted}</strong><span>Conservative by design</span></div><div><small>Needs review</small><strong className="warn-text">{totals.unresolved}</strong><span>Awaiting stronger evidence</span></div></div><div className="shared-workspace-grid"><section className="shared-case-panel"><div className="shared-panel-heading"><div><small>CASE LIBRARY</small><h2>{mode === "business" ? "Businesses" : "People"}</h2></div><span>{visible.length} shown</span></div><div className="shared-search"><Icon name="search"/><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder={`Search ${mode === "business" ? "companies" : "people"} or case ID`}/></div><div className="shared-case-list">{visible.map((item) => <button className={selected?.id === item.id ? "selected" : ""} key={item.id} onClick={() => { setSelected(item); setTab("Overview"); }}><span className="shared-case-avatar">{item.label.split(" ").map((part) => part[0]).join("").slice(0, 2)}</span><span><strong>{item.label}</strong><small>{item.industry || item.occupation || item.reason || "Investigation"}</small><code>{item.id}</code></span><span><Badge tone={item.status === "resolved" || item.status === "verified" ? "good" : "warn"}>{item.status === "resolved" || item.status === "verified" ? "Resolved" : "Needs review"}</Badge><small>{item.source_count || 0} sources</small></span></button>)}{!visible.length && <div className="shared-empty-list"><strong>No {mode} investigations yet</strong><span>Start a new investigation to build the evidence workspace.</span></div>}</div></section><section className="shared-detail-panel">{!selected ? <div className="shared-empty"><h2>Choose an investigation</h2><p>Select a saved case from the library or start a new one.</p></div> : <><header className="shared-detail-heading"><div className="shared-case-avatar large">{selected.label.split(" ").map((part) => part[0]).join("").slice(0, 2)}</div><div><small>{mode === "business" ? "BUSINESS INVESTIGATION" : "PEOPLE INVESTIGATION"} / {selected.id}</small><h2>{selected.label}</h2><p><Badge tone={status === "Resolved" ? "good" : "warn"}>{status}</Badge><span> Evidence can be inspected below</span></p></div><a href={mode === "business" ? `/business-investigations/${selected.id}` : `/investigations/new?name=${encodeURIComponent(selected.label)}&investigation_id=${encodeURIComponent(selected.id)}`}>Refine input ↗</a></header><nav className="shared-tabs">{tabs.map((item) => <button className={tab === item ? "active" : ""} key={item} onClick={() => setTab(item)}>{item}{item === "Evidence" && data && <em>{data.sources.length}</em>}{item === "Verification" && data && <em>{data.verification?.results?.length || 0}</em>}</button>)}{mode === "business" && <a href={`/graph?investigation_id=${selected.id}`}>Open graph ↗</a>}</nav>{error && <div className="shared-error">{error}</div>}{!data && !error ? <div className="shared-loading"><i/>Loading evidence workspace…</div> : data && tab === "Overview" ? <Overview item={selected} data={data} openSource={setDrawer}/> : data && tab === "Evidence" ? <Evidence data={data} openSource={setDrawer}/> : data && tab === "Verification" ? <Verification data={data}/> : data && <Profile item={selected} data={data}/>}</>}</section></div></div></section>{drawer && <SourceDrawer source={drawer} close={() => setDrawer(null)}/>}</main>;
}

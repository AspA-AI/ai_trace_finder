"use client";

import { useState } from "react";

const split = (value) => value.split("\n").map((item) => item.trim()).filter(Boolean);

export default function NewBusinessInvestigation() {
  const [form, setForm] = useState({ company_name: "", industry: "", domains: "", locations: "", founders: "", executives: "", products: "", known_repositories: "", additional_clues: "" });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError(""); setResult(null);
    const payload = { company_name: form.company_name, industry: form.industry || null, domains: split(form.domains), locations: split(form.locations), founders: split(form.founders), executives: split(form.executives), products: split(form.products), known_repositories: split(form.known_repositories), additional_clues: split(form.additional_clues) };
    try {
      const response = await fetch("/api/business-investigations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || "Business investigation could not be started.");
      // Retrieval and verification are separate server stages. Start the
      // business semantic track immediately so the result page never opens
      // with an empty, not-yet-verified state.
      const verification = await fetch(`/api/business-investigations/${body.investigation_id}/verification`, { method: "POST" });
      const verificationBody = await verification.json();
      if (!verification.ok) throw new Error(verificationBody.detail || "Business evidence was collected, but verification failed.");
      setResult({ ...body, verification: verificationBody });
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }
  return <main className="new-investigation"><div className="new-card"><a className="back-link" href="/">← Back to workspace</a><div className="new-intro"><span className="new-mark">⌁</span><div><label>Business investigation</label><h1>Map an organization from evidence.</h1><p>TRACE collects permitted public sources and keeps business claims separate from identity conclusions.</p></div></div><form onSubmit={submit}><div className="form-grid"><label>Company name<input required value={form.company_name} onChange={(event) => update("company_name", event.target.value)} placeholder="e.g. Acme Robotics" /></label><label>Industry<input value={form.industry} onChange={(event) => update("industry", event.target.value)} placeholder="e.g. robotics" /></label><label>Domains<textarea value={form.domains} onChange={(event) => update("domains", event.target.value)} placeholder="One domain per line" /></label><label>Locations<textarea value={form.locations} onChange={(event) => update("locations", event.target.value)} placeholder="One location per line" /></label><label>Founders<textarea value={form.founders} onChange={(event) => update("founders", event.target.value)} placeholder="One name per line" /></label><label>Executives<textarea value={form.executives} onChange={(event) => update("executives", event.target.value)} placeholder="One name per line" /></label><label>Products<textarea value={form.products} onChange={(event) => update("products", event.target.value)} placeholder="One product per line" /></label><label>Known repositories<textarea value={form.known_repositories} onChange={(event) => update("known_repositories", event.target.value)} placeholder="URLs or repository names" /></label></div><label className="wide-field">Additional clues<textarea value={form.additional_clues} onChange={(event) => update("additional_clues", event.target.value)} placeholder="One clue per line" /></label>{error && <div className="trace-error">{error}</div>}{result && <section className="trace-explain"><strong>Business evidence collected</strong><span>{result.investigation_id} · {result.retrieved_source_count || 0} sources · {result.observation_count || 0} observations</span><small><a href={`/business-investigations/${result.investigation_id}`}>Open business evidence map ↗</a></small></section>}<div className="form-footer"><span>V2 business evidence mode</span><button type="submit" className="new-case" disabled={busy}>{busy ? "Researching business…" : "Start business investigation →"}</button></div></form></div></main>;
}

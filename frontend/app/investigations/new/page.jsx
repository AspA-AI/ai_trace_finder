"use client";

import { useEffect, useState } from "react";
import { removeInvestigationCache } from "../../../lib/investigation-cache";

export default function NewInvestigation() {
  const [form, setForm] = useState({ name: "", occupation: "", location: "", username: "", clues: "" });
  const [extended, setExtended] = useState({ employer: "", website: "", github: "" });
  const [existingId, setExistingId] = useState(null);
  const [busy, setBusy] = useState(false);
  const [progressStep, setProgressStep] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [error, setError] = useState("");
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const name = params.get("name");
    // Only an explicit query parameter may turn this into a refinement.
    // Reading the previous page's URL caused the standalone New investigation
    // action to inherit an old investigation ID and call the update path.
    const explicitId = params.get("investigation_id") || null;
    if (name) setForm((current) => ({ ...current, name }));
    if (explicitId) {
      setExistingId(explicitId);
      fetch(`/api/investigations/${encodeURIComponent(explicitId)}/input`, { cache: "no-store" })
        .then((response) => response.ok ? response.json() : null)
        .then((payload) => {
          const input = payload?.input;
          if (!input) return;
          setForm({ name: input.name || "", occupation: input.occupation || "", location: input.locations?.[0] || "", username: input.usernames?.[0] || "", clues: (input.additional_clues || []).join("\n") });
          setExtended({ employer: input.employers?.[0] || "", website: input.websites?.[0] || "", github: input.github_handle || "" });
        })
        .catch(() => {});
      return;
    }
    if (!name) return;
    // Older links may contain only the name. Resolve the latest exact-name
    // case once, then use its ID so refinement still updates instead of
    // creating a duplicate. New investigations without a name are unaffected.
    fetch("/api/investigations", { cache: "no-store" })
      .then((response) => response.ok ? response.json() : [])
      .then((items) => {
        const matches = items.filter((item) => String(item.name || "").trim().toLowerCase() === name.trim().toLowerCase());
        const latest = matches[0];
        if (!latest?.investigation_id) return;
        setExistingId(latest.investigation_id);
        return fetch(`/api/investigations/${encodeURIComponent(latest.investigation_id)}/input`, { cache: "no-store" });
      })
      .then((response) => response?.ok ? response.json() : null)
      .then((payload) => {
        const input = payload?.input;
        if (!input) return;
        setForm({ name: input.name || name, occupation: input.occupation || "", location: input.locations?.[0] || "", username: input.usernames?.[0] || "", clues: (input.additional_clues || []).join("\n") });
        setExtended({ employer: input.employers?.[0] || "", website: input.websites?.[0] || "", github: input.github_handle || "" });
      })
      .catch(() => {});
      
  }, []);
  async function submit(event) {
    event.preventDefault(); setBusy(true); setProgressStep(1); setElapsedSeconds(0); setError("");
    // Measured from the latest complete run: 110.52s investigation + 12.59s
    // verification + ~1s case refresh. This is a UX estimate only; the real
    // request remains the source of truth for completion.
    const estimatedSeconds = 124;
    const startedAt = Date.now();
    const clock = setInterval(() => setElapsedSeconds(Math.floor((Date.now() - startedAt) / 1000)), 1000);
    const progress = [setTimeout(() => setProgressStep(2), 8000), setTimeout(() => setProgressStep(3), 65000), setTimeout(() => setProgressStep(4), 110000)];
    console.log("Submitting investigation:", { form, extended, existingId });
    try {
      const clues = { name: form.name || null, occupation: form.occupation || null, locations: form.location ? [form.location] : [], usernames: form.username ? [form.username] : [], employers: extended.employer ? [extended.employer] : [], websites: extended.website ? [extended.website] : [], github_handle: extended.github || null, additional_clues: form.clues ? form.clues.split("\n").filter(Boolean) : [] };
      const response = existingId
        ? await fetch(`/api/investigations/${encodeURIComponent(existingId)}?force_refresh=true`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(clues) })
        : await fetch("/api/investigations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(clues) });
      const responseBody = await response.text();
      if (!response.ok) throw new Error(responseBody || `Investigation could not be started (HTTP ${response.status})`);
      let result;
      try { result = JSON.parse(responseBody); } catch { throw new Error("The investigation API returned an invalid response."); }
      if (!result.investigation_id) throw new Error("The investigation update did not return an investigation ID.");
      setProgressStep(4);
      const verification = await fetch(`/api/investigations/${encodeURIComponent(result.investigation_id)}/verification`, { method: "POST" });
      if (!verification.ok) throw new Error((await verification.text()) || "Evidence was collected, but verification could not be completed.");
      const saved = await fetch("/api/investigations", { cache: "no-store" });
      const savedItems = saved.ok ? await saved.json() : [];
      if (!savedItems.some((item) => item.investigation_id === result.investigation_id)) throw new Error(`The investigation was created but was not found in the saved case list (${result.investigation_id}).`);
      removeInvestigationCache(result.investigation_id);
      window.location.href = `/?investigation_id=${encodeURIComponent(result.investigation_id)}`;
    } catch (err) { progress.forEach(clearTimeout); clearInterval(clock); setError(err.message); setBusy(false); setProgressStep(0); }
  }
  const progressLabels = ["", "Building research plan", "Discovering public sources", "Evaluating and extracting evidence", "Preparing verification trace"];
  return <main className="new-investigation"><div className="new-card"><a className="back-link" href="/">← Back to investigations</a><div className="new-intro"><span className="new-mark">⌁</span><div><label>New investigation</label><h1>Start with what you know.</h1><p>Trace will discover public sources, preserve the originals, and keep every conclusion tied to evidence.</p></div></div><form onSubmit={submit}><div className="form-grid"><label>Person name<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Chris Lee" /></label><label>Occupation<input value={form.occupation} onChange={(e) => setForm({ ...form, occupation: e.target.value })} placeholder="e.g. software engineer" /></label><label>Location<input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} placeholder="e.g. Austin, Texas" /></label><label>Known username<input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} placeholder="Optional handle" /></label><label>Employer<input value={extended.employer} onChange={(e) => setExtended({ ...extended, employer: e.target.value })} placeholder="Optional organization" /></label><label>Known website<input value={extended.website} onChange={(e) => setExtended({ ...extended, website: e.target.value })} placeholder="Optional URL" /></label><label>GitHub handle<input value={extended.github} onChange={(e) => setExtended({ ...extended, github: e.target.value })} placeholder="Optional handle" /></label></div><label className="wide-field">Additional clues<textarea value={form.clues} onChange={(e) => setForm({ ...form, clues: e.target.value })} placeholder="One clue per line. Avoid conclusions; describe what you know." /></label>{error && <div className="trace-error">{error}</div>}{busy && <div className="investigation-progress" aria-live="polite"><div className="progress-track"><span style={{ width: `${Math.min(96, Math.max(8, (elapsedSeconds / 124) * 100))}%` }} /></div><strong>{elapsedSeconds > 124 ? "Still working — taking longer than usual" : progressLabels[progressStep]}</strong><small>Estimated about 2 minutes · {elapsedSeconds}s elapsed. Provider responses can take a few minutes; completion is confirmed by the server.</small></div>}<div className="form-footer"><span>Evidence-first mode · Unknown is a valid outcome</span><button type="submit" className="new-case" disabled={busy}>{busy ? "Running investigation…" : "Start investigation →"}</button></div></form></div></main>;
}

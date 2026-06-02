"use client";

import { useEffect, useState } from "react";
import AudioPlayer from "./components/AudioPlayer";
import CopyrightNotice from "./components/CopyrightNotice";
import HistoryList from "./components/HistoryList";
import ParameterControls from "./components/ParameterControls";
import SceneSelector from "./components/SceneSelector";
import {
  API_BASE,
  clearHistory,
  deleteGeneration,
  generateMusic,
  getHistory,
  getPolicy,
  getProviders,
  getScenes,
} from "../lib/api";
import type {
  Generation,
  GenerateParams,
  Policy,
  Provider,
  Scene,
} from "../lib/types";

const DEFAULT_MOODS = [
  "calm",
  "focused",
  "warm",
  "uplifting",
  "energetic",
  "dramatic",
  "neutral",
];

export default function Page() {
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [policy, setPolicy] = useState<Policy | null>(null);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [provider, setProvider] = useState("mock");
  const [history, setHistory] = useState<Generation[]>([]);
  const [params, setParams] = useState<GenerateParams>({
    scene: "",
    duration: 60,
    bpm: 90,
    mood: "calm",
    intensity: 5,
    no_drums: false,
  });
  const [current, setCurrent] = useState<Generation | null>(null);
  const [loop, setLoop] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const flash = (message: string) => {
    setNotice(message);
    window.setTimeout(() => setNotice(null), 2500);
  };

  const applyScene = (s: Scene) =>
    setParams((p) => ({
      ...p,
      scene: s.key,
      bpm: s.default_bpm,
      mood: s.default_mood,
      intensity: s.default_intensity,
      no_drums: s.default_no_drums,
    }));

  const onChange = (patch: Partial<GenerateParams>) =>
    setParams((p) => ({ ...p, ...patch }));

  // Initial data load.
  useEffect(() => {
    (async () => {
      try {
        const [sc, pol, hist, provs] = await Promise.all([
          getScenes(),
          getPolicy().catch(() => null),
          getHistory().catch(() => [] as Generation[]),
          getProviders().catch(() => [] as Provider[]),
        ]);
        setScenes(sc);
        setPolicy(pol);
        setHistory(hist);
        setProviders(provs);
        const firstImplemented = provs.find((p) => p.implemented);
        if (firstImplemented) setProvider(firstImplemented.key);
        if (sc.length) applyScene(sc[0]);
      } catch (e) {
        setError(
          `Could not reach the backend at ${API_BASE}. Make sure it is running ` +
            `(see backend/README.md). Details: ${(e as Error).message}`
        );
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const runGenerate = async (overrides: Partial<GenerateParams> = {}) => {
    const payload: GenerateParams = { ...params, provider, ...overrides };
    if (!payload.scene) return;
    setLoading(true);
    setError(null);
    try {
      const gen = await generateMusic(payload);
      setCurrent(gen);
      setHistory((h) => [gen, ...h]);
    } catch (e) {
      setError((e as Error).message ?? "Generation failed.");
    } finally {
      setLoading(false);
    }
  };

  const onGenerate = () => runGenerate();

  const onRegenerate = (sameSeed: boolean) => {
    if (!current) return;
    const seed = sameSeed
      ? current.seed ?? (current.parameters?.seed as number | undefined)
      : undefined;
    runGenerate({
      scene: current.scene,
      duration: current.duration,
      bpm: current.bpm,
      mood: current.mood,
      intensity: current.intensity,
      no_drums: current.no_drums,
      provider: current.provider,
      seed,
    });
  };

  const onDelete = async (id: string) => {
    try {
      await deleteGeneration(id);
      setHistory((h) => h.filter((g) => g.id !== id));
      setCurrent((c) => (c?.id === id ? null : c));
      flash("Track deleted");
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const onClearHistory = async () => {
    if (!window.confirm("Delete all tracks? This cannot be undone.")) return;
    try {
      const { deleted } = await clearHistory();
      setHistory([]);
      setCurrent(null);
      flash(`Cleared ${deleted} track(s)`);
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const moods = policy?.moods ?? DEFAULT_MOODS;

  return (
    <main className="container">
      {loading ? <div className="topbar-progress" aria-hidden /> : null}
      <header className="header">
        <div>
          <h1>🎵 Royalty-Free Music Generator</h1>
          <p className="subtitle">
            Generate original, instrumental, royalty-free background music for
            live streams and videos. Pick a scene, tune the parameters, generate,
            loop, and download — every track is saved with full metadata.
          </p>
        </div>
        <span className="badge">
          <span className="dot" />
          Provider: {provider}
        </span>
      </header>

      {error ? (
        <div className="alert">
          <span>{error}</span>
          <button
            className="alert-dismiss"
            onClick={() => setError(null)}
            aria-label="Dismiss"
          >
            ✕
          </button>
        </div>
      ) : null}

      <div className="grid">
        {/* Left column: create + play */}
        <div>
          <section className="card">
            <h2>1 · Scene</h2>
            <p className="hint">Choose the vibe for your background music.</p>
            <SceneSelector
              scenes={scenes}
              selected={params.scene || null}
              onSelect={applyScene}
            />
          </section>

          <section className="card">
            <h2>2 · Parameters</h2>
            <p className="hint">
              Defaults are tuned per scene — adjust to taste.
            </p>
            <ParameterControls
              params={params}
              moods={moods}
              providers={providers}
              provider={provider}
              onChange={onChange}
              onProviderChange={setProvider}
            />
            <div style={{ marginTop: 18 }}>
              <button
                className="btn btn-primary"
                onClick={onGenerate}
                disabled={loading || !params.scene}
              >
                {loading ? (
                  <>
                    <span className="spinner" /> Generating…
                  </>
                ) : (
                  <>✨ Generate</>
                )}
              </button>
            </div>
          </section>

          <section className="card">
            <h2>3 · Player</h2>
            <p className="hint">Play, loop, regenerate and download your track.</p>
            <AudioPlayer
              track={current}
              loop={loop}
              busy={loading}
              onToggleLoop={setLoop}
              onRegenerate={onRegenerate}
            />
          </section>
        </div>

        {/* Right column: copyright + history */}
        <div>
          <section className="card">
            <h2>Copyright &amp; License</h2>
            <CopyrightNotice policy={policy} track={current} />
          </section>

          <section className="card">
            <h2>History</h2>
            <p className="hint">Click any track to load it; ✕ to delete.</p>
            <HistoryList
              items={history}
              currentId={current?.id ?? null}
              onSelect={setCurrent}
              onDelete={onDelete}
              onClear={onClearHistory}
            />
          </section>
        </div>
      </div>

      {notice ? <div className="toast">{notice}</div> : null}
    </main>
  );
}

"use client";

import type { GenerateParams, Provider } from "../../lib/types";

export default function ParameterControls({
  params,
  moods,
  providers,
  provider,
  onChange,
  onProviderChange,
}: {
  params: GenerateParams;
  moods: string[];
  providers: Provider[];
  provider: string;
  onChange: (patch: Partial<GenerateParams>) => void;
  onProviderChange: (provider: string) => void;
}) {
  const activeProvider = providers.find((p) => p.key === provider);
  return (
    <div className="controls">
      <div className="field">
        <label>
          Duration <span className="value">{params.duration}s</span>
        </label>
        <input
          type="range"
          min={5}
          max={300}
          step={5}
          value={params.duration}
          onChange={(e) => onChange({ duration: Number(e.target.value) })}
        />
      </div>

      <div className="row">
        <div className="field">
          <label>
            BPM <span className="value">{params.bpm}</span>
          </label>
          <input
            type="range"
            min={40}
            max={200}
            step={1}
            value={params.bpm}
            onChange={(e) => onChange({ bpm: Number(e.target.value) })}
          />
        </div>
        <div className="field">
          <label>
            Intensity <span className="value">{params.intensity}/10</span>
          </label>
          <input
            type="range"
            min={1}
            max={10}
            step={1}
            value={params.intensity}
            onChange={(e) => onChange({ intensity: Number(e.target.value) })}
          />
        </div>
      </div>

      <div className="field">
        <label>Mood</label>
        <select
          value={params.mood}
          onChange={(e) => onChange({ mood: e.target.value })}
        >
          {moods.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </div>

      <label className="switch">
        <input
          type="checkbox"
          checked={params.no_drums}
          onChange={(e) => onChange({ no_drums: e.target.checked })}
        />
        No drums / percussion
      </label>

      {providers.length > 0 ? (
        <div className="field">
          <label>Provider</label>
          <select
            value={provider}
            onChange={(e) => onProviderChange(e.target.value)}
          >
            {providers.map((p) => (
              <option key={p.key} value={p.key} disabled={!p.implemented}>
                {p.key}
                {p.implemented ? "" : " — not implemented"}
              </option>
            ))}
          </select>
          {activeProvider ? (
            <p className="field-note">{activeProvider.description}</p>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

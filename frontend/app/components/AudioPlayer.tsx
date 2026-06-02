"use client";

import { useEffect, useRef, useState } from "react";
import { audioUrl } from "../../lib/api";
import { fmtDate, fmtDuration } from "../../lib/format";
import type { Generation } from "../../lib/types";

function trackSeed(track: Generation): number | undefined {
  if (typeof track.seed === "number") return track.seed;
  const fromParams = track.parameters?.seed;
  return typeof fromParams === "number" ? fromParams : undefined;
}

export default function AudioPlayer({
  track,
  loop,
  busy,
  onToggleLoop,
  onRegenerate,
}: {
  track: Generation | null;
  loop: boolean;
  busy: boolean;
  onToggleLoop: (value: boolean) => void;
  onRegenerate: (sameSeed: boolean) => void;
}) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [copied, setCopied] = useState(false);

  // Reload + attempt autoplay whenever the selected track changes.
  useEffect(() => {
    const el = audioRef.current;
    if (el && track) {
      el.load();
      el.play().catch(() => {
        /* autoplay may be blocked; the user can press play */
      });
    }
  }, [track?.id]);

  if (!track) {
    return (
      <div className="empty">
        No track yet — pick a scene, set your parameters, and press Generate.
      </div>
    );
  }

  const seed = trackSeed(track);

  const copyPrompt = async () => {
    try {
      await navigator.clipboard.writeText(track.prompt);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      /* clipboard may be unavailable; ignore */
    }
  };

  return (
    <div className="player">
      <div className="track-title">
        {track.scene} · {track.mood}
      </div>
      <div className="track-meta">
        {fmtDuration(track.duration)} · {track.bpm} BPM · intensity{" "}
        {track.intensity}/10 · {track.provider}
        {seed !== undefined ? ` · seed ${seed}` : ""}
      </div>

      <audio
        ref={audioRef}
        src={audioUrl(track)}
        controls
        loop={loop}
        preload="auto"
      />

      <div className="player-actions">
        <label className="switch">
          <input
            type="checkbox"
            checked={loop}
            onChange={(e) => onToggleLoop(e.target.checked)}
          />
          Loop
        </label>
        <a className="btn" href={audioUrl(track, true)} download>
          ⬇ Download
        </a>
      </div>

      <div className="regen-row">
        <button
          className="btn"
          onClick={() => onRegenerate(true)}
          disabled={busy || seed === undefined}
          title="Recreate this exact track from its seed"
        >
          ↻ Regenerate (same seed)
        </button>
        <button
          className="btn"
          onClick={() => onRegenerate(false)}
          disabled={busy}
          title="Same settings, a fresh random variation"
        >
          🎲 New variation
        </button>
      </div>

      <div className="prompt-box">
        <div className="prompt-head">
          <span>Prompt</span>
          <button className="link-btn" onClick={copyPrompt}>
            {copied ? "✓ Copied" : "Copy"}
          </button>
        </div>
        <p>{track.prompt}</p>
      </div>

      <div className="chips">
        <span className="chip">{track.audio_format.toUpperCase()}</span>
        <span className="chip">{track.no_drums ? "No drums" : "With pulse"}</span>
        <span className="chip">{fmtDate(track.generated_at)}</span>
      </div>
    </div>
  );
}

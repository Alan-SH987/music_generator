"use client";

import { useEffect, useRef, useState } from "react";
import Waveform from "./Waveform";
import { audioUrl } from "../../lib/api";
import { fmtDate, fmtDuration } from "../../lib/format";
import type { Generation } from "../../lib/types";

function trackSeed(track: Generation): number | undefined {
  if (typeof track.seed === "number") return track.seed;
  const fromParams = track.parameters?.seed;
  return typeof fromParams === "number" ? fromParams : undefined;
}

function computePeaks(buffer: AudioBuffer, columns = 500): number[] {
  const data = buffer.getChannelData(0);
  const block = Math.max(1, Math.floor(data.length / columns));
  const peaks: number[] = [];
  for (let i = 0; i < columns; i++) {
    const start = i * block;
    let max = 0;
    for (let j = 0; j < block; j++) {
      const v = Math.abs(data[start + j] || 0);
      if (v > max) max = v;
    }
    peaks.push(max);
  }
  const norm = Math.max(...peaks) || 1;
  return peaks.map((v) => v / norm);
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
  const [src, setSrc] = useState<string | null>(null);
  const [peaks, setPeaks] = useState<number[] | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  // Fetch the audio once, decode it for the waveform, and reuse the blob for
  // playback (avoids downloading the file twice).
  useEffect(() => {
    if (!track) {
      setSrc(null);
      setPeaks(null);
      return;
    }
    let cancelled = false;
    let blobUrl: string | null = null;
    setPeaks(null);
    setAnalyzing(true);

    (async () => {
      try {
        const res = await fetch(audioUrl(track));
        const buf = await res.arrayBuffer();
        if (cancelled) return;
        blobUrl = URL.createObjectURL(new Blob([buf], { type: "audio/wav" }));
        setSrc(blobUrl);
        const Ctx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
        const ctx = new Ctx();
        const decoded = await ctx.decodeAudioData(buf);
        await ctx.close();
        if (!cancelled) setPeaks(computePeaks(decoded));
      } catch {
        // Fallback: stream directly from the server (no waveform).
        if (!cancelled) {
          setSrc(audioUrl(track));
          setPeaks(null);
        }
      } finally {
        if (!cancelled) setAnalyzing(false);
      }
    })();

    return () => {
      cancelled = true;
      if (blobUrl) URL.revokeObjectURL(blobUrl);
    };
  }, [track?.id]);

  // Load + attempt autoplay when the source is ready.
  useEffect(() => {
    const el = audioRef.current;
    if (el && src) {
      el.load();
      el.play().catch(() => {
        /* autoplay may be blocked; the user can press play */
      });
    }
  }, [src]);

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

      <Waveform peaks={peaks} audioRef={audioRef} loading={analyzing} />

      <audio
        ref={audioRef}
        src={src ?? undefined}
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

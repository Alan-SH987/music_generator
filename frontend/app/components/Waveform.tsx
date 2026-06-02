"use client";

import { useEffect, useRef } from "react";

/**
 * Canvas waveform with a playback-progress overlay and click-to-seek.
 * `peaks` are normalized 0..1 amplitudes (one per bar); pass null while loading.
 */
export default function Waveform({
  peaks,
  audioRef,
  loading,
}: {
  peaks: number[] | null;
  audioRef: React.RefObject<HTMLAudioElement | null>;
  loading: boolean;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const render = () => {
      const dpr = window.devicePixelRatio || 1;
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      if (canvas.width !== Math.floor(w * dpr) || canvas.height !== Math.floor(h * dpr)) {
        canvas.width = Math.floor(w * dpr);
        canvas.height = Math.floor(h * dpr);
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);

      const audio = audioRef.current;
      const progress = audio && audio.duration ? audio.currentTime / audio.duration : 0;

      if (peaks && peaks.length) {
        const n = peaks.length;
        const barW = w / n;
        for (let i = 0; i < n; i++) {
          const bh = Math.max(2, peaks[i] * (h - 6));
          const played = i / n <= progress;
          ctx.fillStyle = played ? "#6ea8fe" : "#33405e";
          ctx.fillRect(i * barW, (h - bh) / 2, Math.max(1, barW - 1), bh);
        }
        // playhead
        ctx.fillStyle = "rgba(232,237,246,0.6)";
        ctx.fillRect(progress * w, 0, 1, h);
      } else {
        ctx.fillStyle = "#33405e";
        ctx.fillRect(0, h / 2 - 1, w, 2);
      }
      rafRef.current = requestAnimationFrame(render);
    };

    rafRef.current = requestAnimationFrame(render);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [peaks, audioRef]);

  const seek = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const audio = audioRef.current;
    const canvas = canvasRef.current;
    if (!audio || !canvas || !audio.duration) return;
    const rect = canvas.getBoundingClientRect();
    const ratio = (e.clientX - rect.left) / rect.width;
    audio.currentTime = Math.min(1, Math.max(0, ratio)) * audio.duration;
  };

  return (
    <div className={`waveform-wrap ${loading ? "is-loading" : ""}`}>
      <canvas ref={canvasRef} className="waveform" onClick={seek} title="Click to seek" />
      {loading ? <span className="waveform-hint">analyzing…</span> : null}
    </div>
  );
}

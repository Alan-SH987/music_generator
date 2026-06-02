"use client";

import { fmtDate } from "../../lib/format";
import type { Generation } from "../../lib/types";

export default function HistoryList({
  items,
  currentId,
  onSelect,
  onDelete,
  onClear,
}: {
  items: Generation[];
  currentId: string | null;
  onSelect: (gen: Generation) => void;
  onDelete: (id: string) => void;
  onClear: () => void;
}) {
  if (!items.length) {
    return <div className="empty">No history yet. Your generated tracks appear here.</div>;
  }

  return (
    <>
      <div className="history-toolbar">
        <span className="muted-sm">{items.length} track(s)</span>
        <button className="link-btn danger" onClick={onClear}>
          Clear all
        </button>
      </div>
      <div className="history-list">
        {items.map((g) => (
          <div
            key={g.id}
            className={`history-item ${currentId === g.id ? "active" : ""}`}
            onClick={() => onSelect(g)}
          >
            <div className="h-main">
              <div className="h-title">
                {g.scene} · {g.mood}
              </div>
              <div className="h-meta">
                {g.duration}s · {g.bpm} BPM · {g.provider} · {fmtDate(g.generated_at)}
              </div>
            </div>
            <button
              className="icon-btn"
              title="Delete this track"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(g.id);
              }}
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </>
  );
}

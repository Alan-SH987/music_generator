"use client";

import type { Scene } from "../../lib/types";

export default function SceneSelector({
  scenes,
  selected,
  onSelect,
}: {
  scenes: Scene[];
  selected: string | null;
  onSelect: (scene: Scene) => void;
}) {
  return (
    <div className="scene-grid">
      {scenes.map((s) => (
        <button
          key={s.key}
          type="button"
          className={`scene-btn ${selected === s.key ? "active" : ""}`}
          onClick={() => onSelect(s)}
          title={s.description}
        >
          <div className="zh">{s.label_zh}</div>
          <div className="en">{s.label_en}</div>
        </button>
      ))}
    </div>
  );
}

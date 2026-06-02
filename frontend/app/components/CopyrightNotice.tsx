"use client";

import type { Generation, Policy } from "../../lib/types";

const FALLBACK_POLICY =
  "All tracks are generated as original, instrumental, royalty-free background music. " +
  "No vocals, no lyrics, no imitation of any artist, and no real song titles used as prompts.";

export default function CopyrightNotice({
  policy,
  track,
}: {
  policy: Policy | null;
  track: Generation | null;
}) {
  return (
    <div>
      <p className="policy-text">{policy?.policy ?? FALLBACK_POLICY}</p>

      {policy?.rules?.length ? (
        <ul className="rules">
          {policy.rules.map((rule) => (
            <li key={rule}>{rule}</li>
          ))}
        </ul>
      ) : null}

      {track ? (
        <div className="license-box">
          <div>
            <span className="src">Source:</span> {track.source_type} ·{" "}
            {track.provider}
          </div>
          <div style={{ marginTop: 6 }}>{track.license_note}</div>
        </div>
      ) : null}
    </div>
  );
}

"use client";

import { useMemo, useState } from "react";
import type { HeatmapTrack } from "@/lib/api";

export function EmotionGrid({ tracks }: { tracks: HeatmapTrack[] }) {
  const [hovered, setHovered] = useState<HeatmapTrack | null>(null);
  const maxAbsVal = useMemo(() => Math.max(0.05, ...tracks.map((t) => Math.abs(t.valence))), [tracks]);
  const maxInt = useMemo(() => Math.max(0.05, ...tracks.map((t) => t.intensity)), [tracks]);
  const maxVol = useMemo(() => Math.max(0.05, ...tracks.map((t) => t.volatility)), [tracks]);

  if (tracks.length === 0) return <p className="text-zinc-500 text-sm">No data. Run analysis first.</p>;

  const cellW = tracks.length > 60 ? 8 : tracks.length > 30 ? 14 : 22;

  const rows: { label: string; color: (t: HeatmapTrack) => string }[] = [
    {
      label: "valence",
      color: (t) => {
        const p = t.valence / maxAbsVal; // -1..1
        return p >= 0
          ? `rgba(251, 191, 36, ${0.1 + 0.9 * p})`
          : `rgba(99, 102, 241, ${0.1 + 0.9 * -p})`;
      },
    },
    { label: "intensity", color: (t) => `rgba(244, 63, 94, ${0.08 + 0.92 * (t.intensity / maxInt)})` },
    { label: "volatility", color: (t) => `rgba(52, 211, 153, ${0.08 + 0.92 * (t.volatility / maxVol)})` },
  ];

  return (
    <div>
      <div className="overflow-x-auto pb-2">
        <div className="min-w-fit">
          {rows.map((row) => (
            <div key={row.label} className="flex items-center gap-1 mb-1">
              <span className="w-20 shrink-0 text-right pr-2 text-[11px] uppercase tracking-wider text-zinc-500">
                {row.label}
              </span>
              {tracks.map((t) => (
                <button
                  key={`${row.label}-${t.track_index}`}
                  type="button"
                  aria-label={`${t.title} ${row.label}`}
                  onMouseEnter={() => setHovered(t)}
                  onMouseLeave={() => setHovered(null)}
                  className="h-7 rounded-[3px] transition-transform hover:scale-y-125 hover:ring-1 hover:ring-zinc-300"
                  style={{ width: cellW, backgroundColor: row.color(t) }}
                />
              ))}
            </div>
          ))}
        </div>
      </div>
      <p className="text-xs text-zinc-500 h-5 mt-1">
        {hovered ? (
          <>
            <span className="text-zinc-200 font-semibold">{hovered.title}</span>
            {" — "}valence {hovered.valence >= 0 ? "+" : ""}
            {hovered.valence.toFixed(2)} · intensity {(hovered.intensity * 100).toFixed(0)}% · volatility{" "}
            {(hovered.volatility * 100).toFixed(0)}%
          </>
        ) : (
          "Hover a cell — each column is a track in order. Valence: indigo = dark, amber = bright."
        )}
      </p>
    </div>
  );
}

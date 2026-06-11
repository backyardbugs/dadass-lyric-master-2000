"use client";

import { useMemo, useState } from "react";
import type { HeatmapTrack } from "@/lib/api";

const ROWS = [
  { key: "sadness" as const, label: "sadness", color: (a: number) => `rgba(244, 63, 94, ${a})` },
  { key: "anger" as const, label: "anger", color: (a: number) => `rgba(251, 146, 60, ${a})` },
  { key: "nostalgia" as const, label: "nostalgia", color: (a: number) => `rgba(129, 140, 248, ${a})` },
];

export function EmotionGrid({ tracks }: { tracks: HeatmapTrack[] }) {
  const [hovered, setHovered] = useState<HeatmapTrack | null>(null);
  const maxes = useMemo(
    () =>
      Object.fromEntries(
        ROWS.map((r) => [r.key, Math.max(0.05, ...tracks.map((t) => t[r.key]))]),
      ) as Record<(typeof ROWS)[number]["key"], number>,
    [tracks],
  );

  if (tracks.length === 0) return <p className="text-zinc-500 text-sm">No sentiment data. Run analysis first.</p>;

  return (
    <div>
      <div className="overflow-x-auto pb-2">
        <div className="min-w-fit">
          {ROWS.map((row) => (
            <div key={row.key} className="flex items-center gap-1 mb-1">
              <span className="w-20 shrink-0 text-right pr-2 text-[11px] uppercase tracking-wider text-zinc-500">
                {row.label}
              </span>
              {tracks.map((t) => {
                const intensity = 0.08 + 0.92 * (t[row.key] / maxes[row.key]);
                return (
                  <button
                    key={`${row.key}-${t.track_index}`}
                    type="button"
                    aria-label={`${t.title} ${row.label}`}
                    onMouseEnter={() => setHovered(t)}
                    onMouseLeave={() => setHovered(null)}
                    className="h-7 rounded-[3px] transition-transform hover:scale-y-125 hover:ring-1 hover:ring-zinc-300"
                    style={{
                      width: tracks.length > 60 ? 8 : tracks.length > 30 ? 14 : 22,
                      backgroundColor: row.color(intensity),
                    }}
                  />
                );
              })}
            </div>
          ))}
        </div>
      </div>
      <p className="text-xs text-zinc-500 h-5 mt-1">
        {hovered ? (
          <>
            <span className="text-zinc-200 font-semibold">{hovered.title}</span>
            {" — "}sad {(hovered.sadness * 100).toFixed(0)}% · angry {(hovered.anger * 100).toFixed(0)}% · nostalgic{" "}
            {(hovered.nostalgia * 100).toFixed(0)}%
          </>
        ) : (
          "Hover a cell — each column is a track, in playlist order."
        )}
      </p>
    </div>
  );
}

"use client";

import { useMemo, useState } from "react";
import type { HeatmapTrack } from "@/lib/api";
import { brightness, heat, whiplash } from "@/lib/tone";

export function EmotionGrid({ tracks }: { tracks: HeatmapTrack[] }) {
  const [hovered, setHovered] = useState<HeatmapTrack | null>(null);
  const maxH = useMemo(() => Math.max(10, ...tracks.map((t) => heat(t.intensity))), [tracks]);
  const maxW = useMemo(() => Math.max(10, ...tracks.map((t) => whiplash(t.volatility))), [tracks]);

  if (tracks.length === 0) return <p className="text-zinc-500 text-sm">No data. Run analysis first.</p>;

  const cellW = tracks.length > 60 ? 8 : tracks.length > 30 ? 14 : 22;

  const rows: { label: string; color: (t: HeatmapTrack) => string }[] = [
    {
      label: "brightness",
      color: (t) => {
        const p = (brightness(t.valence) - 50) / 50; // -1..1
        return p >= 0
          ? `rgba(251, 191, 36, ${0.1 + 0.9 * p})`
          : `rgba(99, 102, 241, ${0.1 + 0.9 * -p})`;
      },
    },
    { label: "heat", color: (t) => `rgba(244, 63, 94, ${0.08 + 0.92 * (heat(t.intensity) / maxH)})` },
    { label: "whiplash", color: (t) => `rgba(52, 211, 153, ${0.08 + 0.92 * (whiplash(t.volatility) / maxW)})` },
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
            {" — "}brightness {brightness(hovered.valence)} · heat {heat(hovered.intensity)} · whiplash{" "}
            {whiplash(hovered.volatility)}
          </>
        ) : (
          "Hover a cell — each column is a track in order. Brightness: indigo = dark, amber = bright."
        )}
      </p>
    </div>
  );
}

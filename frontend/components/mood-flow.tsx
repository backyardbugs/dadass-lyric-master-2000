"use client";

import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import type { HeatmapTrack } from "@/lib/api";

function FlowTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload?: HeatmapTrack }> }) {
  if (!active || !payload?.length) return null;
  const t = payload[0]?.payload;
  if (!t) return null;
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-900/95 px-3 py-2 text-xs shadow-xl">
      <p className="font-bold text-zinc-100">#{t.track_index + 1} {t.title}</p>
      <p className="text-amber-300">valence {t.valence >= 0 ? "+" : ""}{t.valence.toFixed(2)}</p>
      <p className="text-rose-400">intensity {(t.intensity * 100).toFixed(0)}%</p>
    </div>
  );
}

export function MoodFlow({ tracks }: { tracks: HeatmapTrack[] }) {
  if (tracks.length < 2) return <p className="text-zinc-500 text-sm">Need at least two tracks for an arc.</p>;

  return (
    <div className="h-[260px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={tracks} margin={{ top: 8, right: 16, bottom: 0, left: -18 }}>
          <defs>
            <linearGradient id="grad-val" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#fbbf24" stopOpacity={0.45} />
              <stop offset="50%" stopColor="#a1a1aa" stopOpacity={0.05} />
              <stop offset="100%" stopColor="#6366f1" stopOpacity={0.45} />
            </linearGradient>
          </defs>
          <XAxis
            dataKey="track_index"
            tick={{ fill: "#71717a", fontSize: 10 }}
            tickFormatter={(v: number) => `#${v + 1}`}
          />
          <YAxis tick={{ fill: "#71717a", fontSize: 10 }} tickFormatter={(v: number) => v.toFixed(1)} />
          <ReferenceLine y={0} stroke="#3f3f46" />
          <Tooltip content={<FlowTooltip />} />
          <Area type="monotone" dataKey="valence" stroke="#fbbf24" fill="url(#grad-val)" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="intensity" stroke="#f43f5e" strokeWidth={1.5} dot={false} strokeDasharray="4 3" />
        </ComposedChart>
      </ResponsiveContainer>
      <p className="text-[11px] text-zinc-600 mt-1">
        Solid: valence (above 0 = brighter, below = darker). Dashed: emotional intensity.
      </p>
    </div>
  );
}

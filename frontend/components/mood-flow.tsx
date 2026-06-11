"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
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
      <p className="text-rose-400">sadness {(t.sadness * 100).toFixed(0)}%</p>
      <p className="text-orange-400">anger {(t.anger * 100).toFixed(0)}%</p>
      <p className="text-indigo-400">nostalgia {(t.nostalgia * 100).toFixed(0)}%</p>
    </div>
  );
}

export function MoodFlow({ tracks }: { tracks: HeatmapTrack[] }) {
  if (tracks.length < 2) return <p className="text-zinc-500 text-sm">Need at least two tracks for an arc.</p>;

  return (
    <div className="h-[260px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={tracks} margin={{ top: 8, right: 16, bottom: 0, left: -18 }}>
          <defs>
            <linearGradient id="grad-sad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f43f5e" stopOpacity={0.5} />
              <stop offset="100%" stopColor="#f43f5e" stopOpacity={0.02} />
            </linearGradient>
            <linearGradient id="grad-ang" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#fb923c" stopOpacity={0.45} />
              <stop offset="100%" stopColor="#fb923c" stopOpacity={0.02} />
            </linearGradient>
            <linearGradient id="grad-nos" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#818cf8" stopOpacity={0.45} />
              <stop offset="100%" stopColor="#818cf8" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <XAxis
            dataKey="track_index"
            tick={{ fill: "#71717a", fontSize: 10 }}
            tickFormatter={(v: number) => `#${v + 1}`}
          />
          <YAxis
            tick={{ fill: "#71717a", fontSize: 10 }}
            tickFormatter={(v: number) => `${Math.round(v * 100)}%`}
          />
          <Tooltip content={<FlowTooltip />} />
          <Area type="monotone" dataKey="nostalgia" stroke="#818cf8" fill="url(#grad-nos)" strokeWidth={2} dot={false} />
          <Area type="monotone" dataKey="anger" stroke="#fb923c" fill="url(#grad-ang)" strokeWidth={2} dot={false} />
          <Area type="monotone" dataKey="sadness" stroke="#f43f5e" fill="url(#grad-sad)" strokeWidth={2} dot={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

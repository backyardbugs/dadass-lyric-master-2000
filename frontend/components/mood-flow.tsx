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
import { brightness, heat } from "@/lib/tone";

type Point = HeatmapTrack & { b: number; h: number };

function FlowTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload?: Point }> }) {
  if (!active || !payload?.length) return null;
  const t = payload[0]?.payload;
  if (!t) return null;
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-900/95 px-3 py-2 text-xs shadow-xl">
      <p className="font-bold text-zinc-100">#{t.track_index + 1} {t.title}</p>
      <p className="text-amber-300">brightness {t.b}/100</p>
      <p className="text-rose-400">heat {t.h}/100</p>
    </div>
  );
}

export function MoodFlow({ tracks }: { tracks: HeatmapTrack[] }) {
  if (tracks.length < 2) return <p className="text-zinc-500 text-sm">Need at least two tracks for an arc.</p>;
  const points: Point[] = tracks.map((t) => ({ ...t, b: brightness(t.valence), h: heat(t.intensity) }));

  return (
    <div>
      <div className="h-[250px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={points} margin={{ top: 8, right: 16, bottom: 0, left: -22 }}>
            <defs>
              <linearGradient id="grad-bright" x1="0" y1="0" x2="0" y2="1">
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
            <YAxis domain={[0, 100]} tick={{ fill: "#71717a", fontSize: 10 }} />
            <ReferenceLine y={50} stroke="#3f3f46" />
            <Tooltip content={<FlowTooltip />} />
            <Area type="monotone" dataKey="b" stroke="#fbbf24" fill="url(#grad-bright)" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="h" stroke="#f43f5e" strokeWidth={1.5} dot={false} strokeDasharray="4 3" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <p className="text-[11px] text-zinc-600 mt-1">
        Solid: brightness (above 50 = brighter, below = darker). Dashed: heat.
      </p>
    </div>
  );
}

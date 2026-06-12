"use client";

import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { HeatmapTrack } from "@/lib/api";
import { brightness, heat, whiplash } from "@/lib/tone";

type Point = HeatmapTrack & { b: number; h: number; w: number };

function MoodTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload?: Point }> }) {
  if (!active || !payload?.length) return null;
  const t = payload[0]?.payload;
  if (!t) return null;
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-900/95 px-3 py-2 text-xs shadow-xl">
      <p className="font-bold text-zinc-100">{t.title}</p>
      <p className="text-zinc-500 mb-1">{t.artist}</p>
      <p className="text-amber-300">brightness {t.b}/100</p>
      <p className="text-rose-400">heat {t.h}/100</p>
      <p className="text-emerald-400">whiplash {t.w}/100 (bubble size)</p>
    </div>
  );
}

export function MoodMap({ tracks }: { tracks: HeatmapTrack[] }) {
  if (tracks.length === 0) return <p className="text-zinc-500 text-sm">No data. Run analysis first.</p>;

  const points: Point[] = tracks.map((t) => ({
    ...t,
    b: brightness(t.valence),
    h: heat(t.intensity),
    w: whiplash(t.volatility),
  }));
  const hMax = Math.min(100, Math.max(30, ...points.map((p) => p.h)) * 1.15);

  return (
    <div className="relative">
      <div className="h-[380px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 18, right: 24, bottom: 8, left: -16 }}>
            <XAxis
              type="number"
              dataKey="b"
              domain={[0, 100]}
              tick={{ fill: "#71717a", fontSize: 10 }}
              name="brightness"
              label={{ value: "dark ← brightness → bright", position: "insideBottom", fill: "#a1a1aa", fontSize: 11, dy: 8 }}
            />
            <YAxis
              type="number"
              dataKey="h"
              domain={[0, hMax]}
              tick={{ fill: "#71717a", fontSize: 10 }}
              name="heat"
              label={{ value: "heat →", angle: -90, position: "insideTopLeft", fill: "#a1a1aa", fontSize: 11, dx: 18 }}
            />
            <ZAxis type="number" dataKey="w" range={[40, 420]} name="whiplash" />
            <ReferenceLine x={50} stroke="#3f3f46" strokeDasharray="4 4" />
            <Tooltip content={<MoodTooltip />} cursor={{ strokeDasharray: "3 3", stroke: "#52525b" }} />
            <Scatter data={points} isAnimationActive>
              {points.map((p, i) => {
                const hue = 240 + (p.b / 100) * 120; // indigo (dark) -> amber-ish (bright)
                return <Cell key={i} fill={`hsla(${hue}, 75%, 62%, 0.75)`} stroke="#18181b" />;
              })}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <span className="absolute left-12 top-2 text-[10px] uppercase tracking-widest text-indigo-400/80">dark &amp; charged</span>
      <span className="absolute right-4 top-2 text-[10px] uppercase tracking-widest text-amber-400/80">bright &amp; charged</span>
      <span className="absolute left-12 bottom-12 text-[10px] uppercase tracking-widest text-zinc-500">dark &amp; understated</span>
      <span className="absolute right-4 bottom-12 text-[10px] uppercase tracking-widest text-zinc-500">bright &amp; understated</span>
    </div>
  );
}

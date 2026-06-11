"use client";

import { useMemo } from "react";
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

function MoodTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload?: HeatmapTrack }> }) {
  if (!active || !payload?.length) return null;
  const t = payload[0]?.payload;
  if (!t) return null;
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-900/95 px-3 py-2 text-xs shadow-xl">
      <p className="font-bold text-zinc-100">{t.title}</p>
      <p className="text-zinc-500 mb-1">{t.artist}</p>
      <p className="text-amber-300">valence {t.valence >= 0 ? "+" : ""}{t.valence.toFixed(2)}</p>
      <p className="text-rose-400">intensity {(t.intensity * 100).toFixed(0)}%</p>
      <p className="text-indigo-400">volatility {(t.volatility * 100).toFixed(0)}% (bubble size)</p>
    </div>
  );
}

export function MoodMap({ tracks }: { tracks: HeatmapTrack[] }) {
  const xAbs = useMemo(
    () => Math.max(0.15, ...tracks.map((t) => Math.abs(t.valence))) * 1.1,
    [tracks],
  );
  const yMax = useMemo(() => Math.max(0.15, ...tracks.map((t) => t.intensity)) * 1.1, [tracks]);

  if (tracks.length === 0) return <p className="text-zinc-500 text-sm">No data. Run analysis first.</p>;

  return (
    <div className="relative">
      <div className="h-[380px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 18, right: 24, bottom: 8, left: -16 }}>
            <XAxis
              type="number"
              dataKey="valence"
              domain={[-xAbs, xAbs]}
              tick={{ fill: "#71717a", fontSize: 10 }}
              tickFormatter={(v: number) => v.toFixed(1)}
              name="valence"
              label={{ value: "dark ← valence → bright", position: "insideBottom", fill: "#a1a1aa", fontSize: 11, dy: 8 }}
            />
            <YAxis
              type="number"
              dataKey="intensity"
              domain={[0, yMax]}
              tick={{ fill: "#71717a", fontSize: 10 }}
              tickFormatter={(v: number) => `${Math.round(v * 100)}%`}
              name="intensity"
              label={{ value: "intensity →", angle: -90, position: "insideTopLeft", fill: "#a1a1aa", fontSize: 11, dx: 18 }}
            />
            <ZAxis type="number" dataKey="volatility" range={[40, 420]} name="volatility" />
            <ReferenceLine x={0} stroke="#3f3f46" strokeDasharray="4 4" />
            <Tooltip content={<MoodTooltip />} cursor={{ strokeDasharray: "3 3", stroke: "#52525b" }} />
            <Scatter data={tracks} isAnimationActive>
              {tracks.map((t, i) => {
                const p = Math.max(0, Math.min(1, (t.valence + xAbs) / (2 * xAbs)));
                const hue = 240 + p * 120; // indigo (dark) -> amber-ish (bright)
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

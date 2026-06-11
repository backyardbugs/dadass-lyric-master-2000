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
      <p className="text-rose-400">sadness {(t.sadness * 100).toFixed(0)}%</p>
      <p className="text-orange-400">anger {(t.anger * 100).toFixed(0)}%</p>
      <p className="text-indigo-400">nostalgia {(t.nostalgia * 100).toFixed(0)}% (bubble size)</p>
    </div>
  );
}

export function MoodMap({ tracks }: { tracks: HeatmapTrack[] }) {
  const maxSad = useMemo(() => Math.max(0.05, ...tracks.map((t) => t.sadness)), [tracks]);
  const maxAng = useMemo(() => Math.max(0.05, ...tracks.map((t) => t.anger)), [tracks]);

  if (tracks.length === 0) return <p className="text-zinc-500 text-sm">No sentiment data. Run analysis first.</p>;

  const xMax = Math.ceil(maxSad * 110) / 100;
  const yMax = Math.ceil(maxAng * 110) / 100;

  return (
    <div className="relative">
      <div className="h-[380px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 18, right: 24, bottom: 8, left: -16 }}>
            <XAxis
              type="number"
              dataKey="sadness"
              domain={[0, xMax]}
              tick={{ fill: "#71717a", fontSize: 10 }}
              tickFormatter={(v: number) => `${Math.round(v * 100)}%`}
              name="sadness"
              label={{ value: "sadness →", position: "insideBottomRight", fill: "#a1a1aa", fontSize: 11, dy: 8 }}
            />
            <YAxis
              type="number"
              dataKey="anger"
              domain={[0, yMax]}
              tick={{ fill: "#71717a", fontSize: 10 }}
              tickFormatter={(v: number) => `${Math.round(v * 100)}%`}
              name="anger"
              label={{ value: "anger →", angle: -90, position: "insideTopLeft", fill: "#a1a1aa", fontSize: 11, dx: 18 }}
            />
            <ZAxis type="number" dataKey="nostalgia" range={[40, 420]} name="nostalgia" />
            <ReferenceLine x={xMax / 2} stroke="#3f3f46" strokeDasharray="4 4" />
            <ReferenceLine y={yMax / 2} stroke="#3f3f46" strokeDasharray="4 4" />
            <Tooltip content={<MoodTooltip />} cursor={{ strokeDasharray: "3 3", stroke: "#52525b" }} />
            <Scatter data={tracks} isAnimationActive>
              {tracks.map((t, i) => {
                const sad = t.sadness / xMax;
                const ang = t.anger / yMax;
                const hue = 350 - sad * 60 + ang * 30;
                return <Cell key={i} fill={`hsla(${hue}, 85%, ${58 - sad * 12}%, 0.75)`} stroke="#18181b" />;
              })}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <span className="absolute left-12 top-2 text-[10px] uppercase tracking-widest text-orange-400/70">mad, not sad</span>
      <span className="absolute right-4 top-2 text-[10px] uppercase tracking-widest text-rose-400/80">sad AND mad</span>
      <span className="absolute left-12 bottom-10 text-[10px] uppercase tracking-widest text-zinc-500">suspiciously fine</span>
      <span className="absolute right-4 bottom-10 text-[10px] uppercase tracking-widest text-rose-300/70">pure heartbreak</span>
    </div>
  );
}

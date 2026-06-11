"use client";

import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { TrendYear } from "@/lib/api";

function TrendTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload?: TrendYear }> }) {
  if (!active || !payload?.length) return null;
  const y = payload[0]?.payload;
  if (!y) return null;
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-900/95 px-3 py-2 text-xs shadow-xl">
      <p className="font-bold text-zinc-100">{y.year} · {y.tracks} track{y.tracks === 1 ? "" : "s"}</p>
      <p className="text-amber-300">valence {y.valence >= 0 ? "+" : ""}{y.valence.toFixed(2)}</p>
      <p className="text-sky-400">lexical diversity {(y.diversity * 100).toFixed(0)}%</p>
      <p className="text-violet-400">rhyme density {(y.rhyme_density * 100).toFixed(0)}%</p>
      <p className="text-zinc-400">{y.words_per_track.toFixed(0)} words/track</p>
    </div>
  );
}

export function TrendsChart({ years }: { years: TrendYear[] }) {
  if (years.length < 2)
    return (
      <p className="text-zinc-500 text-sm">
        Release years aren&apos;t available for this dataset — fetch an artist or album to see
        how the writing changed over time.
      </p>
    );

  return (
    <div className="h-[280px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={years} margin={{ top: 8, right: 16, bottom: 0, left: -18 }}>
          <XAxis dataKey="year" tick={{ fill: "#71717a", fontSize: 10 }} />
          <YAxis tick={{ fill: "#71717a", fontSize: 10 }} />
          <ReferenceLine y={0} stroke="#3f3f46" />
          <Tooltip content={<TrendTooltip />} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Line type="monotone" dataKey="valence" name="valence" stroke="#fbbf24" strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="diversity" name="lexical diversity" stroke="#38bdf8" strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="rhyme_density" name="rhyme density" stroke="#a78bfa" strokeWidth={2} dot={{ r: 3 }} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

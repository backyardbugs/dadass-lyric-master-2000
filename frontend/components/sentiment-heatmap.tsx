"use client";

import { useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import type { HeatmapTrack } from "@/lib/api";

export function SentimentHeatmap({ tracks }: { tracks: HeatmapTrack[] }) {
  const data = useMemo(() => tracks.map((t) => ({ ...t, name: t.title.slice(0, 20) + (t.title.length > 20 ? "…" : "") })), [tracks]);
  const maxSad = useMemo(() => Math.max(0.01, ...tracks.map((t) => t.sadness)), [tracks]);

  if (tracks.length === 0) return <p className="text-zinc-500 text-sm">No sentiment data. Run analysis first.</p>;

  return (
    <div className="h-[400px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ left: 80, right: 20 }}>
          <XAxis type="number" domain={[0, 1]} tick={{ fill: "#a1a1aa" }} />
          <YAxis type="category" dataKey="name" width={80} tick={{ fill: "#a1a1aa", fontSize: 10 }} />
          <Tooltip
            contentStyle={{ backgroundColor: "#27272a", border: "1px solid #3f3f46" }}
            labelStyle={{ color: "#fafafa" }}
            formatter={(value: number | undefined) => [value != null ? value.toFixed(2) : "—", "Sadness"]}
            labelFormatter={(_, payload) => payload[0]?.payload?.title && `${payload[0].payload.artist} — ${payload[0].payload.title}`}
          />
          <Bar dataKey="sadness" radius={2} fill="#f43f5e">
            {data.map((entry, i) => (
              <Cell key={i} fill={`rgba(244, 63, 94, ${0.3 + 0.7 * (entry.sadness / maxSad)})`} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

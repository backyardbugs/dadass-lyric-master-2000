"use client";

import type { Stats, Superlative } from "@/lib/api";
import { brightness, whiplash } from "@/lib/tone";

function HighlightCard({
  title,
  item,
  format,
  accent,
}: {
  title: string;
  item: Superlative;
  format: (v: number) => string;
  accent: string;
}) {
  if (!item) return null;
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/70 p-4 hover:border-zinc-600 hover:-translate-y-0.5 transition-all">
      <p className={`text-[11px] uppercase tracking-widest font-semibold ${accent}`}>{title}</p>
      <p className="font-bold leading-tight mt-2">{item.title}</p>
      <p className="text-xs text-zinc-500 truncate">{item.artist}</p>
      <p className={`text-sm mt-2 font-mono ${accent}`}>{format(item.value)}</p>
    </div>
  );
}

export function StatCards({ stats }: { stats: Stats }) {
  const s = stats.superlatives;
  if (!s) return null;
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/70 p-3">
          <p className="text-2xl font-black">{stats.track_count?.toLocaleString()}</p>
          <p className="text-xs text-zinc-500">tracks</p>
        </div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/70 p-3">
          <p className="text-2xl font-black">{stats.total_words?.toLocaleString()}</p>
          <p className="text-xs text-zinc-500">words</p>
        </div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/70 p-3">
          <p className="text-2xl font-black">{stats.unique_words?.toLocaleString()}</p>
          <p className="text-xs text-zinc-500">unique words</p>
        </div>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <HighlightCard
          title="Darkest track"
          item={s.darkest}
          format={(v) => `brightness ${brightness(v)}/100`}
          accent="text-indigo-400"
        />
        <HighlightCard
          title="Brightest track"
          item={s.brightest}
          format={(v) => `brightness ${brightness(v)}/100`}
          accent="text-amber-400"
        />
        <HighlightCard
          title="Biggest mood swings"
          item={s.most_volatile}
          format={(v) => `whiplash ${whiplash(v)}/100`}
          accent="text-emerald-400"
        />
        <HighlightCard
          title="Biggest vocabulary"
          item={s.biggest_vocabulary}
          format={(v) => `${v} unique words`}
          accent="text-sky-400"
        />
        <HighlightCard
          title="Most repetitive"
          item={s.most_repetitive}
          format={(v) => `${(v * 100).toFixed(0)}% repeated lines`}
          accent="text-rose-400"
        />
        <HighlightCard
          title="Densest rhymes"
          item={s.densest_rhymes}
          format={(v) => `${(v * 100).toFixed(0)}% line endings rhyme`}
          accent="text-violet-400"
        />
      </div>
    </div>
  );
}

"use client";

import type { Stats, Superlative } from "@/lib/api";

function AwardCard({
  award,
  title,
  item,
  format,
  accent,
}: {
  award: string;
  title: string;
  item: Superlative;
  format: (v: number) => string;
  accent: string;
}) {
  if (!item) return null;
  return (
    <div className={`rounded-xl border border-zinc-800 bg-zinc-900/70 p-4 hover:border-zinc-600 hover:-translate-y-0.5 transition-all`}>
      <p className={`text-[11px] uppercase tracking-widest font-semibold ${accent}`}>{award}</p>
      <p className="text-sm text-zinc-500 mb-2">{title}</p>
      <p className="font-bold leading-tight">{item.title}</p>
      <p className="text-xs text-zinc-500 truncate">{item.artist}</p>
      <p className={`text-sm mt-2 font-mono ${accent}`}>{format(item.value)}</p>
    </div>
  );
}

export function StatCards({ stats }: { stats: Stats }) {
  const s = stats.superlatives;
  if (!s) return null;
  const pct = (v: number) => `${(v * 100).toFixed(0)}% intensity`;
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/70 p-3">
          <p className="text-2xl font-black">{stats.track_count?.toLocaleString()}</p>
          <p className="text-xs text-zinc-500">tracks</p>
        </div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/70 p-3">
          <p className="text-2xl font-black">{stats.total_words?.toLocaleString()}</p>
          <p className="text-xs text-zinc-500">words sung</p>
        </div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/70 p-3">
          <p className="text-2xl font-black">{stats.unique_words?.toLocaleString()}</p>
          <p className="text-xs text-zinc-500">unique words</p>
        </div>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <AwardCard award="The Wettest Pillow" title="Saddest track" item={s.saddest} format={pct} accent="text-rose-400" />
        <AwardCard award="Most Slammed Door" title="Angriest track" item={s.angriest} format={pct} accent="text-orange-400" />
        <AwardCard award="Yearbook Signature" title="Most nostalgic" item={s.most_nostalgic} format={pct} accent="text-indigo-400" />
        <AwardCard
          award="Walking Thesaurus"
          title="Biggest vocabulary"
          item={s.biggest_vocabulary}
          format={(v) => `${v} unique words`}
          accent="text-emerald-400"
        />
        <AwardCard
          award="Broken Record"
          title="Most repetitive"
          item={s.most_repetitive}
          format={(v) => `${(v * 100).toFixed(0)}% unique words`}
          accent="text-amber-400"
        />
        <AwardCard
          award="The Novelist"
          title="Wordiest track"
          item={s.wordiest}
          format={(v) => `${v} words`}
          accent="text-sky-400"
        />
      </div>
    </div>
  );
}

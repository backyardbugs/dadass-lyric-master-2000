"use client";

import type { Craft } from "@/lib/api";

export function SignatureWords({
  craft,
  onWordClick,
}: {
  craft: Craft;
  onWordClick?: (word: string) => void;
}) {
  const words = craft.signature_words ?? [];
  if (words.length === 0)
    return <p className="text-zinc-500 text-sm">Not enough data — fetch a few more songs.</p>;
  const maxScore = Math.max(...words.map((w) => w.score), 0.001);
  return (
    <div>
      <ul className="space-y-1.5">
        {words.slice(0, 18).map((w) => (
          <li key={w.word} className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => onWordClick?.(w.word)}
              className="w-28 shrink-0 text-right font-bold text-rose-300 hover:text-rose-200 hover:underline truncate"
              title={`See lyric lines with “${w.word}”`}
            >
              {w.word}
            </button>
            <div className="flex-1 h-3 rounded bg-zinc-800 overflow-hidden">
              <div
                className="h-full rounded bg-gradient-to-r from-rose-600 to-amber-500"
                style={{ width: `${Math.max(4, (w.score / maxScore) * 100)}%` }}
              />
            </div>
            <span className="w-48 shrink-0 text-xs text-zinc-500">
              <span className="font-mono text-zinc-300">{w.ratio >= 100 ? Math.round(w.ratio) : w.ratio}×</span> vs
              everyday English · {w.songs} song{w.songs === 1 ? "" : "s"}
            </span>
          </li>
        ))}
      </ul>
      <p className="text-[11px] text-zinc-600 mt-3">
        &ldquo;28× vs everyday English&rdquo; means the word shows up 28 times more often in these lyrics than
        in ordinary written English — a deliberate word choice, not background vocabulary. Click a word
        to see every line it appears in.
      </p>
    </div>
  );
}

export function Hooks({ craft }: { craft: Craft }) {
  const hooks = craft.hooks ?? [];
  if (hooks.length === 0)
    return <p className="text-zinc-500 text-sm">No heavily repeated lines found.</p>;
  return (
    <ul className="space-y-2">
      {hooks.slice(0, 8).map((h, i) => (
        <li key={i} className="flex items-baseline gap-3 border-b border-zinc-800/70 pb-2">
          <span className="shrink-0 font-mono text-amber-400 text-sm">×{h.count}</span>
          <div className="min-w-0">
            <p className="italic text-zinc-200 leading-snug">&ldquo;{h.line}&rdquo;</p>
            <p className="text-[11px] text-zinc-500">
              {h.songs > 1 ? `${h.songs} songs, incl. ` : ""}{h.example}
            </p>
          </div>
        </li>
      ))}
    </ul>
  );
}

export function RhymePairs({ craft }: { craft: Craft }) {
  const pairs = craft.rhyme_pairs ?? [];
  if (pairs.length === 0)
    return <p className="text-zinc-500 text-sm">No repeated end-rhyme pairs found.</p>;
  return (
    <div>
      <div className="flex flex-wrap gap-2">
        {pairs.map((p, i) => (
          <span
            key={i}
            className="px-3 py-1.5 rounded-full border border-violet-500/30 bg-violet-500/10 text-sm"
          >
            <span className="font-bold">{p.a}</span>
            <span className="text-zinc-500 mx-1">/</span>
            <span className="font-bold">{p.b}</span>
            <span className="text-zinc-500 text-xs ml-1.5 font-mono">×{p.count}</span>
          </span>
        ))}
      </div>
      <p className="text-[11px] text-zinc-600 mt-3">
        Perfect end-rhymes within two lines of each other (CMU pronunciation dictionary), counted
        across the whole dataset.
      </p>
    </div>
  );
}

const POV_ROWS = [
  { key: "i" as const, label: "I / me / my", desc: "confessional", color: "bg-rose-500" },
  { key: "you" as const, label: "you / your", desc: "direct address", color: "bg-amber-500" },
  { key: "we" as const, label: "we / us / our", desc: "communal", color: "bg-emerald-500" },
  { key: "they" as const, label: "he / she / they", desc: "narrative", color: "bg-sky-500" },
];

export function PovProfile({ craft }: { craft: Craft }) {
  const pov = craft.pov;
  if (!pov || !pov.total) return <p className="text-zinc-500 text-sm">No pronoun data yet.</p>;
  return (
    <div>
      <div className="flex h-5 rounded-full overflow-hidden mb-4">
        {POV_ROWS.map((r) => (
          <div key={r.key} className={r.color} style={{ width: `${pov[r.key] * 100}%` }} />
        ))}
      </div>
      <ul className="space-y-2">
        {POV_ROWS.map((r) => (
          <li key={r.key} className="flex items-center gap-2 text-sm">
            <span className={`w-2.5 h-2.5 rounded-full ${r.color}`} />
            <span className="w-28 font-semibold">{r.label}</span>
            <span className="font-mono text-zinc-300">{(pov[r.key] * 100).toFixed(0)}%</span>
            <span className="text-zinc-500 text-xs">{r.desc}</span>
          </li>
        ))}
      </ul>
      <p className="text-[11px] text-zinc-600 mt-3">
        Share of all pronoun uses ({pov.total.toLocaleString()} total). Who the songs are written to —
        and from.
      </p>
    </div>
  );
}

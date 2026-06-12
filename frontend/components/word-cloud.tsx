"use client";

import { useEffect, useState } from "react";
import { getTopWords } from "@/lib/api";

type WordItem = { word: string; count: number };

const POS_TABS = [
  { key: undefined, label: "Everything" },
  { key: "noun", label: "Nouns" },
  { key: "verb", label: "Verbs" },
  { key: "adjective", label: "Adjectives" },
] as const;

const PALETTE = [
  "text-rose-400 hover:bg-rose-500/20",
  "text-fuchsia-400 hover:bg-fuchsia-500/20",
  "text-violet-400 hover:bg-violet-500/20",
  "text-sky-400 hover:bg-sky-500/20",
  "text-amber-400 hover:bg-amber-500/20",
  "text-emerald-400 hover:bg-emerald-500/20",
  "text-zinc-300 hover:bg-zinc-500/20",
];

/** Deterministic hash so each word keeps its color/tilt across renders. */
function hash(word: string): number {
  let h = 0;
  for (let i = 0; i < word.length; i++) h = (h * 31 + word.charCodeAt(i)) | 0;
  return Math.abs(h);
}

function fontSize(count: number, min: number, max: number): number {
  if (max <= min) return 16;
  const p = Math.sqrt((count - min) / (max - min));
  return Math.round(13 + p * 30);
}

export function WordCloud({
  words,
  onWordClick,
}: {
  words: WordItem[];
  onWordClick?: (word: string) => void;
}) {
  const [pos, setPos] = useState<string | undefined>(undefined);
  const [shown, setShown] = useState<WordItem[]>(words);
  const [loading, setLoading] = useState(false);
  const [showAll, setShowAll] = useState(false);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getTopWords(pos, 600)
      .then((res) => !cancelled && setShown(pos === undefined && res.top_words.length === 0 ? words : res.top_words))
      .catch(() => !cancelled && setShown(pos === undefined ? words : []))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [pos, words]);

  if (words.length === 0) return <p className="text-zinc-500 text-sm">No words yet. Run analysis first.</p>;

  const counts = shown.map((w) => w.count);
  const min = counts.length ? Math.min(...counts) : 0;
  const max = counts.length ? Math.max(...counts) : 1;

  return (
    <div>
      <div className="flex flex-wrap gap-2 mb-4 items-center">
        {POS_TABS.map((tab) => (
          <button
            key={tab.label}
            type="button"
            onClick={() => setPos(tab.key)}
            className={`px-3 py-1 rounded-full text-xs font-semibold border transition-colors ${
              pos === tab.key
                ? "bg-rose-600 border-rose-600 text-white"
                : "border-zinc-700 text-zinc-400 hover:border-zinc-500 hover:text-zinc-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
        <button
          type="button"
          onClick={() => setShowAll(!showAll)}
          className="ml-auto px-3 py-1 rounded-full text-xs font-semibold border border-zinc-700 text-zinc-400 hover:border-zinc-500 hover:text-zinc-200 transition-colors"
        >
          {showAll ? "Cloud view" : "Full list"}
        </button>
      </div>
      {loading ? (
        <p className="text-zinc-500 text-sm p-4">Loading…</p>
      ) : shown.length === 0 ? (
        <p className="text-zinc-500 text-sm p-4">Nothing here — run Analyze again to tag parts of speech.</p>
      ) : showAll ? (
        <div>
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Search words…"
            className="w-full max-w-xs mb-3 rounded-md bg-zinc-800 border border-zinc-700 px-3 py-1.5 text-sm outline-none focus:border-zinc-500"
          />
          <div className="max-h-[360px] overflow-y-auto rounded-lg border border-zinc-800">
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
              {shown
                .filter((w) => !filter || w.word.includes(filter.toLowerCase()))
                .map((w) => (
                  <button
                    key={w.word}
                    type="button"
                    onClick={() => onWordClick?.(w.word)}
                    className="flex justify-between gap-2 px-3 py-1.5 text-sm hover:bg-zinc-800/60 text-left border-b border-r border-zinc-800/50"
                  >
                    <span className="truncate">{w.word}</span>
                    <span className="text-zinc-500 font-mono text-xs">{w.count}</span>
                  </button>
                ))}
            </div>
          </div>
          <p className="text-[11px] text-zinc-600 mt-2">
            All {shown.length} words{pos ? ` tagged as ${pos}s` : ""}, by count. Click one for its lyric lines.
          </p>
        </div>
      ) : (
        <div className="flex flex-wrap gap-x-2 gap-y-1 justify-center items-baseline p-4 min-h-[200px]">
          {shown.slice(0, 80).map((w, i) => {
            const h = hash(w.word);
            const tilt = (h % 5) - 2;
            return (
              <button
                key={w.word}
                type="button"
                title={`“${w.word}” × ${w.count} — click for lyric lines`}
                className={`rounded px-1.5 font-bold leading-tight transition-transform duration-150 hover:scale-125 hover:z-10 animate-float-in ${PALETTE[h % PALETTE.length]}`}
                style={{
                  fontSize: fontSize(w.count, min, max),
                  transform: `rotate(${tilt}deg)`,
                  animationDelay: `${Math.min(i * 18, 900)}ms`,
                }}
                onClick={() => onWordClick?.(w.word)}
              >
                {w.word}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

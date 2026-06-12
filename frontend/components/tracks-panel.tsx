"use client";

import { useMemo, useState } from "react";
/* eslint-disable @next/next/no-img-element */
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { getTrack, type TrackSummary, type TrackDetail, type TrackLine, type WordStat } from "@/lib/api";
import { brightness, valenceColor } from "@/lib/tone";

const WORD_SPLIT = /([A-Za-z][A-Za-z']*)/;

type Lens = "plain" | "tone" | "concreteness" | "frequency";

const LENSES: { key: Lens; label: string; hint: string }[] = [
  { key: "plain", label: "Plain", hint: "" },
  { key: "tone", label: "Tone", hint: "Line background: indigo = dark, amber = bright." },
  { key: "concreteness", label: "Concrete vs abstract", hint: "Words colored by meaning in context (Gemini when available): green = concrete image, violet = abstract idea, gray = referential (you, somebody)." },
  { key: "frequency", label: "Their favorites", hint: "Stronger pink = a word this writer uses more across the dataset." },
];

const RHYME_COLORS = [
  "text-rose-300 border-rose-500/40",
  "text-sky-300 border-sky-500/40",
  "text-amber-300 border-amber-500/40",
  "text-emerald-300 border-emerald-500/40",
  "text-violet-300 border-violet-500/40",
  "text-pink-300 border-pink-500/40",
  "text-teal-300 border-teal-500/40",
  "text-orange-300 border-orange-500/40",
];

const ACT_STYLES: Record<string, string> = {
  question: "bg-sky-500/15 text-sky-300",
  command: "bg-orange-500/15 text-orange-300",
  promise: "bg-emerald-500/15 text-emerald-300",
  apology: "bg-violet-500/15 text-violet-300",
  plea: "bg-rose-500/15 text-rose-300",
  accusation: "bg-red-500/15 text-red-300",
  confession: "bg-amber-500/15 text-amber-300",
  exclamation: "bg-pink-500/15 text-pink-300",
};

function dotColor(v: number): string {
  const b = brightness(v);
  if (b > 55) return "bg-amber-400";
  if (b < 45) return "bg-indigo-400";
  return "bg-zinc-500";
}

function concColor(conc: number | undefined): string | undefined {
  if (conc === undefined) return undefined;
  if (conc >= 4) return "#6ee7b7";
  if (conc <= 2.5) return "#c4b5fd";
  return undefined;
}

function imageryColor(role: string | undefined): string | undefined {
  if (role === "concrete") return "#6ee7b7";
  if (role === "abstract") return "#c4b5fd";
  if (role === "referential") return "#71717a";
  return undefined;
}

function HoverableLine({
  line,
  lens,
  stats,
  maxCount,
  llmImagery,
  onHover,
  onWordClick,
}: {
  line: TrackLine;
  lens: Lens;
  stats: Record<string, WordStat>;
  maxCount: number;
  llmImagery?: Record<string, string>;
  onHover: (word: string | null, x: number, y: number) => void;
  onWordClick?: (word: string) => void;
}) {
  const parts = line.text.split(WORD_SPLIT);
  return (
    <span>
      {parts.map((part, i) => {
        const key = part.toLowerCase().replace(/^'+|'+$/g, "");
        const stat = i % 2 === 1 ? stats[key] : undefined;
        if (!stat) return <span key={i}>{part}</span>;
        const style: React.CSSProperties = {};
        if (lens === "concreteness") {
          const role = llmImagery?.[key];
          const c = role ? imageryColor(role) : concColor(stat.conc);
          if (c) style.color = c;
        } else if (lens === "frequency" && stat.count >= 3) {
          const p = Math.log(stat.count) / Math.log(Math.max(2, maxCount));
          style.backgroundColor = `rgba(244, 63, 94, ${0.12 + 0.45 * p})`;
          style.borderRadius = 3;
        }
        return (
          <span
            key={i}
            style={style}
            className="cursor-pointer rounded-sm hover:bg-rose-500/25 hover:text-rose-200"
            onMouseEnter={(e) => onHover(key, e.clientX, e.clientY)}
            onMouseLeave={() => onHover(null, 0, 0)}
            onClick={() => onWordClick?.(key)}
          >
            {part}
          </span>
        );
      })}
    </span>
  );
}

/** Line-by-line self-similarity matrix: choruses appear as bright blocks. */
function SimilarityMatrix({ lines }: { lines: string[] }) {
  const sets = useMemo(
    () => lines.map((l) => new Set(l.toLowerCase().match(/[a-z']+/g) || [])),
    [lines],
  );
  const n = Math.min(sets.length, 80);
  if (n < 6) return null;
  const size = Math.min(280, n * 6);
  const cell = size / n;
  const cells: React.ReactNode[] = [];
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (j > i) continue;
      const a = sets[i];
      const b = sets[j];
      if (!a.size || !b.size) continue;
      let inter = 0;
      a.forEach((w) => {
        if (b.has(w)) inter++;
      });
      const sim = inter / (a.size + b.size - inter);
      if (sim < 0.25) continue;
      cells.push(
        <rect key={`${i}-${j}`} x={j * cell} y={i * cell} width={cell} height={cell} fill={`rgba(244, 63, 94, ${0.25 + sim * 0.75})`} />,
        i !== j ? (
          <rect key={`${j}-${i}`} x={i * cell} y={j * cell} width={cell} height={cell} fill={`rgba(244, 63, 94, ${0.25 + sim * 0.75})`} />
        ) : null,
      );
    }
  }
  return (
    <div className="mt-1">
      <svg width={size} height={size} className="rounded border border-zinc-800 bg-zinc-950">
        {cells}
      </svg>
      <p className="text-[11px] text-zinc-600 mt-1 max-w-[280px]">
        Repetition fingerprint: each pixel compares two lines (top-left = start). Bright blocks =
        repeated sections like choruses.
      </p>
    </div>
  );
}

function MetricChip({ label, value }: { label: string; value: string }) {
  return (
    <span className="rounded-full border border-zinc-700 px-2.5 py-1 text-xs text-zinc-300">
      <span className="text-zinc-500">{label}</span> {value}
    </span>
  );
}

export function TracksPanel({
  tracks,
  wordStats,
  onWordClick,
}: {
  tracks: TrackSummary[];
  wordStats: Record<string, WordStat>;
  onWordClick?: (word: string) => void;
}) {
  const [open, setOpen] = useState<TrackDetail | null>(null);
  const [loadingId, setLoadingId] = useState<number | null>(null);
  const [hover, setHover] = useState<{ word: string; x: number; y: number } | null>(null);
  const [lens, setLens] = useState<Lens>("plain");
  const maxCount = useMemo(
    () => Math.max(1, ...Object.values(wordStats).map((s) => s.count)),
    [wordStats],
  );

  if (tracks.length === 0) return <p className="text-zinc-500 text-sm">No tracks. Run fetch first.</p>;

  const openTrack = async (t: TrackSummary) => {
    if (!t.has_lyrics) return;
    setLoadingId(t.id);
    try {
      setOpen(await getTrack(t.id));
    } catch {
      /* ignore */
    } finally {
      setLoadingId(null);
    }
  };

  const onHover = (word: string | null, x: number, y: number) => {
    setHover(word ? { word, x, y } : null);
  };
  const hoverStat = hover ? wordStats[hover.word] : null;

  const allLines = open ? open.sections.flatMap((s) => s.lines.map((l) => l.text)) : [];
  const rhymeLetters = open
    ? Array.from(new Set(open.sections.flatMap((s) => s.lines.map((l) => l.rhyme_letter)).filter(Boolean)))
    : [];
  const letterClass = (letter: string) =>
    RHYME_COLORS[rhymeLetters.indexOf(letter) % RHYME_COLORS.length] || RHYME_COLORS[0];

  return (
    <div>
      <div className="max-h-[420px] overflow-y-auto rounded-lg border border-zinc-800 divide-y divide-zinc-800/70">
        {tracks.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => openTrack(t)}
            disabled={!t.has_lyrics}
            className="w-full text-left px-3 py-2 hover:bg-zinc-800/50 disabled:opacity-40 disabled:cursor-default transition-colors"
          >
            <div className="flex items-center gap-2.5">
              {t.album_image ? (
                <img src={t.album_image} alt="" className="w-8 h-8 rounded object-cover shrink-0" />
              ) : (
                <span className="w-8 h-8 rounded bg-zinc-800 shrink-0" />
              )}
              <span className={`w-2 h-2 rounded-full shrink-0 ${dotColor(t.valence)}`} />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-semibold truncate">{t.title}</span>
                  {t.release_year && <span className="text-zinc-600 text-xs shrink-0">{t.release_year}</span>}
                  <span className="ml-auto shrink-0 text-xs text-zinc-500 font-mono">
                    {t.has_lyrics ? `${t.words}w` : "no lyrics"}
                  </span>
                </div>
                {t.has_lyrics && (
                  <p className="text-[11px] text-zinc-500 mt-0.5 truncate">
                    {t.structure || "—"}
                    {t.chorus_share > 0 && ` · chorus carries ${Math.round(t.chorus_share * 100)}% of words`}
                    {loadingId === t.id && " · loading…"}
                  </p>
                )}
              </div>
            </div>
          </button>
        ))}
      </div>
      <p className="text-[11px] text-zinc-600 mt-2">
        Dot = tone (indigo dark, amber bright). Click a track to read its lyrics with rhyme scheme,
        per-word data, and a repetition fingerprint.
      </p>

      <Dialog open={!!open} onOpenChange={(o) => !o && setOpen(null)}>
        <DialogContent className="bg-zinc-900 border-zinc-800 max-h-[85vh] overflow-y-auto max-w-3xl">
          {open && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-3">
                  {open.album_image && (
                    <img src={open.album_image} alt="" className="w-10 h-10 rounded object-cover" />
                  )}
                  <span>
                    {open.title}
                    <span className="text-zinc-500 font-normal"> — {open.artist}{open.release_year ? `, ${open.release_year}` : ""}</span>
                  </span>
                </DialogTitle>
              </DialogHeader>
              <div className="flex flex-wrap gap-1.5 mb-1">
                <MetricChip label="words" value={String(open.metrics.words ?? 0)} />
                <MetricChip label="unique" value={String(open.metrics.unique_words ?? 0)} />
                <MetricChip label="brightness" value={`${brightness(open.metrics.valence ?? 0)}/100`} />
                <MetricChip label="syllables/line" value={(open.metrics.syllables_per_line ?? 0).toFixed(1)} />
                <MetricChip
                  label="rhyme"
                  value={`${Math.round(((open.metrics.perfect_rhyme_density ?? 0) + (open.metrics.slant_rhyme_density ?? 0)) * 100)}% (${Math.round((open.metrics.slant_rhyme_density ?? 0) * 100)}% slant)`}
                />
                <MetricChip label="repeated lines" value={`${Math.round((open.metrics.repetition ?? 0) * 100)}%`} />
                {open.chorus_share > 0 && (
                  <MetricChip label="chorus share" value={`${Math.round(open.chorus_share * 100)}%`} />
                )}
              </div>
              {open.summary && <p className="text-xs text-zinc-500 font-mono">{open.summary}</p>}
              {open.llm?.summary && (
                <p className="text-xs text-emerald-400/90 mt-1 leading-relaxed">{open.llm.summary}</p>
              )}

              {open.llm?.metaphors && open.llm.metaphors.length > 0 && (
                <div className="rounded-lg border border-zinc-800 bg-zinc-950/50 p-3 my-2">
                  <p className="text-[11px] uppercase tracking-widest text-zinc-500 mb-2">Metaphors &amp; images</p>
                  <ul className="space-y-2">
                    {open.llm.metaphors.map((m, i) => (
                      <li key={i} className="text-xs text-zinc-300">
                        <span className="text-rose-300 font-semibold">&ldquo;{m.phrase}&rdquo;</span>
                        {m.source && m.target && (
                          <span className="text-zinc-400">
                            {" "}
                            — {m.source} → {m.target}
                          </span>
                        )}
                        {m.note && <span className="text-zinc-500 block mt-0.5">{m.note}</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="flex flex-wrap items-center gap-2 my-2">
                <span className="text-[11px] uppercase tracking-widest text-zinc-500">view:</span>
                {LENSES.map((l) => (
                  <button
                    key={l.key}
                    type="button"
                    onClick={() => setLens(l.key)}
                    className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border transition-colors ${
                      lens === l.key
                        ? "bg-rose-600 border-rose-600 text-white"
                        : "border-zinc-700 text-zinc-400 hover:border-zinc-500"
                    }`}
                  >
                    {l.label}
                  </button>
                ))}
              </div>
              {LENSES.find((l) => l.key === lens)?.hint && (
                <p className="text-[11px] text-zinc-600 mb-2">{LENSES.find((l) => l.key === lens)?.hint}</p>
              )}

              <div className="grid md:grid-cols-[1fr_auto] gap-6">
                <div className="space-y-5 text-sm text-zinc-200">
                  {open.sections.map((s, i) => (
                    <div key={i}>
                      <p className="text-[11px] uppercase tracking-widest text-rose-400/80 font-semibold mb-1">
                        {s.label} <span className="text-zinc-600 normal-case tracking-normal">· {s.words} words</span>
                      </p>
                      {s.lines.map((line, j) => {
                        const lineIdx = line.line_index ?? j;
                        const llmImagery = open.llm?.imagery?.[String(lineIdx)];
                        return (
                        <div
                          key={j}
                          className="flex items-baseline gap-2 rounded px-1 -mx-1"
                          style={lens === "tone" ? { backgroundColor: valenceColor(line.valence, 0.25) } : undefined}
                        >
                          <p className="leading-relaxed flex-1">
                            <HoverableLine
                              line={line}
                              lens={lens}
                              stats={wordStats}
                              maxCount={maxCount}
                              llmImagery={llmImagery}
                              onHover={onHover}
                              onWordClick={onWordClick}
                            />
                            {line.act !== "statement" && (
                              <span
                                className={`ml-2 align-middle text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded ${ACT_STYLES[line.act] || "bg-zinc-700/40 text-zinc-400"}`}
                                title={line.act_source === "llm" ? "Sentence-aware (Gemini)" : "Rule-based"}
                              >
                                {line.act}
                              </span>
                            )}
                          </p>
                          {line.rhyme_letter && (
                            <span
                              className={`shrink-0 w-7 text-center text-[10px] font-mono border rounded ${letterClass(line.rhyme_letter)}`}
                              title={line.rhyme_kind === "slant" ? "slant rhyme (vowels match)" : "perfect rhyme"}
                            >
                              {line.rhyme_letter}
                              {line.rhyme_kind === "slant" ? "~" : ""}
                            </span>
                          )}
                        </div>
                      );})}
                    </div>
                  ))}
                  <p className="text-[11px] text-zinc-600">
                    Rhyme scheme: lines sharing a letter rhyme with each other; ~ marks slant rhymes
                    (vowel sounds match, consonants don&apos;t).
                  </p>
                </div>
                <SimilarityMatrix lines={allLines} />
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      {hover && hoverStat && (
        <div
          className="fixed z-[60] pointer-events-none rounded-lg border border-zinc-700 bg-zinc-950/95 px-3 py-2 text-xs shadow-xl"
          style={{
            left: Math.min(hover.x + 12, typeof window !== "undefined" ? window.innerWidth - 230 : hover.x),
            top: hover.y + 14,
          }}
        >
          <p className="font-bold text-rose-300">{hover.word}</p>
          <p className="text-zinc-300">
            ×{hoverStat.count} in dataset · {hoverStat.songs} song{hoverStat.songs === 1 ? "" : "s"}
          </p>
          {hoverStat.conc !== undefined && (
            <p className="text-zinc-400">
              {hoverStat.conc >= 4 ? "concrete" : hoverStat.conc <= 2.5 ? "abstract" : "in between"} ({hoverStat.conc}/5)
            </p>
          )}
          <p className="text-zinc-500">
            {hoverStat.ratio >= 2
              ? `${hoverStat.ratio >= 100 ? Math.round(hoverStat.ratio) : hoverStat.ratio}× more than everyday English`
              : hoverStat.ratio <= 0.5
                ? "rarer here than in everyday English"
                : "typical English frequency"}
          </p>
          <p className="text-zinc-600 mt-0.5">click for every lyric line</p>
        </div>
      )}
    </div>
  );
}

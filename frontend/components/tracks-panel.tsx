"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { getTrack, type TrackSummary, type TrackDetail, type WordStat } from "@/lib/api";

const WORD_SPLIT = /([A-Za-z][A-Za-z']*)/;

function valenceColor(v: number): string {
  if (v > 0.05) return "bg-amber-400";
  if (v < -0.05) return "bg-indigo-400";
  return "bg-zinc-500";
}

function HoverableLine({
  line,
  stats,
  onHover,
  onWordClick,
}: {
  line: string;
  stats: Record<string, WordStat>;
  onHover: (word: string | null, x: number, y: number) => void;
  onWordClick?: (word: string) => void;
}) {
  const parts = line.split(WORD_SPLIT);
  return (
    <p className="leading-relaxed">
      {parts.map((part, i) => {
        const key = part.toLowerCase().replace(/^'+|'+$/g, "");
        if (i % 2 === 1 && stats[key]) {
          return (
            <span
              key={i}
              className="cursor-pointer rounded-sm hover:bg-rose-500/25 hover:text-rose-200"
              onMouseEnter={(e) => onHover(key, e.clientX, e.clientY)}
              onMouseLeave={() => onHover(null, 0, 0)}
              onClick={() => onWordClick?.(key)}
            >
              {part}
            </span>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </p>
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

  return (
    <div>
      <div className="max-h-[420px] overflow-y-auto rounded-lg border border-zinc-800 divide-y divide-zinc-800/70">
        {tracks.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => openTrack(t)}
            disabled={!t.has_lyrics}
            className="w-full text-left px-3 py-2.5 hover:bg-zinc-800/50 disabled:opacity-40 disabled:cursor-default transition-colors"
          >
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full shrink-0 ${valenceColor(t.valence)}`} />
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
          </button>
        ))}
      </div>
      <p className="text-[11px] text-zinc-600 mt-2">
        Dot = tone (indigo dark, amber bright). Click a track to read its lyrics — hover any word for
        how this writer uses it.
      </p>

      <Dialog open={!!open} onOpenChange={(o) => !o && setOpen(null)}>
        <DialogContent className="bg-zinc-900 border-zinc-800 max-h-[85vh] overflow-y-auto max-w-2xl">
          {open && (
            <>
              <DialogHeader>
                <DialogTitle>
                  {open.title}
                  <span className="text-zinc-500 font-normal"> — {open.artist}{open.release_year ? `, ${open.release_year}` : ""}</span>
                </DialogTitle>
              </DialogHeader>
              <div className="flex flex-wrap gap-1.5 mb-2">
                <MetricChip label="words" value={String(open.metrics.words ?? 0)} />
                <MetricChip label="unique" value={String(open.metrics.unique_words ?? 0)} />
                <MetricChip
                  label="valence"
                  value={`${(open.metrics.valence ?? 0) >= 0 ? "+" : ""}${(open.metrics.valence ?? 0).toFixed(2)}`}
                />
                <MetricChip label="rhyme" value={`${Math.round((open.metrics.rhyme_density ?? 0) * 100)}%`} />
                <MetricChip label="repeated lines" value={`${Math.round((open.metrics.repetition ?? 0) * 100)}%`} />
                {open.chorus_share > 0 && (
                  <MetricChip label="chorus share" value={`${Math.round(open.chorus_share * 100)}%`} />
                )}
              </div>
              {open.summary && (
                <p className="text-xs text-zinc-500 mb-3 font-mono">{open.summary}</p>
              )}
              <div className="space-y-5 text-sm text-zinc-200">
                {open.sections.map((s, i) => (
                  <div key={i}>
                    <p className="text-[11px] uppercase tracking-widest text-rose-400/80 font-semibold mb-1">
                      {s.label} <span className="text-zinc-600 normal-case tracking-normal">· {s.words} words</span>
                    </p>
                    {s.lines.map((line, j) => (
                      <HoverableLine
                        key={j}
                        line={line}
                        stats={wordStats}
                        onHover={onHover}
                        onWordClick={onWordClick}
                      />
                    ))}
                  </div>
                ))}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      {hover && hoverStat && (
        <div
          className="fixed z-[60] pointer-events-none rounded-lg border border-zinc-700 bg-zinc-950/95 px-3 py-2 text-xs shadow-xl"
          style={{
            left: Math.min(hover.x + 12, typeof window !== "undefined" ? window.innerWidth - 220 : hover.x),
            top: hover.y + 14,
          }}
        >
          <p className="font-bold text-rose-300">{hover.word}</p>
          <p className="text-zinc-300">
            ×{hoverStat.count} in dataset · {hoverStat.songs} song{hoverStat.songs === 1 ? "" : "s"}
          </p>
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

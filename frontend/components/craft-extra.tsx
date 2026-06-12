"use client";

import { useState } from "react";
import type { Craft, SectionStats } from "@/lib/api";
import { brightness } from "@/lib/tone";

function Bar({ label, value, max, color, display }: { label: string; value: number; max: number; color: string; display: string }) {
  return (
    <li className="flex items-center gap-3 text-sm">
      <span className="w-36 shrink-0 text-right text-zinc-400">{label}</span>
      <div className="flex-1 h-3 rounded bg-zinc-800 overflow-hidden">
        <div className={`h-full rounded ${color}`} style={{ width: `${Math.min(100, (value / max) * 100)}%` }} />
      </div>
      <span className="w-16 shrink-0 text-xs font-mono text-zinc-300">{display}</span>
    </li>
  );
}

export function SoundProfilePanel({ craft }: { craft: Craft }) {
  const s = craft.sound;
  if (!s || s.syllables_per_line === undefined)
    return <p className="text-zinc-500 text-sm">Run analysis first.</p>;
  const pct = (v?: number) => `${Math.round((v ?? 0) * 100)}%`;
  return (
    <div className="grid md:grid-cols-2 gap-x-8 gap-y-5">
      <div>
        <p className="text-[11px] uppercase tracking-widest text-zinc-500 mb-2">Rhyme &amp; sound devices</p>
        <ul className="space-y-2">
          <Bar label="perfect rhyme" value={s.perfect_rhyme_density ?? 0} max={0.6} color="bg-violet-500" display={pct(s.perfect_rhyme_density)} />
          <Bar label="slant rhyme" value={s.slant_rhyme_density ?? 0} max={0.6} color="bg-violet-400/70" display={pct(s.slant_rhyme_density)} />
          <Bar label="internal rhyme" value={s.internal_rhyme ?? 0} max={0.2} color="bg-fuchsia-500" display={pct(s.internal_rhyme)} />
          <Bar label="alliteration" value={s.alliteration ?? 0} max={0.6} color="bg-sky-500" display={pct(s.alliteration)} />
          <Bar label="assonance" value={s.assonance ?? 0} max={0.6} color="bg-teal-500" display={pct(s.assonance)} />
        </ul>
        <p className="text-[11px] text-zinc-600 mt-2">
          Share of line endings that rhyme (perfect = full sound match, slant = vowels only);
          alliteration = share of lines with repeated starting sounds.
        </p>
      </div>
      <div>
        <p className="text-[11px] uppercase tracking-widest text-zinc-500 mb-2">Phoneme texture</p>
        <ul className="space-y-2">
          <Bar label="soft (l, m, n, r, w)" value={s.soft_ratio ?? 0} max={0.6} color="bg-emerald-500" display={pct(s.soft_ratio)} />
          <Bar label="plosive (p, b, t, k)" value={s.plosive_ratio ?? 0} max={0.6} color="bg-orange-500" display={pct(s.plosive_ratio)} />
          <Bar label="sibilant (s, z, sh)" value={s.sibilant_ratio ?? 0} max={0.6} color="bg-amber-500" display={pct(s.sibilant_ratio)} />
        </ul>
        <p className="text-[11px] text-zinc-600 mt-2">
          The consonant palette: soft sounds feel gentle, plosives punch, sibilants hiss.
        </p>
        <p className="text-sm text-zinc-300 mt-4">
          <span className="text-zinc-500">syllables per line:</span>{" "}
          <span className="font-mono">{(s.syllables_per_line ?? 0).toFixed(1)}</span>
          <span className="text-zinc-500 ml-3">meter consistency:</span>{" "}
          <span className="font-mono">{Math.round((s.syllable_consistency ?? 0) * 100)}%</span>
        </p>
      </div>
    </div>
  );
}

export function DictionPanel({ craft }: { craft: Craft }) {
  const s = craft.sound;
  if (!s || s.concreteness === undefined)
    return <p className="text-zinc-500 text-sm">Run analysis first.</p>;
  const sensory = s.sensory_totals || {};
  const maxSense = Math.max(1, ...Object.values(sensory));
  const conc = s.concreteness ?? 0;
  const pos = Math.max(0, Math.min(100, ((conc - 1) / 4) * 100));
  return (
    <div className="grid md:grid-cols-2 gap-x-8 gap-y-5">
      <div>
        <p className="text-[11px] uppercase tracking-widest text-zinc-500 mb-2">Concrete vs abstract</p>
        <div className="relative h-4 rounded-full bg-gradient-to-r from-violet-500/60 via-zinc-600/50 to-emerald-500/60">
          <div
            className="absolute top-1/2 -translate-y-1/2 w-3 h-6 rounded bg-zinc-100 border border-zinc-400"
            style={{ left: `calc(${pos}% - 6px)` }}
          />
        </div>
        <div className="flex justify-between text-[11px] text-zinc-500 mt-1">
          <span>abstract (ideas)</span>
          <span className="font-mono text-zinc-300">{conc.toFixed(2)} / 5</span>
          <span>concrete (things)</span>
        </div>
        <p className="text-sm text-zinc-300 mt-3">
          <span className="font-mono">{Math.round((s.pct_concrete ?? 0) * 100)}%</span>{" "}
          <span className="text-zinc-500">of content words are concrete,</span>{" "}
          <span className="font-mono">{Math.round((s.pct_abstract ?? 0) * 100)}%</span>{" "}
          <span className="text-zinc-500">abstract.</span>
        </p>
        <p className="text-[11px] text-zinc-600 mt-2">
          Based on the Brysbaert concreteness norms (40k words rated 1–5 by people). Concrete
          writing shows; abstract writing tells.
        </p>
      </div>
      <div>
        <p className="text-[11px] uppercase tracking-widest text-zinc-500 mb-2">Sensory language</p>
        <ul className="space-y-2">
          {(["sight", "sound", "touch", "taste", "smell"] as const).map((k) => (
            <Bar
              key={k}
              label={k}
              value={sensory[k] ?? 0}
              max={maxSense}
              color={{ sight: "bg-amber-500", sound: "bg-sky-500", touch: "bg-rose-500", taste: "bg-emerald-500", smell: "bg-violet-500" }[k]}
              display={String(sensory[k] ?? 0)}
            />
          ))}
        </ul>
        <p className="text-[11px] text-zinc-600 mt-2">
          Mentions of each sense across the dataset — which senses this writer reaches for.
        </p>
      </div>
    </div>
  );
}

const ACT_LABELS: Record<string, string> = {
  statement: "statements",
  question: "questions",
  command: "commands",
  exclamation: "exclamations",
  promise: "promises",
  apology: "apologies",
  plea: "pleas",
  accusation: "accusations",
  confession: "confessions",
};

export function SpeechActsPanel({ craft }: { craft: Craft }) {
  const [openAct, setOpenAct] = useState<string | null>(null);
  const sa = craft.speech_acts;
  if (!sa || !sa.acts?.length) return <p className="text-zinc-500 text-sm">Run analysis first.</p>;
  const interesting = sa.acts.filter((a) => a.act !== "statement");
  const statements = sa.acts.find((a) => a.act === "statement");
  const selected = interesting.find((a) => a.act === openAct);
  return (
    <div>
      <div className="flex flex-wrap gap-2 mb-3">
        {interesting.map((a) => (
          <button
            key={a.act}
            type="button"
            onClick={() => setOpenAct(openAct === a.act ? null : a.act)}
            className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
              openAct === a.act
                ? "bg-rose-600 border-rose-600 text-white"
                : "border-zinc-700 text-zinc-300 hover:border-zinc-500"
            }`}
          >
            {ACT_LABELS[a.act] || a.act} <span className="font-mono text-xs opacity-80">×{a.count}</span>
          </button>
        ))}
      </div>
      {selected ? (
        <ul className="space-y-1.5 max-h-64 overflow-y-auto pr-2">
          {selected.examples.map((e, i) => (
            <li key={i} className="text-sm border-b border-zinc-800/60 pb-1.5">
              <span className="italic text-zinc-200">&ldquo;{e.line}&rdquo;</span>
              <span className="text-zinc-500 text-xs ml-2">{e.title}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-zinc-500 text-sm">
          Click a category to read those lines.
          {statements && ` The rest (${Math.round(statements.share * 100)}% of lines) are plain statements.`}
        </p>
      )}
    </div>
  );
}

function ContrastRow({
  label,
  verse,
  chorus,
  format,
}: {
  label: string;
  verse: number;
  chorus: number;
  format: (v: number) => string;
}) {
  const max = Math.max(verse, chorus, 0.0001);
  return (
    <li className="text-sm">
      <p className="text-zinc-400 mb-1">{label}</p>
      <div className="grid grid-cols-2 gap-2 items-center">
        <div className="flex items-center gap-2">
          <div className="flex-1 h-3 rounded bg-zinc-800 overflow-hidden">
            <div className="h-full bg-sky-500 rounded" style={{ width: `${(verse / max) * 100}%` }} />
          </div>
          <span className="text-xs font-mono w-12 text-zinc-300">{format(verse)}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex-1 h-3 rounded bg-zinc-800 overflow-hidden">
            <div className="h-full bg-rose-500 rounded" style={{ width: `${(chorus / max) * 100}%` }} />
          </div>
          <span className="text-xs font-mono w-12 text-zinc-300">{format(chorus)}</span>
        </div>
      </div>
    </li>
  );
}

export function SectionContrastPanel({ craft }: { craft: Craft }) {
  const c = craft.section_contrast;
  const verse: SectionStats = c?.verse ?? null;
  const chorus: SectionStats = c?.chorus ?? null;
  if (!verse || !chorus)
    return (
      <p className="text-zinc-500 text-sm">
        Not enough labeled choruses detected in this dataset to compare against verses.
      </p>
    );
  return (
    <div>
      <div className="grid grid-cols-2 gap-2 mb-3 text-center text-[11px] uppercase tracking-widest">
        <p className="text-sky-400">verses · {verse.words.toLocaleString()} words</p>
        <p className="text-rose-400">choruses · {chorus.words.toLocaleString()} words</p>
      </div>
      <ul className="space-y-3">
        <ContrastRow label="Brightness" verse={brightness(verse.valence)} chorus={brightness(chorus.valence)} format={(v) => `${Math.round(v)}`} />
        <ContrastRow label="Vocabulary variety (unique words %)" verse={verse.diversity * 100} chorus={chorus.diversity * 100} format={(v) => `${Math.round(v)}%`} />
        <ContrastRow label="Concreteness (1–5)" verse={verse.concreteness} chorus={chorus.concreteness} format={(v) => v.toFixed(1)} />
        <ContrastRow label="Words per line" verse={verse.words_per_line} chorus={chorus.words_per_line} format={(v) => v.toFixed(1)} />
        <ContrastRow label="Syllables per line" verse={verse.syllables_per_line} chorus={chorus.syllables_per_line} format={(v) => v.toFixed(1)} />
      </ul>
      <p className="text-[11px] text-zinc-600 mt-3">
        How the writing changes when the chorus hits — most writers simplify and brighten.
      </p>
    </div>
  );
}

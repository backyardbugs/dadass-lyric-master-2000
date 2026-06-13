"use client";

import type { Topic } from "@/lib/api";

const GRADIENTS = [
  "from-rose-500/20 to-fuchsia-500/10 border-rose-500/30",
  "from-sky-500/20 to-indigo-500/10 border-sky-500/30",
  "from-amber-500/20 to-orange-500/10 border-amber-500/30",
  "from-emerald-500/20 to-teal-500/10 border-emerald-500/30",
  "from-violet-500/20 to-purple-500/10 border-violet-500/30",
  "from-pink-500/20 to-rose-500/10 border-pink-500/30",
];

export function TopicBubbles({ topics, source }: { topics: Topic[]; source?: string }) {
  if (topics.length === 0)
    return <p className="text-zinc-500 text-sm">No themes yet — run analysis on a dataset with a few tracks.</p>;

  const isSemantic = source === "semantic" || source === "gemini";

  return (
    <div>
      {isSemantic && (
        <p className="text-[11px] text-emerald-400/80 mb-3">
          Named themes from narrative analysis — what this writer keeps returning to across the corpus.
        </p>
      )}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {topics.map((topic, i) => (
          <div
            key={topic.id}
            className={`rounded-xl border bg-gradient-to-br p-4 hover:-translate-y-0.5 transition-transform ${GRADIENTS[i % GRADIENTS.length]}`}
          >
            <p className="text-[11px] uppercase tracking-widest text-zinc-400 mb-2">
              {isSemantic ? "theme" : "topic"} #{topic.topic_index + 1}
            </p>
            {isSemantic ? (
              <>
                <p className="text-base font-bold text-zinc-100 mb-1">{topic.label}</p>
                {topic.description && (
                  <p className="text-xs text-zinc-400 mb-2 leading-relaxed">{topic.description}</p>
                )}
              </>
            ) : (
              <div className="flex flex-wrap gap-1.5 mb-3">
                {topic.label.split(" / ").map((word) => (
                  <span key={word} className="px-2 py-0.5 rounded-full bg-zinc-950/60 text-sm font-bold">
                    {word}
                  </span>
                ))}
              </div>
            )}
            {(topic.keywords?.length ?? 0) > 0 && isSemantic && (
              <div className="flex flex-wrap gap-1 mb-3">
                {topic.keywords!.map((word) => (
                  <span key={word} className="px-2 py-0.5 rounded-full bg-zinc-950/50 text-[11px] text-zinc-300">
                    {word}
                  </span>
                ))}
              </div>
            )}
            {topic.top_tracks?.length > 0 && (
              <ul className="space-y-1">
                {topic.top_tracks.map((t, j) => (
                  <li key={j} className="text-xs text-zinc-400 truncate">
                    {!isSemantic && (
                      <span className="text-zinc-600 font-mono mr-1">{Math.round(t.weight * 100)}%</span>
                    )}
                    {t.title}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

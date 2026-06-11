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

export function TopicBubbles({ topics }: { topics: Topic[] }) {
  if (topics.length === 0)
    return <p className="text-zinc-500 text-sm">No topics yet — run Analyze on a dataset with a few tracks.</p>;

  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {topics.map((topic, i) => (
        <div
          key={topic.id}
          className={`rounded-xl border bg-gradient-to-br p-4 hover:-translate-y-0.5 transition-transform ${GRADIENTS[i % GRADIENTS.length]}`}
        >
          <p className="text-[11px] uppercase tracking-widest text-zinc-400 mb-2">topic #{topic.topic_index + 1}</p>
          <div className="flex flex-wrap gap-1.5 mb-3">
            {topic.label.split(" / ").map((word) => (
              <span key={word} className="px-2 py-0.5 rounded-full bg-zinc-950/60 text-sm font-bold">
                {word}
              </span>
            ))}
          </div>
          {topic.top_tracks?.length > 0 && (
            <ul className="space-y-1">
              {topic.top_tracks.map((t, j) => (
                <li key={j} className="text-xs text-zinc-400 truncate">
                  <span className="text-zinc-600 font-mono mr-1">{Math.round(t.weight * 100)}%</span>
                  {t.title}
                </li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  );
}

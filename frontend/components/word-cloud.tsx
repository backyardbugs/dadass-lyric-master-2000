"use client";

type WordItem = { word: string; count: number };

function getSize(count: number, min: number, max: number): number {
  if (max <= min) return 14;
  const p = (count - min) / (max - min);
  return Math.round(12 + p * 24);
}

export function WordCloud({
  words,
  onWordClick,
}: {
  words: WordItem[];
  onWordClick?: (word: string) => void;
}) {
  if (words.length === 0) return <p className="text-zinc-500 text-sm">No words yet. Run analysis first.</p>;
  const counts = words.map((w) => w.count);
  const min = Math.min(...counts);
  const max = Math.max(...counts);
  return (
    <div className="flex flex-wrap gap-2 justify-center items-center p-4 min-h-[200px]">
      {words.slice(0, 80).map((w) => {
        const size = getSize(w.count, min, max);
        return (
          <button
            key={w.word}
            type="button"
            className="hover:bg-rose-500/20 rounded px-1 transition-colors"
            style={{ fontSize: size }}
            onClick={() => onWordClick?.(w.word)}
          >
            {w.word}
          </button>
        );
      })}
    </div>
  );
}

"use client";

import { useState } from "react";
import type { BarcodeTrack } from "@/lib/api";
import { valenceColor } from "@/lib/tone";

export function AlbumBarcode({ tracks }: { tracks: BarcodeTrack[] }) {
  const [hover, setHover] = useState<string | null>(null);
  if (tracks.length === 0) return <p className="text-zinc-500 text-sm">No data. Run fetch first.</p>;

  return (
    <div>
      <div className="space-y-1.5">
        {tracks.map((t) => (
          <div
            key={t.id}
            className="flex items-center gap-3"
            onMouseEnter={() => setHover(t.title)}
            onMouseLeave={() => setHover(null)}
          >
            <span className="w-40 shrink-0 text-right text-xs text-zinc-400 truncate">{t.title}</span>
            <div className="flex-1 flex h-6 rounded-sm overflow-hidden bg-zinc-900">
              {t.values.map((v, i) => (
                <div
                  key={i}
                  className="h-full"
                  style={{ width: `${100 / t.values.length}%`, backgroundColor: valenceColor(v, 1) }}
                  title={`line ${i + 1}`}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
      <p className="text-xs text-zinc-500 mt-2 h-4">
        {hover ? (
          <span className="text-zinc-300">{hover}</span>
        ) : (
          "Each row is a song; each stripe is one line, colored by tone (indigo = dark, amber = bright, grey = neutral)."
        )}
      </p>
    </div>
  );
}

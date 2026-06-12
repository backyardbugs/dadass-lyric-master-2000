"use client";

import { useEffect, useState } from "react";
import { brightness, heat, whiplash, brightnessLabel } from "@/lib/tone";

function polar(cx: number, cy: number, r: number, deg: number) {
  const rad = ((deg - 180) * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function arcPath(cx: number, cy: number, r: number, startDeg: number, endDeg: number) {
  const s = polar(cx, cy, r, startDeg);
  const e = polar(cx, cy, r, endDeg);
  const large = endDeg - startDeg > 180 ? 1 : 0;
  return `M ${s.x.toFixed(2)} ${s.y.toFixed(2)} A ${r} ${r} 0 ${large} 1 ${e.x.toFixed(2)} ${e.y.toFixed(2)}`;
}

export function MoodMeter({
  valence,
  intensity,
  volatility,
}: {
  valence: number;
  intensity: number;
  volatility: number;
}) {
  const b = brightness(valence);
  const [shown, setShown] = useState(50);
  useEffect(() => {
    const t = setTimeout(() => setShown(b), 150);
    return () => clearTimeout(t);
  }, [b]);

  const W = 260;
  const H = 150;
  const CX = W / 2;
  const CY = 130;
  const R = 100;
  const needleDeg = (shown / 100) * 180;
  const tip = polar(CX, CY, R - 18, needleDeg);

  return (
    <div className="flex flex-col items-center">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-[280px]">
        <defs>
          <linearGradient id="tone-arc" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#6366f1" />
            <stop offset="50%" stopColor="#a1a1aa" />
            <stop offset="100%" stopColor="#fbbf24" />
          </linearGradient>
        </defs>
        <path d={arcPath(CX, CY, R, 0, 180)} fill="none" stroke="url(#tone-arc)" strokeWidth={16} strokeLinecap="round" opacity={0.85} />
        {(["dark", "neutral", "bright"] as const).map((t, i) => {
          const p = polar(CX, CY, R + 14, i * 90);
          return (
            <text key={t} x={p.x} y={p.y} fill="#52525b" fontSize={9} textAnchor="middle">
              {t}
            </text>
          );
        })}
        <line
          x1={CX}
          y1={CY}
          x2={tip.x}
          y2={tip.y}
          stroke="#fafafa"
          strokeWidth={3}
          strokeLinecap="round"
          style={{ transition: "all 1.2s cubic-bezier(.3,1.2,.4,1)" }}
        />
        <circle cx={CX} cy={CY} r={6} fill="#fafafa" />
      </svg>
      <p className="text-4xl font-black tracking-tight -mt-2">
        {b}
        <span className="text-base font-medium text-zinc-500"> / 100</span>
      </p>
      <p className="mt-1 text-lg font-bold bg-gradient-to-r from-indigo-400 via-zinc-300 to-amber-400 bg-clip-text text-transparent">
        {brightnessLabel(b)}
      </p>
      <div className="grid grid-cols-2 gap-3 mt-4 w-full max-w-[260px] text-center">
        <div className="rounded-lg border border-zinc-800 p-2">
          <p className="text-lg font-bold">{heat(intensity)}<span className="text-xs text-zinc-600">/100</span></p>
          <p className="text-[11px] text-zinc-500">heat</p>
        </div>
        <div className="rounded-lg border border-zinc-800 p-2">
          <p className="text-lg font-bold">{whiplash(volatility)}<span className="text-xs text-zinc-600">/100</span></p>
          <p className="text-[11px] text-zinc-500">whiplash</p>
        </div>
      </div>
      <div className="text-zinc-500 text-[11px] mt-4 space-y-1.5 max-w-[270px]">
        <p>
          <span className="text-zinc-300 font-semibold">Brightness</span> — does the language read
          positive or negative? 50 is neutral; &ldquo;I love it here&rdquo; pushes up,
          &ldquo;everything is ruined&rdquo; pushes down.
        </p>
        <p>
          <span className="text-zinc-300 font-semibold">Heat</span> — how emotionally charged the
          wording is, in either direction. Plain description scores near 0.
        </p>
        <p>
          <span className="text-zinc-300 font-semibold">Whiplash</span> — how hard the tone swings
          from one line to the next. High = bright and dark lines side by side.
        </p>
        <p className="text-zinc-600">
          Every lyric line is scored by the VADER sentiment model, then averaged per song and
          rescaled to 0–100.
        </p>
      </div>
    </div>
  );
}

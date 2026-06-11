"use client";

import { useEffect, useState } from "react";

const LEVELS: { min: number; label: string }[] = [
  { min: 0.15, label: "Bright" },
  { min: 0.05, label: "Warm" },
  { min: -0.05, label: "Mixed" },
  { min: -0.15, label: "Somber" },
  { min: -1, label: "Dark" },
];

function levelFor(valence: number) {
  return LEVELS.find((l) => valence >= l.min) ?? LEVELS[LEVELS.length - 1];
}

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

/** Valence gauge: -1 (dark) .. +1 (bright). Typical lyric corpora sit within
 * ±0.3, so the dial spans -0.4..0.4 for readability. */
export function MoodMeter({
  valence,
  intensity,
  volatility,
}: {
  valence: number;
  intensity: number;
  volatility: number;
}) {
  const SPAN = 0.4;
  const frac = Math.max(0, Math.min(1, (valence + SPAN) / (2 * SPAN)));
  const level = levelFor(valence);

  const [shown, setShown] = useState(0.5);
  useEffect(() => {
    const t = setTimeout(() => setShown(frac), 150);
    return () => clearTimeout(t);
  }, [frac]);

  const W = 260;
  const H = 150;
  const CX = W / 2;
  const CY = 130;
  const R = 100;
  const needleDeg = shown * 180;
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
        {valence >= 0 ? "+" : ""}
        {valence.toFixed(2)}
      </p>
      <p className="mt-1 text-lg font-bold bg-gradient-to-r from-indigo-400 via-zinc-300 to-amber-400 bg-clip-text text-transparent">
        {level.label}
      </p>
      <div className="grid grid-cols-2 gap-3 mt-4 w-full max-w-[260px] text-center">
        <div className="rounded-lg border border-zinc-800 p-2">
          <p className="text-lg font-bold">{(intensity * 100).toFixed(0)}%</p>
          <p className="text-[11px] text-zinc-500">emotional intensity</p>
        </div>
        <div className="rounded-lg border border-zinc-800 p-2">
          <p className="text-lg font-bold">{(volatility * 100).toFixed(0)}%</p>
          <p className="text-[11px] text-zinc-500">mood volatility</p>
        </div>
      </div>
      <p className="text-zinc-600 text-[11px] text-center mt-3 max-w-[250px]">
        Each line is scored with VADER sentiment (−1 to +1). Valence is the average, intensity
        the average strength, volatility the line-to-line swing.
      </p>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";

/** Blend the three emotions into a 0–100 intensity score. Raw averages live
 * around 0–0.25, so scale up so a typical dataset lands mid-dial. */
export function intensityScore(sadness: number, anger: number, nostalgia: number): number {
  const blended = sadness * 0.55 + anger * 0.2 + nostalgia * 0.25;
  return Math.min(100, Math.round(blended * 450));
}

const LEVELS: { min: number; label: string }[] = [
  { min: 80, label: "Very heavy" },
  { min: 60, label: "Heavy" },
  { min: 40, label: "Moderate" },
  { min: 20, label: "Mild" },
  { min: 0, label: "Light" },
];

export function levelFor(score: number) {
  return LEVELS.find((l) => score >= l.min) ?? LEVELS[LEVELS.length - 1];
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

export function MoodMeter({ sadness, anger, nostalgia }: { sadness: number; anger: number; nostalgia: number }) {
  const score = intensityScore(sadness, anger, nostalgia);
  const level = levelFor(score);
  // Animate the needle sweeping from 0 on mount
  const [shown, setShown] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => setShown(score), 150);
    return () => clearTimeout(t);
  }, [score]);

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
          <linearGradient id="mood-arc" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#fbbf24" />
            <stop offset="45%" stopColor="#f43f5e" />
            <stop offset="100%" stopColor="#a855f7" />
          </linearGradient>
        </defs>
        <path d={arcPath(CX, CY, R, 0, 180)} fill="none" stroke="#27272a" strokeWidth={16} strokeLinecap="round" />
        <path
          d={arcPath(CX, CY, R, 0, Math.max(1, (shown / 100) * 180))}
          fill="none"
          stroke="url(#mood-arc)"
          strokeWidth={16}
          strokeLinecap="round"
          style={{ transition: "all 1.2s cubic-bezier(.3,1.2,.4,1)" }}
        />
        {[0, 25, 50, 75, 100].map((tick) => {
          const p1 = polar(CX, CY, R + 12, (tick / 100) * 180);
          return (
            <text key={tick} x={p1.x} y={p1.y} fill="#52525b" fontSize={9} textAnchor="middle">
              {tick}
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
        {score}
        <span className="text-base font-medium text-zinc-500"> / 100</span>
      </p>
      <p className="mt-1 text-lg font-bold bg-gradient-to-r from-amber-400 via-rose-500 to-purple-500 bg-clip-text text-transparent">
        {level.label}
      </p>
      <p className="text-zinc-500 text-xs text-center mt-1 max-w-[240px]">
        Weighted blend of sadness, anger, and nostalgia across all tracks.
      </p>
      <div className="flex gap-4 mt-4 text-xs text-zinc-400">
        <span><span className="inline-block w-2 h-2 rounded-full bg-rose-500 mr-1" />sad {(sadness * 100).toFixed(0)}%</span>
        <span><span className="inline-block w-2 h-2 rounded-full bg-orange-500 mr-1" />angry {(anger * 100).toFixed(0)}%</span>
        <span><span className="inline-block w-2 h-2 rounded-full bg-indigo-400 mr-1" />nostalgic {(nostalgia * 100).toFixed(0)}%</span>
      </div>
    </div>
  );
}

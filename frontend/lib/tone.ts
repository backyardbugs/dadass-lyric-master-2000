/** Translate raw tone metrics into 0–100 scales with plain names.
 * Raw valence is −1…+1 (typical lyric corpora sit within ±0.4);
 * intensity/volatility are 0…1 (typically under 0.4). */

const clamp = (v: number) => Math.max(0, Math.min(100, Math.round(v)));

/** 0 = darkest, 50 = neutral, 100 = brightest. */
export const brightness = (valence: number) => clamp(50 + valence * 125);

/** How emotionally charged the language is. 0 = plain description. */
export const heat = (intensity: number) => clamp(intensity * 250);

/** How hard the tone swings line to line. */
export const whiplash = (volatility: number) => clamp(volatility * 250);

export function brightnessLabel(score: number): string {
  if (score >= 65) return "Bright";
  if (score >= 55) return "Warm";
  if (score >= 45) return "Mixed";
  if (score >= 35) return "Somber";
  return "Dark";
}

/** Color for a line/word valence: indigo (dark) through zinc to amber (bright). */
export function valenceColor(valence: number, alpha = 0.85): string {
  if (valence > 0.05) return `rgba(251, 191, 36, ${Math.min(1, 0.15 + valence) * alpha})`;
  if (valence < -0.05) return `rgba(99, 102, 241, ${Math.min(1, 0.15 - valence) * alpha})`;
  return `rgba(113, 113, 122, ${0.25 * alpha})`;
}

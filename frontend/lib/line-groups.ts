import type { TrackLine } from "@/lib/api";

export type GroupedLine = { line: TrackLine; count: number };

/** Collapse consecutive identical lines (chorus repeats) into one row with a multiplier. */
export function groupConsecutiveLines(lines: TrackLine[]): GroupedLine[] {
  const out: GroupedLine[] = [];
  for (const line of lines) {
    const norm = line.text.trim().toLowerCase();
    const prev = out[out.length - 1];
    if (prev && prev.line.text.trim().toLowerCase() === norm) {
      prev.count += 1;
    } else {
      out.push({ line, count: 1 });
    }
  }
  return out;
}

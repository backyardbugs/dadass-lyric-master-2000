const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === "string" ? err.detail : JSON.stringify(err));
  }
  return res.json();
}

export type Status = {
  has_data: boolean;
  track_count: number;
  last_analyzed: string | null;
  playlist_name: string | null;
};

export async function getStatus(): Promise<Status> {
  return fetchApi<Status>("/api/status");
}

export async function fetchPlaylist(playlistUrl: string): Promise<{ ok: boolean; message: string; track_count: number; playlist_id?: string }> {
  return fetchApi("/api/fetch", {
    method: "POST",
    body: JSON.stringify({ playlist_url: playlistUrl }),
  });
}

export async function runAnalyze(): Promise<{ ok: boolean; message: string; top_words: { word: string; count: number }[]; run_id: number }> {
  return fetchApi("/api/analyze", { method: "POST" });
}

export async function getTopWords(pos?: string, limit = 100): Promise<{ top_words: { word: string; count: number }[]; run_id: number | null }> {
  const q = pos ? `?pos=${pos}&limit=${limit}` : `?limit=${limit}`;
  return fetchApi(`/api/top-words${q}`);
}

export type HeatmapTrack = { track_index: number; title: string; artist: string; sadness: number; anger: number; nostalgia: number };

export async function getSentimentHeatmap(): Promise<{ tracks: HeatmapTrack[] }> {
  return fetchApi("/api/sentiment/heatmap");
}

export async function getWordContext(word: string): Promise<{ word: string; contexts: { line: string; artist: string; title: string }[] }> {
  return fetchApi(`/api/word-context?word=${encodeURIComponent(word)}`);
}

export async function getTopics(): Promise<{ topics: { id: number; label: string; topic_index: number }[] }> {
  return fetchApi("/api/topics");
}

export async function getSuggestRhymes(word: string): Promise<{ word: string; rhymes: string[] }> {
  return fetchApi(`/api/suggest/rhymes?word=${encodeURIComponent(word)}`);
}

export async function getSuggestThematic(word: string): Promise<{ word: string; thematic: string[] }> {
  return fetchApi(`/api/suggest/thematic?word=${encodeURIComponent(word)}`);
}

export async function getClicheWords(): Promise<{ words: string[] }> {
  return fetchApi("/api/cliche-words");
}

export async function checkCliche(text: string): Promise<{ cliche_words: string[] }> {
  return fetchApi("/api/cliche-check", { method: "POST", body: JSON.stringify({ text }) });
}

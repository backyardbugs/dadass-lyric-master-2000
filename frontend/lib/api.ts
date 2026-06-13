const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://dadass-lyric-master-2000-1.onrender.com";

const ACTIVE_PLAYLIST_KEY = "active_playlist_id";
const SEMANTIC_API_KEY_STORAGE = "semantic_api_key";

let spotifyToken: string | null = null;
let activePlaylistId: string | null = null;
if (typeof window !== "undefined") {
  try {
    const stored = sessionStorage.getItem("spotify_token");
    if (stored) spotifyToken = stored;
    const playlist = sessionStorage.getItem(ACTIVE_PLAYLIST_KEY);
    if (playlist) activePlaylistId = playlist;
  } catch {
    /* ignore */
  }
}

export function setActivePlaylistId(id: string | null) {
  activePlaylistId = id;
  try {
    if (typeof window !== "undefined") {
      if (id) sessionStorage.setItem(ACTIVE_PLAYLIST_KEY, id);
      else sessionStorage.removeItem(ACTIVE_PLAYLIST_KEY);
    }
  } catch {
    /* ignore */
  }
}

export function getActivePlaylistId(): string | null {
  syncActivePlaylistFromStorage();
  return activePlaylistId;
}

function syncActivePlaylistFromStorage() {
  if (typeof window === "undefined") return;
  if (activePlaylistId) return;
  try {
    const stored = sessionStorage.getItem(ACTIVE_PLAYLIST_KEY);
    if (stored) activePlaylistId = stored;
  } catch {
    /* ignore */
  }
}

function withPlaylistId(path: string): string {
  syncActivePlaylistFromStorage();
  if (!activePlaylistId) return path;
  const sep = path.includes("?") ? "&" : "?";
  return `${path}${sep}playlist_id=${encodeURIComponent(activePlaylistId)}`;
}

export function setSpotifyToken(token: string | null) {
  spotifyToken = token;
  try {
    if (typeof window !== "undefined") {
      if (token) sessionStorage.setItem("spotify_token", token);
      else sessionStorage.removeItem("spotify_token");
    }
  } catch {
    /* ignore */
  }
}

/** Sync in-memory token from sessionStorage (e.g. after reload or when chunk loads late). */
function syncTokenFromStorage() {
  if (typeof window === "undefined") return;
  if (spotifyToken) return;
  try {
    const s = sessionStorage.getItem("spotify_token");
    if (s) spotifyToken = s;
  } catch {
    /* ignore */
  }
}

function authHeaders(): Record<string, string> {
  syncTokenFromStorage();
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (spotifyToken) h["Authorization"] = `Bearer ${spotifyToken}`;
  return h;
}

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      ...options,
      credentials: "include",
      headers: { ...authHeaders(), ...options?.headers },
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Network error";
    if (/failed to fetch|load failed|network error/i.test(msg)) {
      throw new Error("Could not reach the server. If this keeps happening, the backend may be starting up (try again in 30 seconds).");
    }
    throw e;
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === "string" ? err.detail : JSON.stringify(err));
  }
  return res.json();
}

export function getSemanticApiKey(): string | null {
  try {
    if (typeof window !== "undefined") {
      return sessionStorage.getItem(SEMANTIC_API_KEY_STORAGE);
    }
  } catch {
    /* ignore */
  }
  return null;
}

export function setSemanticApiKey(key: string | null) {
  try {
    if (typeof window !== "undefined") {
      if (key?.trim()) sessionStorage.setItem(SEMANTIC_API_KEY_STORAGE, key.trim());
      else sessionStorage.removeItem(SEMANTIC_API_KEY_STORAGE);
    }
  } catch {
    /* ignore */
  }
}

export type AnalyzeDatasetEvent = {
  status: string;
  progress?: number;
  phase?: string;
  message?: string;
  playlist_id?: string;
  playlist_name?: string;
  track_count?: number;
  run_id?: number;
  batch?: number;
  batches_total?: number;
  tracks_enriched?: number;
  themes_count?: number;
  skipped?: boolean;
  error?: string;
};

/** Stream POST /api/analyze-dataset (SSE). Calls onEvent for each progress update. */
export async function streamAnalyzeDataset(
  params: {
    spotify_url?: string;
    playlist_id?: string;
    gemini_api_key?: string | null;
  },
  onEvent: (event: AnalyzeDatasetEvent) => void,
  signal?: AbortSignal,
): Promise<AnalyzeDatasetEvent> {
  const body: Record<string, string | null | undefined> = {};
  if (params.spotify_url) body.spotify_url = params.spotify_url;
  if (params.playlist_id) body.playlist_id = params.playlist_id;
  const byok = params.gemini_api_key ?? getSemanticApiKey();
  if (byok) body.gemini_api_key = byok;

  let res: Response;
  try {
    res = await fetch(`${API_BASE}/api/analyze-dataset`, {
      method: "POST",
      credentials: "include",
      headers: authHeaders(),
      body: JSON.stringify(body),
      signal,
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Network error";
    if (/abort/i.test(msg) || (e instanceof Error && e.name === "AbortError")) {
      throw new Error("Analysis cancelled.");
    }
    throw new Error("Could not reach the server. The backend may be starting up — try again in 30 seconds.");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === "string" ? err.detail : JSON.stringify(err));
  }

  if (!res.body) {
    throw new Error("Streaming not supported in this browser.");
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let last: AnalyzeDatasetEvent = { status: "unknown", progress: 0 };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() ?? "";
    for (const chunk of chunks) {
      for (const line of chunk.split("\n")) {
        if (!line.startsWith("data: ")) continue;
        try {
          const parsed = JSON.parse(line.slice(6)) as AnalyzeDatasetEvent;
          last = parsed;
          onEvent(parsed);
        } catch {
          /* ignore malformed SSE */
        }
      }
    }
  }

  if (last.status === "error") {
    throw new Error(last.message || last.error || "Analysis failed.");
  }
  return last;
}

export type Status = {
  has_data: boolean;
  track_count: number;
  last_analyzed: string | null;
  playlist_name: string | null;
  image_url: string | null;
  /** @deprecated API field name — means semantic engine available on server */
  gemini_enabled?: boolean;
  semantic_enabled?: boolean;
  gemini_status?: {
    ok?: boolean;
    status?: string;
    message?: string;
    tracks_enriched?: number;
  } | null;
  semantic_status?: {
    ok?: boolean;
    status?: string;
    message?: string;
    tracks_enriched?: number;
  } | null;
};

export const getSpotifyLoginUrl = () => `${API_BASE}/api/auth/spotify`;

export async function exchangeSpotifyCode(code: string): Promise<{ access_token: string }> {
  const res = await fetch(`${API_BASE}/api/auth/exchange?code=${encodeURIComponent(code)}`, {
    credentials: "include",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === "string" ? err.detail : JSON.stringify(err));
  }
  return res.json();
}

export async function getAuthStatus(): Promise<{ spotify: boolean }> {
  return fetchApi<{ spotify: boolean }>("/api/auth/status");
}

export async function getStatus(): Promise<Status> {
  const s = await fetchApi<Status>(withPlaylistId("/api/status"));
  return {
    ...s,
    semantic_enabled: s.gemini_enabled,
    semantic_status: s.gemini_status,
  };
}

export async function fetchPlaylist(playlistUrl: string): Promise<{ ok: boolean; message: string; track_count: number; playlist_id?: string }> {
  return fetchApi("/api/fetch", {
    method: "POST",
    body: JSON.stringify({ playlist_url: playlistUrl }),
  });
}

const ANALYZE_TIMEOUT_MS = 120000;

export async function runAnalyze(playlistId?: string | null): Promise<{
  ok: boolean;
  message: string;
  top_words: { word: string; count: number }[];
  run_id: number;
  gemini?: { ok?: boolean; status?: string; message?: string; tracks_enriched?: number } | null;
}> {
  const id = playlistId ?? getActivePlaylistId();
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), ANALYZE_TIMEOUT_MS);
  const payload = JSON.stringify({ playlist_id: id ?? null });
  try {
    const res = await fetch(`${API_BASE}/api/analyze`, {
      method: "POST",
      credentials: "include",
      headers: { ...authHeaders(), "Content-Type": "application/json" },
      body: payload,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      const detail = err.detail;
      if (typeof detail === "string") {
        throw new Error(detail);
      }
      if (Array.isArray(detail) && detail[0]?.msg) {
        throw new Error(detail.map((d: { msg?: string }) => d.msg).join("; "));
      }
      throw new Error(JSON.stringify(err));
    }
    return res.json();
  } catch (e) {
    clearTimeout(timeoutId);
    if (e instanceof Error && e.name === "AbortError") {
      throw new Error("Analysis timed out. Narrative analysis can take a few minutes on larger albums — try again or use a smaller dataset.");
    }
    const msg = e instanceof Error ? e.message : "Network error";
    if (/failed to fetch|load failed|network error/i.test(msg)) {
      throw new Error("Analysis request failed—server may have timed out. Try a smaller playlist or try again in a minute.");
    }
    throw e;
  }
}

export async function getTopWords(pos?: string, limit = 100): Promise<{ top_words: { word: string; count: number }[]; run_id: number | null }> {
  const q = pos ? `?pos=${pos}&limit=${limit}` : `?limit=${limit}`;
  return fetchApi(withPlaylistId(`/api/top-words${q}`));
}

export type HeatmapTrack = {
  track_index: number;
  title: string;
  artist: string;
  valence: number;
  intensity: number;
  volatility: number;
  release_year: number | null;
};

export async function getSentimentHeatmap(): Promise<{ tracks: HeatmapTrack[] }> {
  return fetchApi(withPlaylistId("/api/sentiment/heatmap"));
}

export type SpeechAct = {
  act: string;
  count: number;
  share: number;
  examples: { line: string; title: string }[];
};

export type SectionStats = {
  lines: number;
  words: number;
  valence: number;
  diversity: number;
  concreteness: number;
  syllables_per_line: number;
  words_per_line: number;
} | null;

export type SoundProfile = {
  syllables_per_line?: number;
  syllable_consistency?: number;
  perfect_rhyme_density?: number;
  slant_rhyme_density?: number;
  internal_rhyme?: number;
  alliteration?: number;
  assonance?: number;
  plosive_ratio?: number;
  sibilant_ratio?: number;
  soft_ratio?: number;
  concreteness?: number;
  pct_concrete?: number;
  pct_abstract?: number;
  sensory_per_100?: number;
  sensory_totals?: Record<string, number>;
};

export type Craft = {
  has_data: boolean;
  signature_words?: { word: string; count: number; songs: number; ratio: number; score: number }[];
  signature_baseline?: string;
  hooks?: { line: string; count: number; songs: number; example: string }[];
  rhyme_pairs?: { a: string; b: string; count: number }[];
  pov?: { i: number; you: number; we: number; they: number; total: number };
  speech_acts?: { total_lines: number; acts: SpeechAct[] };
  sound?: SoundProfile;
  section_contrast?: { verse: SectionStats; chorus: SectionStats };
};

export async function getCraft(): Promise<Craft> {
  return fetchApi(withPlaylistId("/api/craft"));
}

export type TrackSummary = {
  id: number;
  index: number;
  title: string;
  artist: string;
  release_year: number | null;
  album_image: string | null;
  has_lyrics: boolean;
  words: number;
  unique_words: number;
  valence: number;
  intensity: number;
  volatility: number;
  rhyme_density: number;
  repetition: number;
  structure: string;
  chorus_share: number;
};

export async function getTracks(): Promise<{ tracks: TrackSummary[] }> {
  return fetchApi(withPlaylistId("/api/tracks"));
}

export type TrackLine = {
  text: string;
  valence: number;
  act: string;
  act_source?: "semantic" | "gemini" | "rules" | "pending";
  rhyme_letter: string;
  rhyme_kind: "perfect" | "slant" | null;
  end_word: string;
  line_index?: number;
};

export type TrackMetaphor = {
  phrase: string;
  source: string;
  target: string;
  line: number;
  note: string;
};

export type TrackNarrative = {
  available: boolean;
  summary: string;
  metaphors: TrackMetaphor[];
  imagery: Record<string, Record<string, string>>;
};

/** @deprecated use TrackNarrative — API still returns `gemini` key */
export type TrackGemini = TrackNarrative;

export type TrackSection = { label: string; lines: TrackLine[]; words: number };

export type TrackDetail = {
  id: number;
  title: string;
  artist: string;
  release_year: number | null;
  album_image: string | null;
  metrics: {
    valence?: number;
    intensity?: number;
    volatility?: number;
    words?: number;
    unique_words?: number;
    diversity?: number;
    repetition?: number;
    rhyme_density?: number;
    perfect_rhyme_density?: number;
    slant_rhyme_density?: number;
    internal_rhyme?: number;
    alliteration?: number;
    assonance?: number;
    syllables_per_line?: number;
    concreteness?: number;
    words_per_line?: number;
  };
  sections: TrackSection[];
  summary: string;
  chorus_share: number;
  gemini?: TrackNarrative;
  narrative?: TrackNarrative;
};

export async function getTrack(id: number): Promise<TrackDetail> {
  const t = await fetchApi<TrackDetail>(withPlaylistId(`/api/track/${id}`));
  return { ...t, narrative: t.narrative ?? t.gemini };
}

export type WordStat = { count: number; songs: number; ratio: number; conc?: number };

export async function getWordStats(): Promise<{ words: Record<string, WordStat> }> {
  return fetchApi(withPlaylistId("/api/word-stats"));
}

export type BarcodeTrack = { id: number; title: string; values: number[] };

export async function getBarcode(): Promise<{ tracks: BarcodeTrack[] }> {
  return fetchApi(withPlaylistId("/api/barcode"));
}

export type TrendYear = {
  year: number;
  tracks: number;
  valence: number;
  intensity: number;
  diversity: number;
  words_per_track: number;
  rhyme_density: number;
};

export async function getTrends(): Promise<{ years: TrendYear[] }> {
  return fetchApi(withPlaylistId("/api/trends"));
}

export async function getWordContext(word: string): Promise<{ word: string; contexts: { line: string; artist: string; title: string }[] }> {
  return fetchApi(withPlaylistId(`/api/word-context?word=${encodeURIComponent(word)}`));
}

export type Topic = {
  id: number;
  label: string;
  description?: string;
  keywords?: string[];
  topic_index: number;
  top_tracks: { title: string; artist: string; weight: number }[];
};

export async function getTopics(): Promise<{ topics: Topic[]; source?: "semantic" | "gemini" | "nmf" | "none" }> {
  return fetchApi(withPlaylistId("/api/topics"));
}

export type Superlative = { title: string; artist: string; value: number } | null;

export type Stats = {
  has_data: boolean;
  name?: string | null;
  image_url?: string | null;
  track_count?: number;
  analyzed_count?: number;
  total_words?: number;
  unique_words?: number;
  avg_words_per_track?: number;
  avg_valence?: number;
  avg_intensity?: number;
  avg_volatility?: number;
  avg_rhyme_density?: number;
  avg_repetition?: number;
  superlatives?: {
    darkest: Superlative;
    brightest: Superlative;
    most_volatile: Superlative;
    biggest_vocabulary: Superlative;
    most_repetitive: Superlative;
    densest_rhymes: Superlative;
  };
};

export async function getStats(): Promise<Stats> {
  return fetchApi(withPlaylistId("/api/stats"));
}

export async function getSuggestRhymes(word: string): Promise<{ word: string; rhymes: string[] }> {
  return fetchApi(`/api/suggest/rhymes?word=${encodeURIComponent(word)}`);
}

export async function getSuggestThematic(word: string): Promise<{ word: string; thematic: string[] }> {
  return fetchApi(withPlaylistId(`/api/suggest/thematic?word=${encodeURIComponent(word)}`));
}

export async function getClicheWords(): Promise<{ words: string[] }> {
  return fetchApi("/api/cliche-words");
}

export async function checkCliche(text: string): Promise<{ cliche_words: string[] }> {
  return fetchApi(withPlaylistId("/api/cliche-check"), { method: "POST", body: JSON.stringify({ text }) });
}

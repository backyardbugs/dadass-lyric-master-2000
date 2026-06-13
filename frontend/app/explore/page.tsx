"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { WordCloud } from "@/components/word-cloud";
import { MoodMeter } from "@/components/mood-meter";
import { StatCards } from "@/components/stat-cards";
import { MoodMap } from "@/components/mood-map";
import { MoodFlow } from "@/components/mood-flow";
import { EmotionGrid } from "@/components/emotion-grid";
import { TopicBubbles } from "@/components/topic-bubbles";
import { SignatureWords, Hooks, RhymePairs, PovProfile } from "@/components/craft-panels";
import { SoundProfilePanel, DictionPanel, SpeechActsPanel, SectionContrastPanel } from "@/components/craft-extra";
import { AlbumBarcode } from "@/components/album-barcode";
import { TrendsChart } from "@/components/trends-chart";
import { TracksPanel } from "@/components/tracks-panel";
import {
  getTopWords,
  getSentimentHeatmap,
  getWordContext,
  getStats,
  getTopics,
  getCraft,
  getTrends,
  getTracks,
  getWordStats,
  getBarcode,
  getStatus,
  type Stats,
  type Topic,
  type Craft,
  type TrendYear,
  type HeatmapTrack,
  type TrackSummary,
  type WordStat,
  type BarcodeTrack,
} from "@/lib/api";

export default function ExplorePage() {
  const [topWords, setTopWords] = useState<{ word: string; count: number }[]>([]);
  const [heatmapTracks, setHeatmapTracks] = useState<HeatmapTrack[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [topicsSource, setTopicsSource] = useState<string | undefined>();
  const [craft, setCraft] = useState<Craft | null>(null);
  const [trendYears, setTrendYears] = useState<TrendYear[]>([]);
  const [trackList, setTrackList] = useState<TrackSummary[]>([]);
  const [wordStats, setWordStats] = useState<Record<string, WordStat>>({});
  const [barcode, setBarcode] = useState<BarcodeTrack[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [contexts, setContexts] = useState<{ line: string; artist: string; title: string }[]>([]);
  const [contextLoading, setContextLoading] = useState(false);
  const [geminiPending, setGeminiPending] = useState(false);
  const [geminiPollError, setGeminiPollError] = useState<string | null>(null);

  const GEMINI_POLL_TIMEOUT_MS = 3 * 60 * 1000;

  const loadExploreData = async () => {
    const [wordsRes, heatRes, statsRes, topicsRes, craftRes, trendsRes, tracksRes, wordStatsRes, barcodeRes] =
      await Promise.allSettled([
        getTopWords(undefined, 100),
        getSentimentHeatmap(),
        getStats(),
        getTopics(),
        getCraft(),
        getTrends(),
        getTracks(),
        getWordStats(),
        getBarcode(),
      ]);
    setTopWords(wordsRes.status === "fulfilled" ? wordsRes.value.top_words : []);
    setHeatmapTracks(heatRes.status === "fulfilled" ? heatRes.value.tracks : []);
    setStats(statsRes.status === "fulfilled" && statsRes.value.has_data ? statsRes.value : null);
    setTopics(topicsRes.status === "fulfilled" ? topicsRes.value.topics : []);
    setTopicsSource(topicsRes.status === "fulfilled" ? topicsRes.value.source : undefined);
    setCraft(craftRes.status === "fulfilled" && craftRes.value.has_data ? craftRes.value : null);
    setTrendYears(trendsRes.status === "fulfilled" ? trendsRes.value.years : []);
    setTrackList(tracksRes.status === "fulfilled" ? tracksRes.value.tracks : []);
    setWordStats(wordStatsRes.status === "fulfilled" ? wordStatsRes.value.words : {});
    setBarcode(barcodeRes.status === "fulfilled" ? barcodeRes.value.tracks : []);
  };

  useEffect(() => {
    (async () => {
      setLoading(true);
      await loadExploreData();
      try {
        const st = await getStatus();
        setGeminiPending(st.gemini_status?.status === "running");
      } catch {
        /* ignore */
      }
      setLoading(false);
    })();
  }, []);

  useEffect(() => {
    if (!geminiPending) return;
    const startedAt = Date.now();
    const id = setInterval(async () => {
      if (Date.now() - startedAt > GEMINI_POLL_TIMEOUT_MS) {
        setGeminiPending(false);
        setGeminiPollError(
          "Gemini craft pass is taking longer than expected. Refresh the page to check again, or re-run Analyze."
        );
        return;
      }
      try {
        const st = await getStatus();
        if (st.gemini_status?.status === "running") return;
        setGeminiPending(false);
        setGeminiPollError(null);
        await loadExploreData();
      } catch {
        /* ignore */
      }
    }, 5000);
    return () => clearInterval(id);
  }, [geminiPending]);

  const onWordClick = async (word: string) => {
    setSelectedWord(word);
    setContexts([]);
    setContextLoading(true);
    try {
      const res = await getWordContext(word);
      setContexts(res.contexts);
    } catch {
      setContexts([]);
    } finally {
      setContextLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        <header className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-4">
            {stats?.image_url && (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={stats.image_url}
                alt=""
                className="w-16 h-16 rounded-lg object-cover border border-zinc-800 shadow-lg"
              />
            )}
            <div>
              <h1 className="text-3xl font-black tracking-tight">Explore</h1>
              <p className="text-zinc-500 text-sm">
                {stats?.name ? (
                  <>
                    Dataset: <span className="text-zinc-300 font-semibold">{stats.name}</span>
                  </>
                ) : (
                  "Visualizations of your lyric dataset."
                )}
              </p>
            </div>
          </div>
          <Button asChild variant="outline" size="sm" className="border-zinc-600">
            <Link href="/">Back to dashboard</Link>
          </Button>
        </header>

        {loading ? (
          <p className="text-zinc-500">Loading…</p>
        ) : (
          <>
            {geminiPending && (
              <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">
                Gemini craft pass still running… themes and track details will update automatically (usually under a minute).
              </div>
            )}
            {geminiPollError && (
              <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">
                {geminiPollError}
              </div>
            )}
            <div className="grid lg:grid-cols-5 gap-6">
              <Card className="bg-zinc-900 border-zinc-800 lg:col-span-2">
                <CardHeader>
                  <CardTitle>Overall tone</CardTitle>
                  <CardDescription>How dark or bright the writing reads.</CardDescription>
                </CardHeader>
                <CardContent>
                  {stats ? (
                    <MoodMeter
                      valence={stats.avg_valence ?? 0}
                      intensity={stats.avg_intensity ?? 0}
                      volatility={stats.avg_volatility ?? 0}
                    />
                  ) : (
                    <p className="text-zinc-500 text-sm">Run analysis first.</p>
                  )}
                </CardContent>
              </Card>

              <Card className="bg-zinc-900 border-zinc-800 lg:col-span-3">
                <CardHeader>
                  <CardTitle>Highlights</CardTitle>
                  <CardDescription>Standout tracks and dataset totals.</CardDescription>
                </CardHeader>
                <CardContent>
                  {stats ? <StatCards stats={stats} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
                </CardContent>
              </Card>
            </div>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Tracks &amp; lyrics</CardTitle>
                <CardDescription>
                  Every track with word counts and detected structure. Click one to read the lyrics —
                  hover any word for usage data.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TracksPanel tracks={trackList} wordStats={wordStats} onWordClick={onWordClick} />
              </CardContent>
            </Card>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Word cloud</CardTitle>
                <CardDescription>
                  Filter by part of speech, click a word to see its lyric lines.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <WordCloud words={topWords} onWordClick={onWordClick} />
              </CardContent>
            </Card>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Signature words</CardTitle>
                <CardDescription>
                  The words this writer returns to far more than everyday English does — their fingerprint.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {craft ? <SignatureWords craft={craft} onWordClick={onWordClick} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
              </CardContent>
            </Card>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Sound &amp; rhyme habits</CardTitle>
                <CardDescription>
                  How the lyrics sound: rhyme types, sound devices, and the consonant palette.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {craft ? <SoundProfilePanel craft={craft} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
              </CardContent>
            </Card>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Show vs tell</CardTitle>
                <CardDescription>
                  Concrete imagery vs abstract ideas, and which senses the writing reaches for.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {craft ? <DictionPanel craft={craft} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
              </CardContent>
            </Card>

            <div className="grid lg:grid-cols-2 gap-6">
              <Card className="bg-zinc-900 border-zinc-800">
                <CardHeader>
                  <CardTitle>Hooks &amp; repetition</CardTitle>
                  <CardDescription>The most repeated lines in the dataset.</CardDescription>
                </CardHeader>
                <CardContent>
                  {craft ? <Hooks craft={craft} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
                </CardContent>
              </Card>

              <div className="space-y-6">
                <Card className="bg-zinc-900 border-zinc-800">
                  <CardHeader>
                    <CardTitle>Favorite rhymes</CardTitle>
                    <CardDescription>End-rhyme pairs they reach for most.</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {craft ? <RhymePairs craft={craft} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
                  </CardContent>
                </Card>

                <Card className="bg-zinc-900 border-zinc-800">
                  <CardHeader>
                    <CardTitle>Point of view</CardTitle>
                    <CardDescription>Who the songs speak as, and to.</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {craft ? <PovProfile craft={craft} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
                  </CardContent>
                </Card>
              </div>
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
              <Card className="bg-zinc-900 border-zinc-800">
                <CardHeader>
                  <CardTitle>Speech acts</CardTitle>
                  <CardDescription>
                    What the lines are doing: questions, commands, promises, pleas, accusations…
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {craft ? <SpeechActsPanel craft={craft} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
                </CardContent>
              </Card>

              <Card className="bg-zinc-900 border-zinc-800">
                <CardHeader>
                  <CardTitle>Verse vs chorus</CardTitle>
                  <CardDescription>How the writing changes when the chorus hits.</CardDescription>
                </CardHeader>
                <CardContent>
                  {craft ? <SectionContrastPanel craft={craft} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
                </CardContent>
              </Card>
            </div>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Mood map</CardTitle>
                <CardDescription>
                  Each track plotted by valence (dark ↔ bright) and emotional intensity. Bubble size =
                  mood volatility.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <MoodMap tracks={heatmapTracks} />
              </CardContent>
            </Card>

            <div className="grid lg:grid-cols-2 gap-6">
              <Card className="bg-zinc-900 border-zinc-800">
                <CardHeader>
                  <CardTitle>Emotional arc</CardTitle>
                  <CardDescription>Valence and intensity across the tracklist.</CardDescription>
                </CardHeader>
                <CardContent>
                  <MoodFlow tracks={heatmapTracks} />
                </CardContent>
              </Card>

              <Card className="bg-zinc-900 border-zinc-800">
                <CardHeader>
                  <CardTitle>Tone heatmap</CardTitle>
                  <CardDescription>Valence, intensity, and volatility for every track.</CardDescription>
                </CardHeader>
                <CardContent>
                  <EmotionGrid tracks={heatmapTracks} />
                </CardContent>
              </Card>
            </div>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Album barcode</CardTitle>
                <CardDescription>
                  Every song line by line — the emotional shape of the whole dataset in one image.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <AlbumBarcode tracks={barcode} />
              </CardContent>
            </Card>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Themes</CardTitle>
                <CardDescription>
                  Recurring ideas across the dataset. After Analyze, Gemini names the themes; otherwise
                  TF-IDF + NMF word clusters.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TopicBubbles topics={topics} source={topicsSource} />
              </CardContent>
            </Card>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Over the years</CardTitle>
                <CardDescription>
                  How the writing changed by release year: tone, vocabulary range, rhyme habits.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TrendsChart years={trendYears} />
              </CardContent>
            </Card>
          </>
        )}
      </div>

      <Dialog open={!!selectedWord} onOpenChange={(open) => !open && setSelectedWord(null)}>
        <DialogContent className="bg-zinc-900 border-zinc-800 max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>&ldquo;{selectedWord}&rdquo; in the dataset</DialogTitle>
          </DialogHeader>
          {contextLoading ? (
            <p className="text-zinc-500">Loading…</p>
          ) : contexts.length === 0 ? (
            <p className="text-zinc-500">No contexts found.</p>
          ) : (
            <ul className="space-y-3 text-sm">
              {contexts.map((c, i) => (
                <li key={i} className="border-b border-zinc-800 pb-2">
                  <p className="text-zinc-200 italic">&ldquo;{c.line}&rdquo;</p>
                  <p className="text-zinc-500 mt-1">
                    {c.artist} — {c.title}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

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
import {
  getTopWords,
  getSentimentHeatmap,
  getWordContext,
  getStats,
  getTopics,
  type Stats,
  type Topic,
  type HeatmapTrack,
} from "@/lib/api";

export default function ExplorePage() {
  const [topWords, setTopWords] = useState<{ word: string; count: number }[]>([]);
  const [heatmapTracks, setHeatmapTracks] = useState<HeatmapTrack[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [contexts, setContexts] = useState<{ line: string; artist: string; title: string }[]>([]);
  const [contextLoading, setContextLoading] = useState(false);

  useEffect(() => {
    (async () => {
      setLoading(true);
      const [wordsRes, heatRes, statsRes, topicsRes] = await Promise.allSettled([
        getTopWords(undefined, 100),
        getSentimentHeatmap(),
        getStats(),
        getTopics(),
      ]);
      setTopWords(wordsRes.status === "fulfilled" ? wordsRes.value.top_words : []);
      setHeatmapTracks(heatRes.status === "fulfilled" ? heatRes.value.tracks : []);
      setStats(statsRes.status === "fulfilled" && statsRes.value.has_data ? statsRes.value : null);
      setTopics(topicsRes.status === "fulfilled" ? topicsRes.value.topics : []);
      setLoading(false);
    })();
  }, []);

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
          <Button asChild variant="outline" size="sm" className="border-zinc-600">
            <Link href="/">Back to dashboard</Link>
          </Button>
        </header>

        {loading ? (
          <p className="text-zinc-500">Loading…</p>
        ) : (
          <>
            <div className="grid lg:grid-cols-5 gap-6">
              <Card className="bg-zinc-900 border-zinc-800 lg:col-span-2">
                <CardHeader>
                  <CardTitle>Mood meter</CardTitle>
                  <CardDescription>Overall emotional intensity of this dataset.</CardDescription>
                </CardHeader>
                <CardContent>
                  {stats ? (
                    <MoodMeter
                      sadness={stats.avg_sadness ?? 0}
                      anger={stats.avg_anger ?? 0}
                      nostalgia={stats.avg_nostalgia ?? 0}
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
                <CardTitle>Mood map</CardTitle>
                <CardDescription>
                  Every track plotted by sadness and anger. Bigger bubble = more nostalgia. Hover for details.
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
                  <CardDescription>How each emotion rises and falls across the tracklist.</CardDescription>
                </CardHeader>
                <CardContent>
                  <MoodFlow tracks={heatmapTracks} />
                </CardContent>
              </Card>

              <Card className="bg-zinc-900 border-zinc-800">
                <CardHeader>
                  <CardTitle>Emotion heatmap</CardTitle>
                  <CardDescription>All three emotions for every track.</CardDescription>
                </CardHeader>
                <CardContent>
                  <EmotionGrid tracks={heatmapTracks} />
                </CardContent>
              </Card>
            </div>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Topics</CardTitle>
                <CardDescription>
                  Themes found by the topic model, with the tracks that match each one most strongly.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TopicBubbles topics={topics} />
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

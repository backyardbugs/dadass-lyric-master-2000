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
import { SentimentHeatmap } from "@/components/sentiment-heatmap";
import { getTopWords, getSentimentHeatmap, getWordContext } from "@/lib/api";

export default function ExplorePage() {
  const [topWords, setTopWords] = useState<{ word: string; count: number }[]>([]);
  const [heatmapTracks, setHeatmapTracks] = useState<Awaited<ReturnType<typeof getSentimentHeatmap>>["tracks"]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [contexts, setContexts] = useState<{ line: string; artist: string; title: string }[]>([]);
  const [contextLoading, setContextLoading] = useState(false);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const [wordsRes, heatRes] = await Promise.all([getTopWords(undefined, 100), getSentimentHeatmap()]);
        setTopWords(wordsRes.top_words);
        setHeatmapTracks(heatRes.tracks);
      } catch {
        setTopWords([]);
        setHeatmapTracks([]);
      } finally {
        setLoading(false);
      }
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
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Explore</h1>
          <Button asChild variant="outline" size="sm" className="border-zinc-600">
            <Link href="/">Back to dashboard</Link>
          </Button>
        </header>

        {loading ? (
          <p className="text-zinc-500">Loading…</p>
        ) : (
          <>
            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Word cloud</CardTitle>
                <CardDescription>Click a word to see where it appears in the lyrics.</CardDescription>
              </CardHeader>
              <CardContent>
                <WordCloud words={topWords} onWordClick={onWordClick} />
              </CardContent>
            </Card>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Sadness by track</CardTitle>
                <CardDescription>Playlist order vs. sadness score.</CardDescription>
              </CardHeader>
              <CardContent>
                <SentimentHeatmap tracks={heatmapTracks} />
              </CardContent>
            </Card>
          </>
        )}
      </div>

      <Dialog open={!!selectedWord} onOpenChange={(open) => !open && setSelectedWord(null)}>
        <DialogContent className="bg-zinc-900 border-zinc-800 max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>“{selectedWord}” in the dataset</DialogTitle>
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
                  <p className="text-zinc-500 mt-1">{c.artist} — {c.title}</p>
                </li>
              ))}
            </ul>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

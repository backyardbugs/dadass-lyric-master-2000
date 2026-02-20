"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getSuggestRhymes, getSuggestThematic, checkCliche } from "@/lib/api";

export default function LyricLabPage() {
  const [text, setText] = useState("");
  const [highlightedWords, setHighlightedWords] = useState<string[]>([]);
  const [suggestWord, setSuggestWord] = useState("");
  const [rhymes, setRhymes] = useState<string[]>([]);
  const [thematic, setThematic] = useState<string[]>([]);
  const [suggestLoading, setSuggestLoading] = useState(false);

  useEffect(() => {
    if (!text.trim()) {
      setHighlightedWords([]);
      return;
    }
    checkCliche(text).then((r) => setHighlightedWords(r.cliche_words)).catch(() => setHighlightedWords([]));
  }, [text]);

  const onSuggest = async () => {
    const w = suggestWord.trim().toLowerCase();
    if (!w) return;
    setSuggestLoading(true);
    try {
      const [rRes, tRes] = await Promise.all([getSuggestRhymes(w), getSuggestThematic(w)]);
      setRhymes(rRes.rhymes || []);
      setThematic(tRes.thematic || []);
    } catch {
      setRhymes([]);
      setThematic([]);
    } finally {
      setSuggestLoading(false);
    }
  };

  const insertWord = (word: string) => {
    setText((prev) => prev + (prev.endsWith(" ") || prev.length === 0 ? "" : " ") + word);
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Lyric Lab</h1>
          <Button asChild variant="outline" size="sm" className="border-zinc-600">
            <Link href="/">Back to dashboard</Link>
          </Button>
        </header>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle>Write lyrics</CardTitle>
            <CardDescription>
              Words that appear in more than 50% of the dataset are highlighted. Use suggestions for rhymes and thematic words.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <textarea
              className="w-full min-h-[200px] rounded border border-zinc-700 bg-zinc-800 p-3 text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-rose-500"
              placeholder="Type your lyrics here…"
              value={text}
              onChange={(e) => setText(e.target.value)}
              spellCheck={false}
            />
            {highlightedWords.length > 0 && (
              <p className="text-sm text-amber-400">
                Overused in dataset (highlighted): {highlightedWords.join(", ")}
              </p>
            )}
          </CardContent>
        </Card>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle>Suggestions</CardTitle>
            <CardDescription>Enter a word to get rhymes and thematic alternatives from the dataset.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2 items-center">
              <input
                type="text"
                className="rounded border border-zinc-700 bg-zinc-800 px-3 py-2 text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-rose-500 w-40"
                placeholder="Word"
                value={suggestWord}
                onChange={(e) => setSuggestWord(e.target.value)}
              />
              <Button onClick={onSuggest} disabled={suggestLoading} className="bg-rose-600 hover:bg-rose-700">
                {suggestLoading ? "Loading…" : "Suggest"}
              </Button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium text-zinc-400 mb-2">Rhymes</h3>
                <div className="flex flex-wrap gap-2">
                  {rhymes.length === 0 && !suggestLoading && <span className="text-zinc-500 text-sm">—</span>}
                  {rhymes.map((w) => (
                    <Button key={w} variant="outline" size="sm" className="border-zinc-600" onClick={() => insertWord(w)}>
                      {w}
                    </Button>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-medium text-zinc-400 mb-2">Thematic</h3>
                <div className="flex flex-wrap gap-2">
                  {thematic.length === 0 && !suggestLoading && <span className="text-zinc-500 text-sm">—</span>}
                  {thematic.map((w) => (
                    <Button key={w} variant="outline" size="sm" className="border-zinc-600" onClick={() => insertWord(w)}>
                      {w}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

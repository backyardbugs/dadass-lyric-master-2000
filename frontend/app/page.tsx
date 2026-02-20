"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getStatus, fetchPlaylist, runAnalyze, getAuthStatus, getSpotifyLoginUrl } from "@/lib/api";

export default function DashboardPage() {
  const [playlistUrl, setPlaylistUrl] = useState("");
  const [status, setStatus] = useState<Awaited<ReturnType<typeof getStatus>> | null>(null);
  const [spotifyLoggedIn, setSpotifyLoggedIn] = useState(false);
  const [loading, setLoading] = useState<"fetch" | "analyze" | null>(null);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const loadStatus = async () => {
    try {
      const s = await getStatus();
      setStatus(s);
    } catch {
      setStatus({ has_data: false, track_count: 0, last_analyzed: null, playlist_name: null });
    }
  };

  const loadAuthStatus = async () => {
    try {
      const a = await getAuthStatus();
      setSpotifyLoggedIn(a.spotify);
    } catch {
      setSpotifyLoggedIn(false);
    }
  };

  useEffect(() => {
    loadStatus();
    loadAuthStatus();
    const params = typeof window !== "undefined" ? new URLSearchParams(window.location.search) : null;
    if (params?.get("spotify") === "ok") {
      window.history.replaceState({}, "", window.location.pathname);
      loadAuthStatus();
    }
  }, []);

  const onFetch = async () => {
    if (!playlistUrl.trim()) {
      setMessage({ type: "error", text: "Enter a playlist URL." });
      return;
    }
    setLoading("fetch");
    setMessage(null);
    try {
      await fetchPlaylist(playlistUrl.trim());
      setMessage({ type: "success", text: "Lyrics fetched successfully." });
      await loadStatus();
    } catch (e) {
      const text = e instanceof Error ? e.message : "Fetch failed.";
      setMessage({ type: "error", text });
      if (text.includes("Log in with Spotify")) loadAuthStatus();
    } finally {
      setLoading(null);
    }
  };

  const onAnalyze = async () => {
    setLoading("analyze");
    setMessage(null);
    try {
      await runAnalyze();
      setMessage({ type: "success", text: "Analysis complete." });
      await loadStatus();
    } catch (e) {
      setMessage({ type: "error", text: e instanceof Error ? e.message : "Analysis failed." });
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <div className="max-w-2xl mx-auto space-y-8">
        <header className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">The Emo Almanac</h1>
          <p className="text-zinc-400 mt-1">Lyric analysis & generative tools for Emo / Pop-Punk</p>
        </header>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle>Data pipeline</CardTitle>
            <CardDescription>Paste a Spotify playlist URL, fetch lyrics, then run analysis. Spotify requires you to log in once to read playlists.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-3 items-center">
              {spotifyLoggedIn ? (
                <span className="text-emerald-400 text-sm">Logged in with Spotify</span>
              ) : (
                <Button
                  type="button"
                  variant="outline"
                  className="border-zinc-600"
                  onClick={() => { window.location.href = getSpotifyLoginUrl(); }}
                >
                  Log in with Spotify
                </Button>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="playlist-url">Spotify playlist URL</Label>
              <Input
                id="playlist-url"
                placeholder="https://open.spotify.com/playlist/..."
                value={playlistUrl}
                onChange={(e) => setPlaylistUrl(e.target.value)}
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
            <div className="flex flex-wrap gap-3">
              <Button onClick={onFetch} disabled={loading !== null} className="bg-rose-600 hover:bg-rose-700">
                {loading === "fetch" ? "Fetching…" : "Fetch lyrics"}
              </Button>
              <Button
                onClick={onAnalyze}
                disabled={loading !== null || !status?.has_data}
                variant="outline"
                className="border-zinc-600"
              >
                {loading === "analyze" ? "Analyzing…" : "Analyze"}
              </Button>
            </div>
            {message && (
              <p className={message.type === "success" ? "text-emerald-400 text-sm" : "text-rose-400 text-sm"}>
                {message.text}
              </p>
            )}
            {status && (
              <p className="text-zinc-500 text-sm">
                {status.has_data
                  ? `Fetched ${status.track_count} tracks.${status.last_analyzed ? " Analysis complete." : " Run Analyze to see results."}`
                  : "Run fetch first with a playlist URL."}
              </p>
            )}
          </CardContent>
        </Card>

        {status?.has_data && status?.last_analyzed && (
          <Card className="bg-zinc-900 border-zinc-800">
            <CardHeader>
              <CardTitle>Explore</CardTitle>
              <CardDescription>View visualizations and write in the Lyric Lab.</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-3">
              <Button asChild variant="outline" className="border-zinc-600">
                <Link href="/explore">Word cloud & sentiment heatmap</Link>
              </Button>
              <Button asChild variant="outline" className="border-zinc-600">
                <Link href="/lyric-lab">Lyric Lab</Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

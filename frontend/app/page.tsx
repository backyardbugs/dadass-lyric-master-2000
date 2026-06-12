"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getStatus, fetchPlaylist, runAnalyze, getAuthStatus, getSpotifyLoginUrl, exchangeSpotifyCode, setSpotifyToken } from "@/lib/api";

export default function DashboardPage() {
  const [playlistUrl, setPlaylistUrl] = useState("");
  const [status, setStatus] = useState<Awaited<ReturnType<typeof getStatus>> | null>(null);
  const [spotifyLoggedIn, setSpotifyLoggedIn] = useState(false);
  const [authChecking, setAuthChecking] = useState(true);
  const [loading, setLoading] = useState<"fetch" | "analyze" | null>(null);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const loadStatus = async () => {
    try {
      const s = await getStatus();
      setStatus(s);
    } catch {
      setStatus({ has_data: false, track_count: 0, last_analyzed: null, playlist_name: null, image_url: null });
    }
  };

  const loadAuthStatus = async (): Promise<boolean> => {
    try {
      const a = await getAuthStatus();
      setSpotifyLoggedIn(a.spotify);
      return a.spotify;
    } catch {
      setSpotifyLoggedIn(false);
      return false;
    }
  };

  useEffect(() => {
    loadStatus();
    const params = typeof window !== "undefined" ? new URLSearchParams(window.location.search) : null;
    const spotifyParam = params?.get("spotify") ?? null;

    if (spotifyParam === "ok") {
      setMessage({ type: "success", text: "Connected to Spotify! You can fetch playlists now." });
      const run = async () => {
        // Read from current URL inside callback so we have it after hydration
        const search = typeof window !== "undefined" ? window.location.search : "";
        const urlParams = search ? new URLSearchParams(search) : null;
        const tokenFromQuery = urlParams?.get("token") ?? null;
        const hash = typeof window !== "undefined" ? window.location.hash.slice(1) : "";
        const hashParams = hash ? new URLSearchParams(hash) : null;
        const tokenFromFragment = hashParams?.get("token") ?? null;
        const token = tokenFromQuery || tokenFromFragment;
        const code = urlParams?.get("code") ?? null;

        if (token) {
          setSpotifyToken(token);
          window.history.replaceState({}, "", window.location.pathname);
        } else if (code) {
          try {
            const { access_token } = await exchangeSpotifyCode(code);
            setSpotifyToken(access_token);
            window.history.replaceState({}, "", window.location.pathname);
          } catch {
            setMessage({ type: "error", text: "Could not complete Spotify connection. Try logging in again." });
            window.history.replaceState({}, "", window.location.pathname);
          }
        } else {
          setMessage({ type: "error", text: "Missing token. Try logging in with Spotify again." });
          window.history.replaceState({}, "", window.location.pathname);
        }
        const ok = await loadAuthStatus();
        setAuthChecking(false);
        if (!ok) {
          setTimeout(() => loadAuthStatus(), 3000);
          setTimeout(() => loadAuthStatus(), 10000);
        }
      };
      run();
      return;
    }
    if (spotifyParam === "auth_denied") {
      window.history.replaceState({}, "", window.location.pathname);
      setMessage({ type: "error", text: "Spotify login was cancelled or denied." });
    } else if (spotifyParam === "exchange_failed" || spotifyParam === "no_token") {
      const reason = params?.get("reason") ?? "";
      window.history.replaceState({}, "", window.location.pathname);
      let text = "Spotify connection failed. Try logging in again.";
      if (reason === "env") {
        text = "Server missing Spotify keys. Add SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in Vercel → Settings → Environment Variables.";
      } else if (/redirect|mismatch/i.test(decodeURIComponent(reason))) {
        text = "Redirect URI mismatch. In Spotify Dashboard → Edit Settings → Redirect URIs, add exactly: " + (typeof window !== "undefined" ? window.location.origin + "/api/auth/spotify/callback" : "this app’s callback URL");
      }
      setMessage({ type: "error", text });
    }

    loadAuthStatus().finally(() => setAuthChecking(false));
  }, []);

  const onFetch = async () => {
    if (!playlistUrl.trim()) {
      setMessage({ type: "error", text: "Enter a Spotify playlist, album, or artist URL." });
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
      if (text.includes("Log in with Spotify") || text.includes("401")) {
        setSpotifyToken(null);
        await loadAuthStatus();
      }
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
          <h1 className="text-3xl font-bold tracking-tight">Dad Ass Lyric Analyzer 3000</h1>
          <p className="text-zinc-400 mt-1">Lyric analysis & writing tools for any genre</p>
        </header>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle>Data pipeline</CardTitle>
            <CardDescription>Paste a Spotify playlist, album, or artist URL, fetch lyrics, then run analysis. Spotify requires you to log in once to read playlists; albums and artists work without login.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-3 items-center">
              {authChecking && (
                <span className="text-zinc-400 text-sm">Checking login…</span>
              )}
              {!authChecking && spotifyLoggedIn && (
                <span className="text-emerald-400 text-sm">Logged in with Spotify</span>
              )}
              <Button variant="outline" className="border-zinc-600" asChild>
                <a href={getSpotifyLoginUrl()} rel="noopener noreferrer">
                  {spotifyLoggedIn ? "Reconnect Spotify" : "Log in with Spotify"}
                </a>
              </Button>
              {!authChecking && !spotifyLoggedIn && (
                <span className="text-zinc-500 text-sm">Required to fetch playlists (not albums/artists)</span>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="playlist-url">Spotify playlist, album, or artist URL</Label>
              <Input
                id="playlist-url"
                placeholder="https://open.spotify.com/playlist/… or /album/… or /artist/…"
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
              <div className="flex flex-wrap items-center gap-2">
                <p className={message.type === "success" ? "text-emerald-400 text-sm" : "text-rose-400 text-sm"}>
                  {message.text}
                </p>
                {message.type === "error" && /try again|starting up/i.test(message.text) && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="text-zinc-400 hover:text-zinc-200"
                    onClick={async () => {
                      setMessage(null);
                      setAuthChecking(true);
                      await loadAuthStatus();
                      await loadStatus();
                      setAuthChecking(false);
                    }}
                  >
                    Retry
                  </Button>
                )}
              </div>
            )}
            {status && (
              <p className="text-zinc-500 text-sm">
                {status.has_data
                  ? `Fetched ${status.track_count} tracks${status.playlist_name ? ` from “${status.playlist_name}”` : ""}.${status.last_analyzed ? " Analysis complete." : " Run Analyze to see results."}`
                  : "Run fetch first with a playlist, album, or artist URL."}
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

/**
 * Spotify OAuth callback (runs on frontend domain).
 * Receives code from Spotify, exchanges for token, redirects to app with token.
 * Same-origin redirect ensures the token is not stripped by proxies.
 */
import { NextRequest, NextResponse } from "next/server";

const SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token";

export async function GET(request: NextRequest) {
  const url = new URL(request.url);
  const { searchParams } = url;
  const code = searchParams.get("code");
  const error = searchParams.get("error");
  // Must exactly match the redirect_uri used in the authorize step. Prefer the configured
  // value: behind proxies/port-forwards the Host header (url.origin) can differ from the
  // address Spotify actually redirected to (e.g. localhost vs 127.0.0.1).
  const redirectUri = process.env.SPOTIFY_REDIRECT_URI || `${url.origin}${url.pathname}`;
  const baseAppUrl = url.origin;

  if (error || !code) {
    return NextResponse.redirect(`${baseAppUrl}/?spotify=auth_denied`);
  }

  const clientId = process.env.SPOTIFY_CLIENT_ID ?? process.env.SPOTIPY_CLIENT_ID;
  const clientSecret = process.env.SPOTIFY_CLIENT_SECRET ?? process.env.SPOTIPY_CLIENT_SECRET;
  if (!clientId || !clientSecret) {
    return NextResponse.redirect(`${baseAppUrl}/?spotify=exchange_failed&reason=env`);
  }

  const body = new URLSearchParams({
    grant_type: "authorization_code",
    code,
    redirect_uri: redirectUri,
  });
  const auth = Buffer.from(`${clientId}:${clientSecret}`).toString("base64");

  let accessToken: string;
  try {
    const res = await fetch(SPOTIFY_TOKEN_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Authorization: `Basic ${auth}`,
      },
      body: body.toString(),
    });
    if (!res.ok) {
      const text = await res.text();
      console.error("Spotify token exchange failed:", res.status, text);
      const reason = encodeURIComponent(res.status === 400 ? "redirect_uri or code mismatch" : `Spotify ${res.status}`);
      return NextResponse.redirect(`${baseAppUrl}/?spotify=exchange_failed&reason=${reason}`);
    }
    const data = (await res.json()) as { access_token?: string };
    const token = data.access_token;
    if (!token) {
      return NextResponse.redirect(`${baseAppUrl}/?spotify=no_token`);
    }
    accessToken = token;
  } catch (e) {
    console.error("Spotify token exchange error:", e);
    return NextResponse.redirect(`${baseAppUrl}/?spotify=exchange_failed`);
  }

  const tokenParam = encodeURIComponent(accessToken);
  return NextResponse.redirect(`${baseAppUrl}/?spotify=ok&token=${tokenParam}`);
}

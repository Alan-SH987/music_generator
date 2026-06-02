// Thin API client for the FastAPI backend.

import type {
  Generation,
  GenerateParams,
  Policy,
  Provider,
  Scene,
} from "./types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

async function jsonFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore non-JSON error bodies */
    }
    throw new Error(detail);
  }
  return (await res.json()) as T;
}

export const getScenes = () => jsonFetch<Scene[]>("/api/scenes");
export const getProviders = () => jsonFetch<Provider[]>("/api/providers");
export const getPolicy = () => jsonFetch<Policy>("/api/policy");
export const getHistory = () => jsonFetch<Generation[]>("/api/history");

export const generateMusic = (params: GenerateParams) =>
  jsonFetch<Generation>("/api/generate_music", {
    method: "POST",
    body: JSON.stringify(params),
  });

export const clearHistory = () =>
  jsonFetch<{ deleted: number }>("/api/history", { method: "DELETE" });

export async function deleteGeneration(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/history/${id}`, { method: "DELETE" });
  if (!res.ok && res.status !== 204) {
    throw new Error(`Delete failed: ${res.status} ${res.statusText}`);
  }
}

/** Absolute URL for a track's audio (inline by default, or as a download). */
export function audioUrl(gen: Generation, download = false): string {
  return `${API_BASE}${gen.audio_url}${download ? "?download=true" : ""}`;
}

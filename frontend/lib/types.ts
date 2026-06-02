// Shared types mirroring the backend API contract (app/schemas.py).

export interface Scene {
  key: string;
  label_en: string;
  label_zh: string;
  description: string;
  default_bpm: number;
  default_mood: string;
  default_intensity: number;
  default_no_drums: boolean;
}

export interface Generation {
  id: string;
  scene: string;
  provider: string;
  prompt: string;
  duration: number;
  bpm: number;
  mood: string;
  intensity: number;
  no_drums: boolean;
  seed?: number | null;
  parameters: Record<string, unknown>;
  filename: string;
  audio_format: string;
  license_note: string;
  source_type: string;
  generated_at: string;
  audio_url: string;
}

export interface Provider {
  key: string;
  implemented: boolean;
  description: string;
}

export interface Policy {
  policy: string;
  rules: string[];
  moods: string[];
  default_provider: string;
}

export interface GenerateParams {
  scene: string;
  duration: number;
  bpm: number;
  mood: string;
  intensity: number;
  no_drums: boolean;
  provider?: string;
  seed?: number;
}

export interface Dialog {
  id: number;
  title: string;
  category: string;
  difficulty_level: string;
  description: string | null;
  phrases: Phrase[];
  created_at: string;
  updated_at: string;
}

export interface DialogCreate {
  title: string;
  category: string;
  difficulty_level: string;
  description?: string;
}

export interface Phrase {
  id: number;
  dialog_id: number;
  reference_text: string;
  phonetic_transcription: string | null;
  order: number;
  difficulty: string;
}

export interface PhraseCreate {
  dialog_id: number;
  reference_text: string;
  phonetic_transcription?: string;
  order?: number;
  difficulty?: string;
}

export interface Assessment {
  id: number;
  phrase_id: number;
  phrase_text: string;
  overall_score: number;
  accuracy_score: number;
  prosody_score: number;
  fluency_score: number;
  created_at: string;
}

export interface UserProgress {
  user_id: number;
  total_assessments: number;
  average_overall_score: number;
  average_accuracy: number;
  average_prosody: number;
  average_fluency: number;
  average_completeness: number;
  best_score: number;
  worst_score: number;
  categories_practiced: Record<string, number>;
  improvement_rate: number | null;
}

export interface HealthCheck {
  status: string;
  version: string;
  project: string;
  mock_mode: boolean;
}

export interface User {
  id: number;
  user_id: string;
  display_name: string | null;
  created_at: string;
}

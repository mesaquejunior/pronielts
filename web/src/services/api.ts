import axios from 'axios';
import type { Dialog, DialogCreate, Phrase, PhraseCreate, Assessment, UserProgress, HealthCheck } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health
export const getHealth = () =>
  api.get<HealthCheck>('/health', { baseURL: import.meta.env.VITE_API_URL?.replace('/api/v1', '') || '' });

// Dialogs
export const getDialogs = () =>
  api.get<Dialog[]>('/dialogs');

export const getDialog = (id: number) =>
  api.get<Dialog>(`/dialogs/${id}`);

export const createDialog = (data: DialogCreate) =>
  api.post<Dialog>('/dialogs', data);

export const updateDialog = (id: number, data: Partial<DialogCreate>) =>
  api.put<Dialog>(`/dialogs/${id}`, data);

export const deleteDialog = (id: number) =>
  api.delete(`/dialogs/${id}`);

// Phrases
export const getPhrases = (dialogId?: number) => {
  const params = dialogId ? { dialog_id: dialogId } : {};
  return api.get<Phrase[]>('/phrases', { params });
};

export const getPhrase = (id: number) =>
  api.get<Phrase>(`/phrases/${id}`);

export const createPhrase = (data: PhraseCreate) =>
  api.post<Phrase>('/phrases', data);

export const updatePhrase = (id: number, data: Partial<PhraseCreate>) =>
  api.put<Phrase>(`/phrases/${id}`, data);

export const deletePhrase = (id: number) =>
  api.delete(`/phrases/${id}`);

// Users
export const getUserAssessments = (userId: number, limit = 50, offset = 0) =>
  api.get<Assessment[]>(`/users/${userId}/assessments`, { params: { limit, offset } });

export const getUserProgress = (userId: number) =>
  api.get<UserProgress>(`/users/${userId}/progress`);

export default api;

import { useState, useEffect, useCallback } from 'react';
import type { Dialog, DialogCreate } from '../types';
import * as api from '../services/api';

export function useDialogs() {
  const [dialogs, setDialogs] = useState<Dialog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDialogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getDialogs();
      setDialogs(response.data);
    } catch (err) {
      setError('Failed to fetch dialogs');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDialogs();
  }, [fetchDialogs]);

  const addDialog = async (data: DialogCreate) => {
    const response = await api.createDialog(data);
    setDialogs((prev) => [...prev, response.data]);
    return response.data;
  };

  const editDialog = async (id: number, data: Partial<DialogCreate>) => {
    const response = await api.updateDialog(id, data);
    setDialogs((prev) => prev.map((d) => (d.id === id ? response.data : d)));
    return response.data;
  };

  const removeDialog = async (id: number) => {
    await api.deleteDialog(id);
    setDialogs((prev) => prev.filter((d) => d.id !== id));
  };

  return { dialogs, loading, error, fetchDialogs, addDialog, editDialog, removeDialog };
}

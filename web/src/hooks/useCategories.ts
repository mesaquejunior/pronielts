import { useState, useEffect, useCallback } from 'react';
import type { Category, CategoryCreate } from '../types';
import * as api from '../services/api';

export function useCategories() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCategories = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getCategories();
      setCategories(response.data);
    } catch (err) {
      setError('Failed to fetch categories');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  const addCategory = async (data: CategoryCreate) => {
    const response = await api.createCategory(data);
    setCategories((prev) => [...prev, response.data]);
    return response.data;
  };

  const editCategory = async (id: number, data: Partial<CategoryCreate>) => {
    const response = await api.updateCategory(id, data);
    setCategories((prev) => prev.map((c) => (c.id === id ? response.data : c)));
    return response.data;
  };

  const removeCategory = async (id: number) => {
    await api.deleteCategory(id);
    setCategories((prev) => prev.filter((c) => c.id !== id));
  };

  return { categories, loading, error, fetchCategories, addCategory, editCategory, removeCategory };
}

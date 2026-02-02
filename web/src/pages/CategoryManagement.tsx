import { useState } from 'react';
import { Plus, Edit2, Trash2 } from 'lucide-react';
import { useCategories } from '../hooks/useCategories';
import { CategoryForm } from '../components/categories/CategoryForm';
import type { Category, CategoryCreate } from '../types';

export function CategoryManagement() {
  const { categories, loading, error, addCategory, editCategory, removeCategory } = useCategories();
  const [showForm, setShowForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);

  const handleCreateCategory = async (data: CategoryCreate) => {
    await addCategory(data);
    setShowForm(false);
  };

  const handleEditCategory = async (data: CategoryCreate) => {
    if (editingCategory) {
      await editCategory(editingCategory.id, data);
      setEditingCategory(null);
    }
  };

  const handleDeleteCategory = async (category: Category) => {
    const confirmMessage =
      category.dialog_count > 0
        ? `Are you sure you want to delete "${category.name}"?\n\nWARNING: This will also delete ${category.dialog_count} dialog(s) and all their phrases and assessments. This action cannot be undone.`
        : `Are you sure you want to delete "${category.name}"?`;

    if (confirm(confirmMessage)) {
      await removeCategory(category.id);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-500">Loading categories...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-700 p-4 rounded-lg">
        {error}. Make sure the backend is running.
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Category Management</h1>
          <p className="text-slate-500 mt-1">{categories.length} categories</p>
        </div>
        <button
          onClick={() => {
            setShowForm(true);
            setEditingCategory(null);
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus size={18} />
          New Category
        </button>
      </div>

      {(showForm || editingCategory) && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">
            {editingCategory ? 'Edit Category' : 'Create New Category'}
          </h2>
          <CategoryForm
            category={editingCategory || undefined}
            onSubmit={editingCategory ? handleEditCategory : handleCreateCategory}
            onCancel={() => {
              setShowForm(false);
              setEditingCategory(null);
            }}
          />
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-slate-200">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">Name</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">Description</th>
                <th className="text-center py-3 px-4 text-sm font-medium text-slate-600">Dialogs</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-slate-600">Actions</th>
              </tr>
            </thead>
            <tbody>
              {categories.map((category) => (
                <tr key={category.id} className="border-b border-slate-100 last:border-0">
                  <td className="py-3 px-4">
                    <span className="font-medium text-slate-900">
                      {category.name.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-slate-600">
                    {category.description || <span className="italic text-slate-400">No description</span>}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="inline-flex items-center justify-center min-w-[2rem] px-2 py-0.5 bg-slate-100 text-slate-700 text-sm rounded-full">
                      {category.dialog_count}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => {
                          setEditingCategory(category);
                          setShowForm(false);
                        }}
                        className="p-2 text-slate-400 hover:text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                        title="Edit"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button
                        onClick={() => handleDeleteCategory(category)}
                        className="p-2 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                        title="Delete"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {categories.length === 0 && (
                <tr>
                  <td colSpan={4} className="py-8 text-center text-slate-500">
                    No categories yet. Create one to get started.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

import { useState } from 'react';
import { Plus, Edit2, Trash2, ChevronDown, ChevronRight } from 'lucide-react';
import { useDialogs } from '../hooks/useDialogs';
import { DialogForm } from '../components/dialogs/DialogForm';
import { PhraseForm } from '../components/dialogs/PhraseForm';
import type { Dialog, DialogCreate, PhraseCreate } from '../types';
import * as api from '../services/api';

export function DialogManagement() {
  const { dialogs, loading, error, addDialog, editDialog, removeDialog, fetchDialogs } = useDialogs();
  const [showForm, setShowForm] = useState(false);
  const [editingDialog, setEditingDialog] = useState<Dialog | null>(null);
  const [expandedDialog, setExpandedDialog] = useState<number | null>(null);
  const [addingPhraseTo, setAddingPhraseTo] = useState<number | null>(null);

  const handleCreateDialog = async (data: DialogCreate) => {
    await addDialog(data);
    setShowForm(false);
  };

  const handleEditDialog = async (data: DialogCreate) => {
    if (editingDialog) {
      await editDialog(editingDialog.id, data);
      setEditingDialog(null);
    }
  };

  const handleDeleteDialog = async (id: number) => {
    if (confirm('Are you sure you want to delete this dialog and all its phrases?')) {
      await removeDialog(id);
    }
  };

  const handleAddPhrase = async (data: PhraseCreate) => {
    await api.createPhrase(data);
    setAddingPhraseTo(null);
    fetchDialogs();
  };

  const handleDeletePhrase = async (phraseId: number) => {
    if (confirm('Delete this phrase?')) {
      await api.deletePhrase(phraseId);
      fetchDialogs();
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-500">Loading dialogs...</div>
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
          <h1 className="text-2xl font-bold text-slate-900">Dialog Management</h1>
          <p className="text-slate-500 mt-1">{dialogs.length} dialogs</p>
        </div>
        <button
          onClick={() => { setShowForm(true); setEditingDialog(null); }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus size={18} />
          New Dialog
        </button>
      </div>

      {(showForm || editingDialog) && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">
            {editingDialog ? 'Edit Dialog' : 'Create New Dialog'}
          </h2>
          <DialogForm
            dialog={editingDialog || undefined}
            onSubmit={editingDialog ? handleEditDialog : handleCreateDialog}
            onCancel={() => { setShowForm(false); setEditingDialog(null); }}
          />
        </div>
      )}

      <div className="space-y-3">
        {dialogs.map((dialog) => (
          <div key={dialog.id} className="bg-white rounded-xl shadow-sm border border-slate-200">
            <div className="p-4 flex items-center justify-between">
              <button
                onClick={() => setExpandedDialog(expandedDialog === dialog.id ? null : dialog.id)}
                className="flex items-center gap-3 flex-1 text-left"
              >
                {expandedDialog === dialog.id ? (
                  <ChevronDown size={18} className="text-slate-400" />
                ) : (
                  <ChevronRight size={18} className="text-slate-400" />
                )}
                <div>
                  <h3 className="font-medium text-slate-900">{dialog.title}</h3>
                  <p className="text-sm text-slate-500">
                    {dialog.category.replace('_', ' ')} - {dialog.difficulty_level} - {dialog.phrases?.length || 0} phrases
                  </p>
                </div>
              </button>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => { setEditingDialog(dialog); setShowForm(false); }}
                  className="p-2 text-slate-400 hover:text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                  title="Edit"
                >
                  <Edit2 size={16} />
                </button>
                <button
                  onClick={() => handleDeleteDialog(dialog.id)}
                  className="p-2 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                  title="Delete"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>

            {expandedDialog === dialog.id && (
              <div className="border-t border-slate-100 p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-medium text-slate-700">Phrases</h4>
                  <button
                    onClick={() => setAddingPhraseTo(addingPhraseTo === dialog.id ? null : dialog.id)}
                    className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
                  >
                    <Plus size={14} /> Add Phrase
                  </button>
                </div>

                {addingPhraseTo === dialog.id && (
                  <div className="mb-4">
                    <PhraseForm
                      dialogId={dialog.id}
                      onSubmit={handleAddPhrase}
                      onCancel={() => setAddingPhraseTo(null)}
                    />
                  </div>
                )}

                {dialog.phrases && dialog.phrases.length > 0 ? (
                  <div className="space-y-2">
                    {dialog.phrases.map((phrase, idx) => (
                      <div key={phrase.id} className="flex items-center justify-between py-2 px-3 bg-slate-50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <span className="text-xs text-slate-400 font-mono w-6">{idx + 1}.</span>
                          <div>
                            <p className="text-sm text-slate-900">{phrase.reference_text}</p>
                            {phrase.phonetic_transcription && (
                              <p className="text-xs text-slate-500 italic">{phrase.phonetic_transcription}</p>
                            )}
                          </div>
                        </div>
                        <button
                          onClick={() => handleDeletePhrase(phrase.id)}
                          className="p-1.5 text-slate-400 hover:text-red-600 rounded hover:bg-red-50"
                          title="Delete phrase"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-400 italic">No phrases yet</p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

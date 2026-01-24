import { useState } from 'react';
import type { PhraseCreate } from '../../types';

interface PhraseFormProps {
  dialogId: number;
  onSubmit: (data: PhraseCreate) => Promise<void>;
  onCancel: () => void;
}

export function PhraseForm({ dialogId, onSubmit, onCancel }: PhraseFormProps) {
  const [referenceText, setReferenceText] = useState('');
  const [phoneticTranscription, setPhoneticTranscription] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit({
        dialog_id: dialogId,
        reference_text: referenceText,
        phonetic_transcription: phoneticTranscription || undefined,
      });
      setReferenceText('');
      setPhoneticTranscription('');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3 bg-slate-50 p-4 rounded-lg">
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Reference Text</label>
        <input
          type="text"
          value={referenceText}
          onChange={(e) => setReferenceText(e.target.value)}
          required
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="The phrase to practice..."
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Phonetic Transcription (optional)</label>
        <input
          type="text"
          value={phoneticTranscription}
          onChange={(e) => setPhoneticTranscription(e.target.value)}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          placeholder="IPA transcription..."
        />
      </div>

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={submitting || !referenceText}
          className="px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 disabled:opacity-50"
        >
          {submitting ? 'Adding...' : 'Add Phrase'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-3 py-1.5 bg-slate-200 text-slate-700 text-sm rounded-lg hover:bg-slate-300"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

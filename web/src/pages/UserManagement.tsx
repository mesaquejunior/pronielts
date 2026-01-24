import { useState } from 'react';
import { Search, ChevronDown, ChevronRight } from 'lucide-react';
import * as api from '../services/api';
import type { Assessment, UserProgress } from '../types';

export function UserManagement() {
  const [userId, setUserId] = useState('');
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showAssessments, setShowAssessments] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const id = parseInt(userId);
    if (isNaN(id)) {
      setError('Please enter a valid user ID (number)');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const [assessmentsRes, progressRes] = await Promise.all([
        api.getUserAssessments(id),
        api.getUserProgress(id),
      ]);
      setAssessments(assessmentsRes.data);
      setProgress(progressRes.data);
    } catch {
      setError('User not found or an error occurred');
      setAssessments([]);
      setProgress(null);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">User Management</h1>
        <p className="text-slate-500 mt-1">View user progress and assessment history</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-3 mb-6">
        <div className="flex-1 max-w-xs">
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Enter user ID..."
            className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          <Search size={18} />
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6">{error}</div>
      )}

      {progress && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Progress Overview</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-slate-50 rounded-lg">
                <p className="text-2xl font-bold text-slate-900">{progress.total_assessments}</p>
                <p className="text-xs text-slate-500">Total Assessments</p>
              </div>
              <div className="text-center p-3 bg-slate-50 rounded-lg">
                <p className={`text-2xl font-bold ${getScoreColor(progress.average_overall_score)}`}>
                  {progress.average_overall_score.toFixed(1)}
                </p>
                <p className="text-xs text-slate-500">Avg Overall</p>
              </div>
              <div className="text-center p-3 bg-slate-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">{progress.best_score.toFixed(1)}</p>
                <p className="text-xs text-slate-500">Best Score</p>
              </div>
              <div className="text-center p-3 bg-slate-50 rounded-lg">
                <p className="text-2xl font-bold text-red-600">{progress.worst_score.toFixed(1)}</p>
                <p className="text-xs text-slate-500">Worst Score</p>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
              <div className="text-center">
                <p className={`text-lg font-semibold ${getScoreColor(progress.average_accuracy)}`}>
                  {progress.average_accuracy.toFixed(1)}
                </p>
                <p className="text-xs text-slate-500">Accuracy</p>
              </div>
              <div className="text-center">
                <p className={`text-lg font-semibold ${getScoreColor(progress.average_prosody)}`}>
                  {progress.average_prosody.toFixed(1)}
                </p>
                <p className="text-xs text-slate-500">Prosody</p>
              </div>
              <div className="text-center">
                <p className={`text-lg font-semibold ${getScoreColor(progress.average_fluency)}`}>
                  {progress.average_fluency.toFixed(1)}
                </p>
                <p className="text-xs text-slate-500">Fluency</p>
              </div>
              <div className="text-center">
                <p className={`text-lg font-semibold ${getScoreColor(progress.average_completeness)}`}>
                  {progress.average_completeness.toFixed(1)}
                </p>
                <p className="text-xs text-slate-500">Completeness</p>
              </div>
            </div>

            {Object.keys(progress.categories_practiced).length > 0 && (
              <div className="mt-4 pt-4 border-t border-slate-100">
                <h3 className="text-sm font-medium text-slate-700 mb-2">Categories Practiced</h3>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(progress.categories_practiced).map(([cat, count]) => (
                    <span key={cat} className="px-3 py-1 bg-blue-50 text-blue-700 text-sm rounded-full">
                      {cat.replace('_', ' ')}: {count}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200">
            <button
              onClick={() => setShowAssessments(!showAssessments)}
              className="w-full p-4 flex items-center justify-between text-left"
            >
              <h2 className="text-lg font-semibold text-slate-900">
                Assessment History ({assessments.length})
              </h2>
              {showAssessments ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
            </button>

            {showAssessments && (
              <div className="border-t border-slate-100">
                {assessments.length === 0 ? (
                  <p className="p-4 text-slate-500 text-sm italic">No assessments yet</p>
                ) : (
                  <div className="divide-y divide-slate-100">
                    {assessments.map((a) => (
                      <div key={a.id} className="p-4 flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-slate-900">{a.phrase_text}</p>
                          <p className="text-xs text-slate-500 mt-1">
                            {new Date(a.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex items-center gap-4 text-sm">
                          <span className={`font-semibold ${getScoreColor(a.overall_score)}`}>
                            {a.overall_score.toFixed(1)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {!progress && !loading && !error && (
        <div className="text-center py-12 text-slate-400">
          <Search size={48} className="mx-auto mb-4 opacity-50" />
          <p>Enter a user ID to view their progress and assessments</p>
        </div>
      )}
    </div>
  );
}

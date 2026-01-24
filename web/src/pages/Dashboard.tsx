import { useState, useEffect } from 'react';
import { MessageSquare, BookOpen, Activity, Server } from 'lucide-react';
import { StatsCard } from '../components/dashboard/StatsCard';
import * as api from '../services/api';
import type { Dialog, HealthCheck } from '../types';

export function Dashboard() {
  const [dialogs, setDialogs] = useState<Dialog[]>([]);
  const [health, setHealth] = useState<HealthCheck | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [dialogsRes, healthRes] = await Promise.all([
          api.getDialogs(),
          api.getHealth(),
        ]);
        setDialogs(dialogsRes.data);
        setHealth(healthRes.data);
      } catch (err) {
        console.error('Failed to fetch dashboard data', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const totalPhrases = dialogs.reduce((acc, d) => acc + (d.phrases?.length || 0), 0);
  const categories = [...new Set(dialogs.map((d) => d.category))];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-500">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-slate-500 mt-1">Overview of your PronIELTS platform</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatsCard
          title="Total Dialogs"
          value={dialogs.length}
          icon={MessageSquare}
          color="bg-blue-500"
        />
        <StatsCard
          title="Total Phrases"
          value={totalPhrases}
          icon={BookOpen}
          color="bg-green-500"
        />
        <StatsCard
          title="Categories"
          value={categories.length}
          icon={Activity}
          color="bg-purple-500"
        />
        <StatsCard
          title="API Status"
          value={health?.status === 'healthy' ? 'Online' : 'Offline'}
          icon={Server}
          color={health?.status === 'healthy' ? 'bg-emerald-500' : 'bg-red-500'}
          subtitle={health?.mock_mode ? 'Mock Mode' : 'Production'}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Dialogs by Category</h2>
          <div className="space-y-3">
            {categories.map((cat) => {
              const count = dialogs.filter((d) => d.category === cat).length;
              const pct = Math.round((count / dialogs.length) * 100);
              return (
                <div key={cat}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-700">{cat.replace('_', ' ')}</span>
                    <span className="text-slate-500">{count} dialogs</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Recent Dialogs</h2>
          <div className="space-y-3">
            {dialogs.slice(0, 5).map((dialog) => (
              <div key={dialog.id} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                <div>
                  <p className="text-sm font-medium text-slate-900">{dialog.title}</p>
                  <p className="text-xs text-slate-500">{dialog.category.replace('_', ' ')} - {dialog.difficulty_level}</p>
                </div>
                <span className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded">
                  {dialog.phrases?.length || 0} phrases
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

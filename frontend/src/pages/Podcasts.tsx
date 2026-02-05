import { useEffect, useState } from 'react';
import { Plus, Edit2, FileAudio } from 'lucide-react';
import { getPodcasts, updatePodcast, createPodcast, deletePodcast, Podcast } from '../api';

export default function Podcasts() {
  const [podcasts, setPodcasts] = useState<Podcast[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedPodcast, setSelectedPodcast] = useState<Podcast | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    host: '',
    default_studio_settings: '',
    tasks_time_allowance_days: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPodcasts();
  }, []);

  useEffect(() => {
    if (isModalOpen && selectedPodcast) {
      setFormData({
        name: selectedPodcast.name,
        host: selectedPodcast.host || '',
        default_studio_settings: selectedPodcast.default_studio_settings || '',
        tasks_time_allowance_days: selectedPodcast.tasks_time_allowance_days || '',
      });
    } else if (isModalOpen && !selectedPodcast) {
      setFormData({
        name: '',
        host: '',
        default_studio_settings: '',
        tasks_time_allowance_days: '',
      });
    }
  }, [isModalOpen, selectedPodcast]);

  const loadPodcasts = async () => {
    try {
      const res = await getPodcasts();
      setPodcasts(res.data);
    } catch (err) {
      console.error('Failed to load podcasts:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (selectedPodcast) {
        await updatePodcast(selectedPodcast.id, formData);
      } else {
        await createPodcast(formData);
      }
      loadPodcasts();
      setIsModalOpen(false);
      setSelectedPodcast(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save podcast');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (podcast: Podcast) => {
    if (!confirm(`Delete podcast "${podcast.name}"? This will also delete all its episodes and tasks.`)) return;
    try {
      await deletePodcast(podcast.id);
      loadPodcasts();
      if (selectedPodcast?.id === podcast.id) {
        setIsModalOpen(false);
        setSelectedPodcast(null);
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete podcast');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            Podcasts
          </h2>
          <p className="text-gray-500 mt-1">Manage podcasts and their task time allowances</p>
        </div>
        <button
          onClick={() => {
            setSelectedPodcast(null);
            setIsModalOpen(true);
          }}
          className="inline-flex items-center px-5 py-2.5 border border-transparent rounded-xl shadow-lg shadow-primary-500/30 text-sm font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 transition-all duration-200 hover:shadow-xl hover:shadow-primary-500/40 hover:scale-105"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Podcast
        </button>
      </div>

      <div className="glass-dark rounded-xl shadow-lg border border-gray-200/50 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200/50">
          <thead className="bg-gray-50/80">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Podcast
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Host
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Tasks Time Allowance
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white/50 divide-y divide-gray-200/50">
            {podcasts.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-12 text-center text-gray-500">
                  No podcasts yet. Create one or import from CSV.
                </td>
              </tr>
            ) : (
              podcasts.map((podcast) => (
                <tr key={podcast.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <FileAudio className="h-5 w-5 text-gray-400 mr-2" />
                      <span className="text-sm font-medium text-gray-900">{podcast.name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {podcast.host || '—'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {podcast.tasks_time_allowance_days || '—'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => {
                        setSelectedPodcast(podcast);
                        setIsModalOpen(true);
                      }}
                      className="text-primary-600 hover:text-primary-700 inline-flex items-center px-3 py-1.5 rounded-lg hover:bg-primary-50 transition-all font-medium text-sm"
                    >
                      <Edit2 className="h-4 w-4 mr-1.5" />
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(podcast)}
                      className="ml-2 text-red-600 hover:text-red-700 text-sm"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Edit/Create Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="glass-dark rounded-2xl shadow-2xl max-w-lg w-full mx-4 border border-gray-200/50">
            <div className="flex justify-between items-center p-6 border-b border-gray-200/50">
              <h3 className="text-xl font-bold text-gray-900">
                {selectedPodcast ? 'Edit Podcast' : 'New Podcast'}
              </h3>
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setSelectedPodcast(null);
                }}
                className="text-gray-400 hover:text-gray-600 rounded-lg p-1.5"
              >
                ×
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
                  {error}
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                  placeholder="Podcast name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Host</label>
                <input
                  type="text"
                  value={formData.host}
                  onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                  placeholder="Host name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tasks Time Allowance
                </label>
                <input
                  type="text"
                  value={formData.tasks_time_allowance_days}
                  onChange={(e) => setFormData({ ...formData, tasks_time_allowance_days: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                  placeholder="e.g., 7, 3 days, 1 week"
                />
                <p className="mt-1 text-xs text-gray-500">
                  How long engineers have to complete all tasks for an episode of this podcast.
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Default Studio Settings
                </label>
                <input
                  type="text"
                  value={formData.default_studio_settings}
                  onChange={(e) => setFormData({ ...formData, default_studio_settings: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                  placeholder="e.g., two mics, two cameras"
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setIsModalOpen(false);
                    setSelectedPodcast(null);
                  }}
                  className="px-4 py-2.5 border border-gray-300 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2.5 rounded-xl text-sm font-semibold text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
                >
                  {loading ? 'Saving...' : selectedPodcast ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

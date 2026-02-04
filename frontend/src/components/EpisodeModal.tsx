import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { Episode, Podcast, User, createEpisode, updateEpisode, getPodcasts, getUsers } from '../api';
import { format } from 'date-fns';

interface EpisodeModalProps {
  episode?: Episode | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void;
}

export default function EpisodeModal({ episode, isOpen, onClose, onSave }: EpisodeModalProps) {
  const [podcasts, setPodcasts] = useState<Podcast[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [formData, setFormData] = useState({
    podcast_id: '',
    episode_number: '',
    recording_date: '',
    studio: '',
    guest_names: '',
    status: 'not_started' as Episode['status'],
    episode_notes: '',
    drive_link: '',
    card_name: '',
    recording_engineer_id: '',
    editing_engineer_id: '',
    reels_engineer_id: '',
    reels_notes: '',
    studio_settings_override: '',
    client_approved_editing: 'pending' as 'pending' | 'approved' | 'rejected',
    client_approved_reels: 'pending' as 'pending' | 'approved' | 'rejected',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadData();
      if (episode) {
        // Edit mode - populate form
        setFormData({
          podcast_id: episode.podcast_id,
          episode_number: episode.episode_number || '',
          recording_date: episode.recording_date 
            ? format(new Date(episode.recording_date), "yyyy-MM-dd'T'HH:mm")
            : '',
          studio: episode.studio || '',
          guest_names: episode.guest_names || '',
          status: episode.status,
          episode_notes: episode.episode_notes || '',
          drive_link: episode.drive_link || '',
          card_name: episode.card_name || '',
          recording_engineer_id: episode.recording_engineer_id || '',
          editing_engineer_id: episode.editing_engineer_id || '',
          reels_engineer_id: episode.reels_engineer_id || '',
          reels_notes: episode.reels_notes || '',
          studio_settings_override: episode.studio_settings_override || '',
          client_approved_editing: episode.client_approved_editing || 'pending',
          client_approved_reels: episode.client_approved_reels || 'pending',
        });
      } else {
        // Create mode - reset form
        setFormData({
          podcast_id: '',
          episode_number: '',
          recording_date: '',
          studio: '',
          guest_names: '',
          status: 'not_started',
          episode_notes: '',
          drive_link: '',
          card_name: '',
          recording_engineer_id: '',
          editing_engineer_id: '',
          reels_engineer_id: '',
          reels_notes: '',
          studio_settings_override: '',
          client_approved_editing: 'pending',
          client_approved_reels: 'pending',
        });
      }
      setError(null);
    }
  }, [isOpen, episode]);

  const loadData = async () => {
    try {
      const [podcastsRes, usersRes] = await Promise.all([
        getPodcasts(),
        getUsers(),
      ]);
      setPodcasts(podcastsRes.data);
      setUsers(usersRes.data);
    } catch (err) {
      console.error('Failed to load data:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = {
        ...formData,
        recording_date: formData.recording_date ? new Date(formData.recording_date).toISOString() : undefined,
        recording_engineer_id: formData.recording_engineer_id || undefined,
        editing_engineer_id: formData.editing_engineer_id || undefined,
        reels_engineer_id: formData.reels_engineer_id || undefined,
      };

      if (episode) {
        await updateEpisode(episode.id, data);
      } else {
        await createEpisode(data);
      }
      
      onSave();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save episode');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
      <div className="glass-dark rounded-2xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto border border-gray-200/50 animate-in zoom-in-95 duration-200">
        <div className="flex justify-between items-center p-6 border-b border-gray-200/50 bg-gradient-to-r from-primary-50/50 to-transparent">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            {episode ? 'Edit Episode' : 'New Episode'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 rounded-lg p-1.5 hover:bg-gray-100 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Podcast *
            </label>
            <select
              required
              value={formData.podcast_id}
              onChange={(e) => setFormData({ ...formData, podcast_id: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
            >
              <option value="">Select a podcast</option>
              {podcasts.map(podcast => (
                <option key={podcast.id} value={podcast.id}>{podcast.name}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Episode Number
              </label>
              <input
                type="text"
                value={formData.episode_number}
                onChange={(e) => setFormData({ ...formData, episode_number: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
                placeholder="e.g., 1, 2, S3E1"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value as Episode['status'] })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
              >
                <option value="not_started">Not Started</option>
                <option value="recorded">Recorded</option>
                <option value="in_editing">In Editing</option>
                <option value="sent_to_client">Sent to Client</option>
                <option value="published">Published</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Recording Date
              </label>
              <input
                type="datetime-local"
                value={formData.recording_date}
                onChange={(e) => setFormData({ ...formData, recording_date: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Studio
              </label>
              <input
                type="text"
                value={formData.studio}
                onChange={(e) => setFormData({ ...formData, studio: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
                placeholder="e.g., חשמונאים, גבעון"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Guest Names
            </label>
            <input
              type="text"
              value={formData.guest_names}
              onChange={(e) => setFormData({ ...formData, guest_names: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
              placeholder="Comma-separated names"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Drive Link
            </label>
            <input
              type="url"
              value={formData.drive_link}
              onChange={(e) => setFormData({ ...formData, drive_link: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
              placeholder="https://drive.google.com/..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Card Name
            </label>
            <input
              type="text"
              value={formData.card_name}
              onChange={(e) => setFormData({ ...formData, card_name: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
              placeholder="e.g., roni ve barak, SSDzilla"
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Recording Engineer
              </label>
              <select
                value={formData.recording_engineer_id}
                onChange={(e) => setFormData({ ...formData, recording_engineer_id: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
              >
                <option value="">Unassigned</option>
                {users.map(user => (
                  <option key={user.id} value={user.id}>{user.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Editing Engineer
              </label>
              <select
                value={formData.editing_engineer_id}
                onChange={(e) => setFormData({ ...formData, editing_engineer_id: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
              >
                <option value="">Unassigned</option>
                {users.map(user => (
                  <option key={user.id} value={user.id}>{user.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Reels Engineer
              </label>
              <select
                value={formData.reels_engineer_id}
                onChange={(e) => setFormData({ ...formData, reels_engineer_id: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
              >
                <option value="">Unassigned</option>
                {users.map(user => (
                  <option key={user.id} value={user.id}>{user.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Episode Notes
            </label>
            <textarea
              value={formData.episode_notes}
              onChange={(e) => setFormData({ ...formData, episode_notes: e.target.value })}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
              placeholder="Additional notes about this episode..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Reels Notes
            </label>
            <textarea
              value={formData.reels_notes}
              onChange={(e) => setFormData({ ...formData, reels_notes: e.target.value })}
              rows={2}
              className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
              placeholder="Notes specific to reels content..."
            />
          </div>

          {/* Studio Settings Section */}
          <div className="border-t pt-4">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Studio Settings</h3>
            
            {formData.podcast_id && (
              <div className="mb-3 p-3 bg-gray-50 rounded-md">
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Default Studio Settings (from Podcast)
                </label>
                <p className="text-sm text-gray-700">
                  {podcasts.find(p => p.id === formData.podcast_id)?.default_studio_settings || 'No default settings'}
                </p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Studio Settings Override (for this episode)
              </label>
              <input
                type="text"
                value={formData.studio_settings_override}
                onChange={(e) => setFormData({ ...formData, studio_settings_override: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
                placeholder="e.g., 3 mics (guest episode)"
              />
              <p className="mt-1 text-xs text-gray-500">
                Leave empty to use podcast default. Override for special cases (e.g., guest episodes).
              </p>
            </div>
          </div>

          {/* Client Approvals Section */}
          {episode && (episode.status === 'sent_to_client' || episode.status === 'in_editing') && (
            <div className="border-t pt-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Client Approvals</h3>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-md">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Editing Approval
                    </label>
                    <p className="text-xs text-gray-500 mt-1">
                      Mark when client approves the edited episode
                    </p>
                  </div>
                  <select
                    value={formData.client_approved_editing}
                    onChange={(e) => setFormData({ ...formData, client_approved_editing: e.target.value as 'pending' | 'approved' | 'rejected' })}
                    className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="pending">Pending</option>
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </div>

                <div className="flex items-center justify-between p-3 bg-pink-50 rounded-md">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Reels Approval
                    </label>
                    <p className="text-xs text-gray-500 mt-1">
                      Mark when client approves the reels
                    </p>
                  </div>
                  <select
                    value={formData.client_approved_reels}
                    onChange={(e) => setFormData({ ...formData, client_approved_reels: e.target.value as 'pending' | 'approved' | 'rejected' })}
                    className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="pending">Pending</option>
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200/50">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 border border-gray-300 rounded-xl text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-all duration-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2.5 border border-transparent rounded-xl shadow-lg shadow-primary-500/30 text-sm font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 disabled:opacity-50 transition-all duration-200 hover:shadow-xl hover:shadow-primary-500/40"
            >
              {loading ? 'Saving...' : episode ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

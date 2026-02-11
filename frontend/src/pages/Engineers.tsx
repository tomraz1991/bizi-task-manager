import { useEffect, useState } from 'react';
import { User, Calendar, CheckCircle2, Mic, Edit, Video, Plus } from 'lucide-react';
import { getAllEngineersSummary, getEngineerEpisodes, getEngineerTasks, createUser, Episode } from '../api';
import { format } from 'date-fns';

interface EngineerSummary {
  id: string;
  name: string;
  email?: string;
  role?: string;
  assignments: {
    recording_episodes: number;
    editing_episodes: number;
    reels_episodes: number;
    additional_tasks: number;
    total: number;
  };
}

export default function Engineers() {
  const [engineers, setEngineers] = useState<EngineerSummary[]>([]);
  const [selectedEngineer, setSelectedEngineer] = useState<string | null>(null);
  const [engineerEpisodes, setEngineerEpisodes] = useState<Episode[]>([]);
  const [engineerTasks, setEngineerTasks] = useState<any[]>([]);
  const [selectedRole, setSelectedRole] = useState<string>('all');
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newEngineerName, setNewEngineerName] = useState('');
  const [newEngineerEmail, setNewEngineerEmail] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadEngineers();
  }, []);

  useEffect(() => {
    if (selectedEngineer) {
      loadEngineerData();
    }
  }, [selectedEngineer, selectedRole]);

  const loadEngineers = async () => {
    try {
      const response = await getAllEngineersSummary();
      setEngineers(response.data);
    } catch (error) {
      console.error('Failed to load engineers:', error);
    }
  };

  const loadEngineerData = async () => {
    if (!selectedEngineer) return;
    
    setLoading(true);
    try {
      const [episodesRes, tasksRes] = await Promise.all([
        getEngineerEpisodes(selectedEngineer, { role: selectedRole === 'all' ? undefined : selectedRole }),
        getEngineerTasks(selectedEngineer),
      ]);
      setEngineerEpisodes(episodesRes.data);
      setEngineerTasks(tasksRes.data);
    } catch (error) {
      console.error('Failed to load engineer data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'recording':
        return <Mic className="h-4 w-4" />;
      case 'editing':
        return <Edit className="h-4 w-4" />;
      case 'reels':
        return <Video className="h-4 w-4" />;
      default:
        return <CheckCircle2 className="h-4 w-4" />;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'recording':
        return 'bg-purple-100 text-purple-800';
      case 'editing':
        return 'bg-blue-100 text-blue-800';
      case 'reels':
        return 'bg-pink-100 text-pink-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const statusColors = {
    published: 'bg-green-100 text-green-800',
    in_editing: 'bg-blue-100 text-blue-800',
    recorded: 'bg-yellow-100 text-yellow-800',
    sent_to_client: 'bg-purple-100 text-purple-800',
    not_started: 'bg-gray-100 text-gray-800',
  };

  const selectedEngineerData = engineers.find(e => e.id === selectedEngineer);

  const handleAddEngineer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEngineerName.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await createUser({ name: newEngineerName.trim(), email: newEngineerEmail.trim() || undefined });
      loadEngineers();
      setIsModalOpen(false);
      setNewEngineerName('');
      setNewEngineerEmail('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add engineer');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Engineers & Team</h2>
        <button
          onClick={() => {
            setError(null);
            setNewEngineerName('');
            setNewEngineerEmail('');
            setIsModalOpen(true);
          }}
          className="inline-flex items-center px-5 py-2.5 border border-transparent rounded-xl shadow-lg shadow-primary-500/30 text-sm font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 transition-all duration-200 hover:shadow-xl hover:shadow-primary-500/40 hover:scale-105"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Engineer
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Engineers List */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Team Members</h3>
              {engineers.length === 0 && !isModalOpen && (
                <p className="text-sm text-gray-500 mb-3">No engineers yet. Add one to get started.</p>
              )}
              <div className="space-y-2">
                {engineers.map((engineer) => (
                  <button
                    key={engineer.id}
                    onClick={() => setSelectedEngineer(engineer.id)}
                    className={`w-full text-left p-3 rounded-lg border-2 transition-colors ${
                      selectedEngineer === engineer.id
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <User className="h-5 w-5 text-gray-400 mr-2" />
                        <span className="font-medium text-gray-900">{engineer.name}</span>
                      </div>
                      <span className="text-sm text-gray-500">{engineer.assignments.total}</span>
                    </div>
                    <div className="mt-2 flex space-x-2 text-xs text-gray-500">
                      <span>R: {engineer.assignments.recording_episodes}</span>
                      <span>E: {engineer.assignments.editing_episodes}</span>
                      <span>Reels: {engineer.assignments.reels_episodes}</span>
                      {engineer.assignments.additional_tasks > 0 && (
                        <span>Tasks: {engineer.assignments.additional_tasks}</span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Engineer Details */}
        <div className="lg:col-span-2">
          {selectedEngineer ? (
            <div className="space-y-6">
              {/* Engineer Header */}
              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">{selectedEngineerData?.name}</h3>
                    {selectedEngineerData?.email && (
                      <p className="text-sm text-gray-500">{selectedEngineerData.email}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-primary-600">
                      {selectedEngineerData?.assignments.total || 0}
                    </div>
                    <div className="text-sm text-gray-500">Total Assignments</div>
                  </div>
                </div>

                {/* Role Filter */}
                <div className="flex space-x-2 mb-4">
                  <button
                    onClick={() => setSelectedRole('all')}
                    className={`px-3 py-1 rounded-md text-sm font-medium ${
                      selectedRole === 'all'
                        ? 'bg-primary-100 text-primary-800'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    All Roles
                  </button>
                  <button
                    onClick={() => setSelectedRole('recording')}
                    className={`px-3 py-1 rounded-md text-sm font-medium ${
                      selectedRole === 'recording'
                        ? 'bg-purple-100 text-purple-800'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Recording ({selectedEngineerData?.assignments.recording_episodes || 0})
                  </button>
                  <button
                    onClick={() => setSelectedRole('editing')}
                    className={`px-3 py-1 rounded-md text-sm font-medium ${
                      selectedRole === 'editing'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Editing ({selectedEngineerData?.assignments.editing_episodes || 0})
                  </button>
                  <button
                    onClick={() => setSelectedRole('reels')}
                    className={`px-3 py-1 rounded-md text-sm font-medium ${
                      selectedRole === 'reels'
                        ? 'bg-pink-100 text-pink-800'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Reels ({selectedEngineerData?.assignments.reels_episodes || 0})
                  </button>
                </div>
              </div>

              {/* Upcoming Recordings */}
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                    <Calendar className="h-5 w-5 text-primary-500 mr-2" />
                    Upcoming Recordings
                  </h4>
                  {loading ? (
                    <p className="text-sm text-gray-500">Loading...</p>
                  ) : engineerEpisodes.filter(e => e.recording_date && new Date(e.recording_date) > new Date()).length === 0 ? (
                    <p className="text-sm text-gray-500">No upcoming recordings</p>
                  ) : (
                    <div className="space-y-3">
                      {engineerEpisodes
                        .filter(e => e.recording_date && new Date(e.recording_date) > new Date())
                        .slice(0, 5)
                        .map((episode) => {
                          const roles = [];
                          if (episode.recording_engineer_id === selectedEngineer) roles.push('recording');
                          if (episode.editing_engineer_id === selectedEngineer) roles.push('editing');
                          if (episode.reels_engineer_id === selectedEngineer) roles.push('reels');
                          
                          return (
                            <div key={episode.id} className="border-l-4 border-primary-500 pl-4 py-2">
                              <div className="flex items-center justify-between">
                                <div>
                                  <p className="text-sm font-medium text-gray-900">
                                    {episode.podcast?.name || 'Unknown'} - Episode {episode.episode_number || 'N/A'}
                                  </p>
                                  {episode.recording_date && (
                                    <p className="text-sm text-gray-500">
                                      {format(new Date(episode.recording_date), 'MMM d, yyyy HH:mm')}
                                    </p>
                                  )}
                                </div>
                                <div className="flex space-x-1">
                                  {roles.map(role => (
                                    <span key={role} className={`px-2 py-1 text-xs font-semibold rounded-full ${getRoleColor(role)}`}>
                                      {getRoleIcon(role)}
                                    </span>
                                  ))}
                                </div>
                              </div>
                              {episode.studio && (
                                <p className="text-xs text-gray-400 mt-1">Studio: {episode.studio}</p>
                              )}
                            </div>
                          );
                        })}
                    </div>
                  )}
                </div>
              </div>

              {/* Episodes & Tasks */}
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h4 className="text-lg font-medium text-gray-900 mb-4">All Assignments</h4>
                  {loading ? (
                    <p className="text-sm text-gray-500">Loading...</p>
                  ) : engineerEpisodes.length === 0 && engineerTasks.length === 0 ? (
                    <p className="text-sm text-gray-500">No assignments found</p>
                  ) : (
                    <div className="space-y-3">
                      {/* Episode Assignments */}
                      {engineerEpisodes.map((episode) => {
                        const roles = [];
                        if (episode.recording_engineer_id === selectedEngineer) roles.push('recording');
                        if (episode.editing_engineer_id === selectedEngineer) roles.push('editing');
                        if (episode.reels_engineer_id === selectedEngineer) roles.push('reels');
                        
                        if (selectedRole !== 'all' && !roles.includes(selectedRole)) return null;
                        
                        return (
                          <div key={episode.id} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <p className="text-sm font-medium text-gray-900">
                                  {episode.podcast?.name || 'Unknown'} - Episode {episode.episode_number || 'N/A'}
                                </p>
                                <div className="flex items-center space-x-2 mt-1">
                                  {roles.map(role => (
                                    <span key={role} className={`px-2 py-1 text-xs font-semibold rounded-full ${getRoleColor(role)} flex items-center space-x-1`}>
                                      {getRoleIcon(role)}
                                      <span>{role}</span>
                                    </span>
                                  ))}
                                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                                    statusColors[episode.status] || statusColors.not_started
                                  }`}>
                                    {episode.status.replace('_', ' ')}
                                  </span>
                                </div>
                                {episode.recording_date && (
                                  <p className="text-xs text-gray-500 mt-1">
                                    {format(new Date(episode.recording_date), 'MMM d, yyyy')}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                      
                      {/* Additional Tasks */}
                      {engineerTasks
                        .filter(t => t.type === 'task')
                        .map((task) => (
                          <div key={task.id} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <p className="text-sm font-medium text-gray-900">
                                  {task.episode?.podcast || 'Unknown'} - Episode {task.episode?.episode_number || 'N/A'}
                                </p>
                                <div className="flex items-center space-x-2 mt-1">
                                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getRoleColor(task.task_type)}`}>
                                    {task.task_type}
                                  </span>
                                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                                    task.status === 'done' ? 'bg-green-100 text-green-800' :
                                    task.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                                    task.status === 'sent_to_client' ? 'bg-amber-100 text-amber-800' :
                                    'bg-gray-100 text-gray-800'
                                  }`}>
                                    {task.status.replace('_', ' ')}
                                  </span>
                                </div>
                                {task.due_date && (
                                  <p className="text-xs text-gray-500 mt-1">
                                    Due: {format(new Date(task.due_date), 'MMM d, yyyy')}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white shadow rounded-lg p-12 text-center">
              <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Select an engineer to view their assignments</p>
            </div>
          )}
        </div>
      </div>

      {/* New Engineer Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="glass-dark rounded-2xl shadow-2xl max-w-md w-full mx-4 border border-gray-200/50">
            <div className="flex justify-between items-center p-6 border-b border-gray-200/50">
              <h3 className="text-xl font-bold text-gray-900">Add Engineer</h3>
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setError(null);
                }}
                className="text-gray-400 hover:text-gray-600 rounded-lg p-1.5"
              >
                ×
              </button>
            </div>
            <form onSubmit={handleAddEngineer} className="p-6 space-y-4">
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
                  value={newEngineerName}
                  onChange={(e) => setNewEngineerName(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                  placeholder="Engineer name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={newEngineerEmail}
                  onChange={(e) => setNewEngineerEmail(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                  placeholder="email@example.com"
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setIsModalOpen(false);
                    setError(null);
                  }}
                  className="px-4 py-2.5 border border-gray-300 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving || !newEngineerName.trim()}
                  className="px-4 py-2.5 rounded-xl text-sm font-semibold text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
                >
                  {saving ? 'Adding...' : 'Add Engineer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

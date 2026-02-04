import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Clock, AlertCircle, CheckCircle2, FileAudio, TrendingUp } from 'lucide-react';
import { useNotifications } from '../contexts/NotificationContext';
import { getEpisodes, getTasks, getUpcomingRecordings, Episode } from '../api';
import { format, formatDistanceToNow } from 'date-fns';
import CSVImport from '../components/CSVImport';
import { DEFAULT_NOTIFICATION_DAYS, MS_PER_DAY } from '../constants';

export default function Dashboard() {
  const { notifications } = useNotifications();
  const [stats, setStats] = useState({
    totalEpisodes: 0,
    inProgress: 0,
    published: 0,
    dueTasks: 0,
  });
  const [recentEpisodes, setRecentEpisodes] = useState<Episode[]>([]);
  const [upcomingRecordings, setUpcomingRecordings] = useState<Episode[]>([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [episodesRes, tasksRes, upcomingRes] = await Promise.all([
          getEpisodes(),
          getTasks({ status: 'not_started' }),
          getUpcomingRecordings(DEFAULT_NOTIFICATION_DAYS),
        ]);

        const episodes = episodesRes.data;
        const tasks = tasksRes.data;
        
        // Calculate due tasks with proper null checking
        const now = Date.now();
        const daysFromNow = now + DEFAULT_NOTIFICATION_DAYS * MS_PER_DAY;
        const dueTasksCount = tasks.filter(t => {
          if (!t.due_date) return false;
          const dueDate = new Date(t.due_date).getTime();
          return dueDate <= daysFromNow;
        }).length;
        
        setStats({
          totalEpisodes: episodes.length,
          inProgress: episodes.filter(e => e.status === 'in_editing').length,
          published: episodes.filter(e => e.status === 'published').length,
          dueTasks: dueTasksCount,
        });

        setRecentEpisodes(episodes.slice(0, 5));
        setUpcomingRecordings(upcomingRes.data.slice(0, 5));
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      }
    };

    loadData();
  }, []);

  const urgentNotifications = notifications.filter(n => n.priority === 'urgent').slice(0, 5);

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            Dashboard
          </h2>
          <p className="text-gray-500 mt-1">Overview of your podcast production pipeline</p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="glass-dark overflow-hidden rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-200/50 group">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600 mb-1">Total Episodes</p>
                <p className="text-3xl font-bold text-gray-900">{stats.totalEpisodes}</p>
              </div>
              <div className="p-3 rounded-xl bg-gradient-to-br from-primary-100 to-primary-50 group-hover:scale-110 transition-transform duration-300">
                <FileAudio className="h-6 w-6 text-primary-600" />
              </div>
            </div>
          </div>
        </div>

        <div className="glass-dark overflow-hidden rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-200/50 group">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600 mb-1">In Progress</p>
                <p className="text-3xl font-bold text-gray-900">{stats.inProgress}</p>
              </div>
              <div className="p-3 rounded-xl bg-gradient-to-br from-blue-100 to-blue-50 group-hover:scale-110 transition-transform duration-300">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>
        </div>

        <div className="glass-dark overflow-hidden rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-200/50 group">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600 mb-1">Published</p>
                <p className="text-3xl font-bold text-gray-900">{stats.published}</p>
              </div>
              <div className="p-3 rounded-xl bg-gradient-to-br from-green-100 to-green-50 group-hover:scale-110 transition-transform duration-300">
                <CheckCircle2 className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>
        </div>

        <div className="glass-dark overflow-hidden rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-200/50 group">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600 mb-1">Due Tasks</p>
                <p className="text-3xl font-bold text-gray-900">{stats.dueTasks}</p>
              </div>
              <div className="p-3 rounded-xl bg-gradient-to-br from-orange-100 to-orange-50 group-hover:scale-110 transition-transform duration-300">
                <Clock className="h-6 w-6 text-orange-600" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* CSV Import */}
        <div className="lg:col-span-1">
          <CSVImport onImportComplete={async () => {
            // Reload data instead of full page reload
            const [episodesRes, tasksRes, upcomingRes] = await Promise.all([
              getEpisodes(),
              getTasks({ status: 'not_started' }),
              getUpcomingRecordings(DEFAULT_NOTIFICATION_DAYS),
            ]);
            const episodes = episodesRes.data;
            const tasks = tasksRes.data;
            const now = Date.now();
            const daysFromNow = now + DEFAULT_NOTIFICATION_DAYS * MS_PER_DAY;
            const dueTasksCount = tasks.filter(t => {
              if (!t.due_date) return false;
              const dueDate = new Date(t.due_date).getTime();
              return dueDate <= daysFromNow;
            }).length;
            setStats({
              totalEpisodes: episodes.length,
              inProgress: episodes.filter(e => e.status === 'in_editing').length,
              published: episodes.filter(e => e.status === 'published').length,
              dueTasks: dueTasksCount,
            });
            setRecentEpisodes(episodes.slice(0, 5));
            setUpcomingRecordings(upcomingRes.data.slice(0, 5));
          }} />
        </div>

        {/* Urgent Notifications */}
        {urgentNotifications.length > 0 ? (
          <div className="glass-dark rounded-xl shadow-lg border border-red-200/50 lg:col-span-2 overflow-hidden">
            <div className="px-6 py-5 bg-gradient-to-r from-red-50 to-transparent border-b border-red-100/50">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
                Urgent Notifications
              </h3>
            </div>
            <div className="px-6 py-5">
              <div className="space-y-4">
                {urgentNotifications.map((notif) => (
                  <div key={notif.id} className="border-l-4 border-red-500 pl-4 py-3 rounded-r-lg bg-gradient-to-r from-red-50/50 to-transparent hover:from-red-50 transition-colors">
                    <p className="text-sm font-semibold text-gray-900">{notif.title}</p>
                    <p className="text-sm text-gray-600 mt-1">{notif.message}</p>
                    <p className="text-xs text-gray-400 mt-2">
                      {formatDistanceToNow(new Date(notif.due_date), { addSuffix: true })}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="lg:col-span-2 glass-dark rounded-xl shadow-lg border border-gray-200/50 overflow-hidden">
            <div className="px-6 py-5 bg-gradient-to-r from-primary-50 to-transparent border-b border-primary-100/50">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Calendar className="h-5 w-5 text-primary-500 mr-2" />
                Upcoming Recordings
              </h3>
            </div>
            <div className="px-6 py-5">
              {upcomingRecordings.length === 0 ? (
                <p className="text-sm text-gray-500">No upcoming recordings</p>
              ) : (
                <div className="space-y-4">
                  {upcomingRecordings.map((episode) => (
                    <div key={episode.id} className="border-l-4 border-primary-500 pl-4 py-3 rounded-r-lg bg-gradient-to-r from-primary-50/50 to-transparent hover:from-primary-50 transition-colors">
                      <p className="text-sm font-semibold text-gray-900">
                        {episode.podcast?.name || 'Unknown'} - Episode {episode.episode_number || 'N/A'}
                      </p>
                      {episode.recording_date && (
                        <p className="text-sm text-gray-600 mt-1">
                          {format(new Date(episode.recording_date), 'MMM d, yyyy HH:mm')}
                        </p>
                      )}
                      {episode.studio && (
                        <p className="text-xs text-gray-400 mt-1">Studio: {episode.studio}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Upcoming Recordings - Show separately if urgent notifications exist */}
      {urgentNotifications.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Calendar className="h-5 w-5 text-primary-500 mr-2" />
              Upcoming Recordings
            </h3>
            {upcomingRecordings.length === 0 ? (
              <p className="text-sm text-gray-500">No upcoming recordings</p>
            ) : (
              <div className="space-y-3">
                {upcomingRecordings.map((episode) => (
                  <div key={episode.id} className="border-l-4 border-primary-500 pl-4 py-2">
                    <p className="text-sm font-medium text-gray-900">
                      {episode.podcast?.name || 'Unknown'} - Episode {episode.episode_number || 'N/A'}
                    </p>
                    {episode.recording_date && (
                      <p className="text-sm text-gray-500">
                        {format(new Date(episode.recording_date), 'MMM d, yyyy HH:mm')}
                      </p>
                    )}
                    {episode.studio && (
                      <p className="text-xs text-gray-400">Studio: {episode.studio}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recent Episodes */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">Recent Episodes</h3>
            <Link to="/episodes" className="text-sm text-primary-600 hover:text-primary-700">
              View all →
            </Link>
          </div>
          {recentEpisodes.length === 0 ? (
            <p className="text-sm text-gray-500">No episodes yet</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Podcast
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Episode
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {recentEpisodes.map((episode) => (
                    <tr key={episode.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {episode.podcast?.name || 'Unknown'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {episode.episode_number || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          episode.status === 'published' ? 'bg-green-100 text-green-800' :
                          episode.status === 'in_editing' ? 'bg-blue-100 text-blue-800' :
                          episode.status === 'recorded' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {episode.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {episode.recording_date ? format(new Date(episode.recording_date), 'MMM d, yyyy') : 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

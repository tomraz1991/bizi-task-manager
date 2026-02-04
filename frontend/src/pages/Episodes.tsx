import { useEffect, useState } from 'react';
import { Plus, Search, Edit2, ChevronLeft, ChevronRight, Calendar } from 'lucide-react';
import { getEpisodes, getEpisodesCount, getPodcasts, Episode, Podcast } from '../api';
import { format } from 'date-fns';
import EpisodeModal from '../components/EpisodeModal';

const ITEMS_PER_PAGE = 50;

export default function Episodes() {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [podcasts, setPodcasts] = useState<Podcast[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPodcast, setSelectedPodcast] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedEpisode, setSelectedEpisode] = useState<Episode | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, [currentPage, selectedPodcast, selectedStatus, dateFrom, dateTo]);

  const loadData = async () => {
    setLoading(true);
    try {
      const skip = (currentPage - 1) * ITEMS_PER_PAGE;
      const params: any = {
        skip,
        limit: ITEMS_PER_PAGE,
      };

      if (selectedPodcast !== 'all') {
        params.podcast_id = selectedPodcast;
      }
      if (selectedStatus !== 'all') {
        params.status = selectedStatus;
      }
      if (dateFrom) {
        params.date_from = new Date(dateFrom).toISOString();
      }
      if (dateTo) {
        // Set to end of day
        const toDate = new Date(dateTo);
        toDate.setHours(23, 59, 59, 999);
        params.date_to = toDate.toISOString();
      }

      const [episodesRes, countRes, podcastsRes] = await Promise.all([
        getEpisodes(params),
        getEpisodesCount({
          podcast_id: selectedPodcast !== 'all' ? selectedPodcast : undefined,
          status: selectedStatus !== 'all' ? selectedStatus : undefined,
          date_from: dateFrom ? new Date(dateFrom).toISOString() : undefined,
          date_to: dateTo ? new Date(dateTo).toISOString() : undefined,
        }),
        getPodcasts(),
      ]);

      setEpisodes(episodesRes.data);
      setTotalCount(countRes.data.total);
      setPodcasts(podcastsRes.data);
    } catch (error) {
      console.error('Failed to load episodes:', error);
    } finally {
      setLoading(false);
    }
  };

  // Client-side search filtering (since we're using server-side pagination)
  const filteredEpisodes = episodes.filter(ep => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      ep.podcast?.name.toLowerCase().includes(search) ||
      ep.episode_number?.toLowerCase().includes(search) ||
      ep.guest_names?.toLowerCase().includes(search)
    );
  });

  const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE);

  const handleFilterChange = () => {
    setCurrentPage(1); // Reset to first page when filters change
  };

  const statusColors = {
    published: 'bg-gradient-to-r from-green-100 to-green-50 text-green-800 border border-green-200',
    in_editing: 'bg-gradient-to-r from-blue-100 to-blue-50 text-blue-800 border border-blue-200',
    recorded: 'bg-gradient-to-r from-yellow-100 to-yellow-50 text-yellow-800 border border-yellow-200',
    sent_to_client: 'bg-gradient-to-r from-purple-100 to-purple-50 text-purple-800 border border-purple-200',
    not_started: 'bg-gradient-to-r from-gray-100 to-gray-50 text-gray-800 border border-gray-200',
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            Episodes
          </h2>
          <p className="text-gray-500 mt-1">Manage your podcast episodes</p>
        </div>
        <button 
          onClick={() => {
            setSelectedEpisode(null);
            setIsModalOpen(true);
          }}
          className="inline-flex items-center px-5 py-2.5 border border-transparent rounded-xl shadow-lg shadow-primary-500/30 text-sm font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 transition-all duration-200 hover:shadow-xl hover:shadow-primary-500/40 hover:scale-105"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Episode
        </button>
      </div>

      {/* Filters */}
      <div className="glass-dark p-5 rounded-xl shadow-lg border border-gray-200/50">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search episodes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
            />
          </div>
          <select
            value={selectedPodcast}
            onChange={(e) => {
              setSelectedPodcast(e.target.value);
              handleFilterChange();
            }}
            className="border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
          >
            <option value="all">All Podcasts</option>
            {podcasts.map(podcast => (
              <option key={podcast.id} value={podcast.id}>{podcast.name}</option>
            ))}
          </select>
          <select
            value={selectedStatus}
            onChange={(e) => {
              setSelectedStatus(e.target.value);
              handleFilterChange();
            }}
            className="border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
          >
            <option value="all">All Statuses</option>
            <option value="not_started">Not Started</option>
            <option value="recorded">Recorded</option>
            <option value="in_editing">In Editing</option>
            <option value="sent_to_client">Sent to Client</option>
            <option value="published">Published</option>
          </select>
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="date"
              placeholder="From date"
              value={dateFrom}
              onChange={(e) => {
                setDateFrom(e.target.value);
                handleFilterChange();
              }}
              className="pl-10 w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
            />
          </div>
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="date"
              placeholder="To date"
              value={dateTo}
              onChange={(e) => {
                setDateTo(e.target.value);
                handleFilterChange();
              }}
              className="pl-10 w-full border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
            />
          </div>
        </div>
      </div>

      {/* Episodes Table */}
      <div className="glass-dark rounded-xl shadow-lg border border-gray-200/50 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200/50">
            <thead className="bg-gradient-to-r from-gray-50 to-gray-50/50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Podcast
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Episode
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Recording Date
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Studio
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Guests
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Engineers
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white/50 divide-y divide-gray-200/50">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-gray-500">
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                      <span className="ml-3">Loading episodes...</span>
                    </div>
                  </td>
                </tr>
              ) : filteredEpisodes.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-gray-500">
                    No episodes found
                  </td>
                </tr>
              ) : (
                filteredEpisodes.map((episode) => (
                  <tr key={episode.id} className="hover:bg-gray-50/50 transition-colors duration-150">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {episode.podcast?.name || 'Unknown'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {episode.episode_number || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {episode.recording_date ? format(new Date(episode.recording_date), 'MMM d, yyyy') : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {episode.studio || 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {episode.guest_names || 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      <div className="space-y-1">
                        {episode.recording_engineer && (
                          <div className="text-xs">
                            <span className="font-medium text-purple-700">Recording:</span> {episode.recording_engineer.name}
                          </div>
                        )}
                        {episode.editing_engineer && (
                          <div className="text-xs">
                            <span className="font-medium text-blue-700">Editing:</span> {episode.editing_engineer.name}
                          </div>
                        )}
                        {episode.reels_engineer && (
                          <div className="text-xs">
                            <span className="font-medium text-pink-700">Reels:</span> {episode.reels_engineer.name}
                          </div>
                        )}
                        {!episode.recording_engineer && !episode.editing_engineer && !episode.reels_engineer && (
                          <span className="text-xs text-gray-400">Unassigned</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        statusColors[episode.status] || statusColors.not_started
                      }`}>
                        {episode.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => {
                          setSelectedEpisode(episode);
                          setIsModalOpen(true);
                        }}
                        className="text-primary-600 hover:text-primary-700 inline-flex items-center px-3 py-1.5 rounded-lg hover:bg-primary-50 transition-all duration-200 font-medium"
                      >
                        <Edit2 className="h-4 w-4 mr-1.5" />
                        Edit
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        {totalPages > 1 && (
          <div className="glass-dark px-6 py-4 flex items-center justify-between border-t border-gray-200/50 rounded-b-xl">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-semibold rounded-lg text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-semibold rounded-lg text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                Next
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-600">
                  Showing <span className="font-semibold text-gray-900">{(currentPage - 1) * ITEMS_PER_PAGE + 1}</span> to{' '}
                  <span className="font-semibold text-gray-900">
                    {Math.min(currentPage * ITEMS_PER_PAGE, totalCount)}
                  </span>{' '}
                  of <span className="font-semibold text-gray-900">{totalCount}</span> episodes
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-xl shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                    className="relative inline-flex items-center px-3 py-2 rounded-l-xl border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    <ChevronLeft className="h-5 w-5" />
                  </button>
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (currentPage <= 3) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = currentPage - 2 + i;
                    }
                    return (
                      <button
                        key={pageNum}
                        onClick={() => setCurrentPage(pageNum)}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-semibold transition-all ${
                          currentPage === pageNum
                            ? 'z-10 bg-gradient-to-r from-primary-500 to-primary-600 border-primary-500 text-white shadow-lg shadow-primary-500/30'
                            : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                  <button
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={currentPage === totalPages}
                    className="relative inline-flex items-center px-3 py-2 rounded-r-xl border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    <ChevronRight className="h-5 w-5" />
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>

      <EpisodeModal
        episode={selectedEpisode}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedEpisode(null);
        }}
        onSave={async () => {
          // Reload episodes with current filters
          await loadData();
        }}
      />
    </div>
  );
}

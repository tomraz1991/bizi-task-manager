import axios from 'axios';

// Get API base URL from environment variable or use default.
// Ensure it ends with /api so paths like /import/csv become /api/import/csv.
const raw = import.meta.env.VITE_API_BASE_URL || '/api';
const API_BASE_URL = raw.endsWith('/api') ? raw : raw.replace(/\/?$/, '') + '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Podcast {
  id: string;
  name: string;
  host?: string;
  default_studio_settings?: string;
  tasks_time_allowance_days?: string;  // e.g. "7", "3 days", "1 week"
  created_at: string;
  updated_at: string;
}

export interface Episode {
  id: string;
  podcast_id: string;
  episode_number?: string;
  recording_date?: string;
  studio?: string;
  guest_names?: string;
  status: 'not_started' | 'recorded' | 'in_editing' | 'sent_to_client' | 'published';
  episode_notes?: string;
  drive_link?: string;
  backup_deletion_date?: string;
  card_name?: string;
  memory_card?: string;
  recording_engineer_id?: string;
  editing_engineer_id?: string;
  reels_engineer_id?: string;
  reels_notes?: string;
  studio_settings_override?: string;
  client_approved_editing?: 'pending' | 'approved' | 'rejected';
  client_approved_reels?: 'pending' | 'approved' | 'rejected';
  created_at: string;
  updated_at: string;
  podcast?: Podcast;
  recording_engineer?: User;
  editing_engineer?: User;
  reels_engineer?: User;
}

export interface Task {
  id: string;
  episode_id: string;
  type: 'recording' | 'editing' | 'reels' | 'publishing' | 'studio_preparation';
  status: 'not_started' | 'in_progress' | 'blocked' | 'done' | 'skipped';
  assigned_to?: string;
  due_date?: string;
  notes?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
  episode?: Episode;
  assigned_user?: User;
}

export interface User {
  id: string;
  name: string;
  email?: string;
  role?: string;
  created_at: string;
  updated_at: string;
}

export interface NotificationItem {
  id: string;
  type: 'recording_session' | 'due_task';
  title: string;
  message: string;
  due_date: string;
  episode_id?: string;
  task_id?: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
}

// Podcasts
export const getPodcasts = () => api.get<Podcast[]>('/podcasts');
export const getPodcast = (id: string) => api.get<Podcast>(`/podcasts/${id}`);
export const createPodcast = (data: Partial<Podcast>) => api.post<Podcast>('/podcasts', data);
export const updatePodcast = (id: string, data: Partial<Podcast>) => api.put<Podcast>(`/podcasts/${id}`, data);
export const deletePodcast = (id: string) => api.delete(`/podcasts/${id}`);

// Episodes
export const getEpisodes = (params?: { 
  podcast_id?: string; 
  status?: string; 
  limit?: number; 
  skip?: number;
  date_from?: string;
  date_to?: string;
}) => 
  api.get<Episode[]>('/episodes', { params });
export const getEpisodesCount = (params?: { 
  podcast_id?: string; 
  status?: string;
  date_from?: string;
  date_to?: string;
}) => 
  api.get<{ total: number }>('/episodes/count', { params });
export const getEpisode = (id: string) => api.get<Episode>(`/episodes/${id}`);
export const createEpisode = (data: Partial<Episode>) => api.post<Episode>('/episodes', data);
export const updateEpisode = (id: string, data: Partial<Episode>) => api.put<Episode>(`/episodes/${id}`, data);
export const deleteEpisode = (id: string) => api.delete(`/episodes/${id}`);
export const getUpcomingRecordings = (daysAhead?: number) => 
  api.get<Episode[]>('/episodes/upcoming/recordings', { params: { days_ahead: daysAhead } });

// Tasks
export const getTasks = (params?: { episode_id?: string; assigned_to?: string; status?: string; task_type?: string }) => 
  api.get<Task[]>('/tasks', { params });
export const getTask = (id: string) => api.get<Task>(`/tasks/${id}`);
export const createTask = (data: Partial<Task>) => api.post<Task>('/tasks', data);
export const updateTask = (id: string, data: Partial<Task>) => api.put<Task>(`/tasks/${id}`, data);
export const deleteTask = (id: string) => api.delete(`/tasks/${id}`);
export const getDueTasks = (daysAhead?: number) => 
  api.get<Task[]>('/tasks/due/upcoming', { params: { days_ahead: daysAhead } });
export const getOverdueTasks = () => api.get<Task[]>('/tasks/overdue');

// Users
export const getUsers = () => api.get<User[]>('/users');
export const getUser = (id: string) => api.get<User>(`/users/${id}`);
export const createUser = (data: Partial<User>) => api.post<User>('/users', data);
export const updateUser = (id: string, data: Partial<User>) => api.put<User>(`/users/${id}`, data);
export const deleteUser = (id: string) => api.delete(`/users/${id}`);

// Notifications
export const getNotifications = (daysAhead?: number) => 
  api.get<NotificationItem[]>('/notifications', { params: { days_ahead: daysAhead } });

// Import
export const importCSV = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/import/csv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

// Engineers
export const getEngineerEpisodes = (engineerId: string, params?: { role?: string; status?: string; upcoming_only?: boolean; days_ahead?: number }) =>
  api.get<Episode[]>(`/engineers/${engineerId}/episodes`, { params });
export const getEngineerUpcoming = (engineerId: string, daysAhead?: number) =>
  api.get<Episode[]>(`/engineers/${engineerId}/upcoming`, { params: { days_ahead: daysAhead } });
export const getEngineerTasks = (engineerId: string, status?: string) =>
  api.get(`/engineers/${engineerId}/tasks`, { params: { status } });
export const getAllEngineersSummary = () =>
  api.get('/engineers');

export default api;

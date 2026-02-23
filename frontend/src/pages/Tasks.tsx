import { useEffect, useState, useMemo } from 'react';
import { Plus, Search, Edit2, AlertCircle, X, ArrowUp, ArrowDown } from 'lucide-react';
import { getTasks, getUsers, updateTask, Task, User } from '../api';
import { format, formatDistanceToNow } from 'date-fns';
import TaskModal from '../components/TaskModal';

export default function Tasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAssignedTo, setSelectedAssignedTo] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'due_date' | 'episode' | 'type' | 'status' | 'assignee'>('due_date');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [tasksRes, usersRes] = await Promise.all([
          getTasks(),
          getUsers(),
        ]);
        setTasks(tasksRes.data);
        setFilteredTasks(tasksRes.data);
        setUsers(usersRes.data);
      } catch (error) {
        console.error('Failed to load tasks:', error);
      }
    };
    loadData();
  }, []);

  useEffect(() => {
    let filtered = tasks;

    // By default, exclude "done" and "skipped" (dismissed) unless explicitly selected
    if (selectedStatus === 'all') {
      filtered = filtered.filter(task => task.status !== 'done' && task.status !== 'skipped');
    } else if (selectedStatus !== 'all') {
      filtered = filtered.filter(task => task.status === selectedStatus);
    }

    if (searchTerm) {
      filtered = filtered.filter(task => 
        task.episode?.podcast?.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        task.notes?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedAssignedTo !== 'all') {
      filtered = filtered.filter(task => task.assigned_to === selectedAssignedTo);
    }

    if (selectedType !== 'all') {
      filtered = filtered.filter(task => task.type === selectedType);
    }

    setFilteredTasks(filtered);
  }, [tasks, searchTerm, selectedAssignedTo, selectedStatus, selectedType]);

  const sortedTasks = useMemo(() => {
    const list = [...filteredTasks];
    const mult = sortDir === 'asc' ? 1 : -1;
    list.sort((a, b) => {
      let cmp = 0;
      if (sortBy === 'due_date') {
        const da = a.due_date ? new Date(a.due_date).getTime() : 0;
        const db = b.due_date ? new Date(b.due_date).getTime() : 0;
        cmp = da - db;
      } else if (sortBy === 'episode') {
        const na = (a.episode?.podcast?.name || '') + (a.episode?.episode_number ?? '');
        const nb = (b.episode?.podcast?.name || '') + (b.episode?.episode_number ?? '');
        cmp = na.localeCompare(nb);
      } else if (sortBy === 'type') {
        cmp = (a.type || '').localeCompare(b.type || '');
      } else if (sortBy === 'status') {
        cmp = (a.status || '').localeCompare(b.status || '');
      } else if (sortBy === 'assignee') {
        const na = a.assigned_user?.name ?? 'Unassigned';
        const nb = b.assigned_user?.name ?? 'Unassigned';
        cmp = na.localeCompare(nb);
      }
      return mult * cmp;
    });
    return list;
  }, [filteredTasks, sortBy, sortDir]);

  const statusColors = {
    done: 'bg-gradient-to-r from-green-100 to-green-50 text-green-800 border border-green-200',
    in_progress: 'bg-gradient-to-r from-blue-100 to-blue-50 text-blue-800 border border-blue-200',
    blocked: 'bg-gradient-to-r from-red-100 to-red-50 text-red-800 border border-red-200',
    not_started: 'bg-gradient-to-r from-gray-100 to-gray-50 text-gray-800 border border-gray-200',
    sent_to_client: 'bg-gradient-to-r from-amber-100 to-amber-50 text-amber-800 border border-amber-200',
    skipped: 'bg-gradient-to-r from-yellow-100 to-yellow-50 text-yellow-800 border border-yellow-200',
  };

  const typeColors = {
    recording: 'bg-gradient-to-r from-purple-100 to-purple-50 text-purple-800 border border-purple-200',
    editing: 'bg-gradient-to-r from-blue-100 to-blue-50 text-blue-800 border border-blue-200',
    reels: 'bg-gradient-to-r from-pink-100 to-pink-50 text-pink-800 border border-pink-200',
    publishing: 'bg-gradient-to-r from-green-100 to-green-50 text-green-800 border border-green-200',
    studio_preparation: 'bg-gradient-to-r from-indigo-100 to-indigo-50 text-indigo-800 border border-indigo-200',
  };

  const isOverdue = (dueDate?: string) => {
    if (!dueDate) return false;
    return new Date(dueDate) < new Date();
  };

  const handleDismiss = async (task: Task) => {
    if (!confirm('Dismiss this task? It will be hidden from the list (status: Skipped). You can show it again by filtering by "Skipped".')) return;
    try {
      await updateTask(task.id, { status: 'skipped' });
      const response = await getTasks();
      setTasks(response.data);
    } catch (err) {
      console.error('Failed to dismiss task:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
            Tasks
          </h2>
          <p className="text-gray-500 mt-1">Track and manage your production tasks</p>
        </div>
        <button 
          onClick={() => {
            setSelectedTask(null);
            setIsModalOpen(true);
          }}
          className="inline-flex items-center px-5 py-2.5 border border-transparent rounded-xl shadow-lg shadow-primary-500/30 text-sm font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 transition-all duration-200 hover:shadow-xl hover:shadow-primary-500/40 hover:scale-105"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Task
        </button>
      </div>

      {/* Filters */}
      <div className="glass-dark p-5 rounded-xl shadow-lg border border-gray-200/50">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <select
            value={selectedAssignedTo}
            onChange={(e) => setSelectedAssignedTo(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
          >
            <option value="all">All Assignees</option>
            {users.map(user => (
              <option key={user.id} value={user.id}>{user.name}</option>
            ))}
          </select>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
          >
            <option value="all">All Statuses</option>
            <option value="not_started">Not Started</option>
            <option value="in_progress">In Progress</option>
            <option value="blocked">Blocked</option>
            <option value="sent_to_client">Sent to Client</option>
            <option value="done">Done</option>
            <option value="skipped">Skipped</option>
          </select>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
          >
            <option value="all">All Types</option>
            <option value="recording">Recording</option>
            <option value="editing">Editing</option>
            <option value="reels">Reels</option>
            <option value="publishing">Publishing</option>
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            className="border border-gray-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all bg-white"
          >
            <option value="due_date">Sort: Due date</option>
            <option value="episode">Sort: Episode</option>
            <option value="type">Sort: Type</option>
            <option value="status">Sort: Status</option>
            <option value="assignee">Sort: Assignee</option>
          </select>
          <button
            type="button"
            onClick={() => setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))}
            className="inline-flex items-center px-3 py-2.5 border border-gray-300 rounded-lg bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
            title={sortDir === 'asc' ? 'Ascending (click for descending)' : 'Descending (click for ascending)'}
          >
            {sortDir === 'asc' ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Tasks Table */}
      <div className="glass-dark rounded-xl shadow-lg border border-gray-200/50 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200/50">
            <thead className="bg-gradient-to-r from-gray-50 to-gray-50/50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Episode
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Owner
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Due Date
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Notes
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white/50 divide-y divide-gray-200/50">
              {sortedTasks.map((task) => {
                const overdue = isOverdue(task.due_date);
                return (
                  <tr key={task.id} className={`hover:bg-gray-50/50 transition-colors duration-150 ${overdue ? 'bg-red-50/50' : ''}`}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {task.episode?.podcast?.name || 'Unknown'}
                      </div>
                      <div className="text-sm text-gray-500">
                        Episode {task.episode?.episode_number || 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        typeColors[task.type] || 'bg-gradient-to-r from-gray-100 to-gray-50 text-gray-800 border border-gray-200'
                      }`}>
                        {task.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {task.assigned_user?.name || 'Unassigned'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {task.due_date ? (
                        <div className="text-sm text-gray-900">
                          {format(new Date(task.due_date), 'MMM d, yyyy')}
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">No due date</span>
                      )}
                      {task.due_date && (
                        <div className={`text-xs ${overdue ? 'text-red-600' : 'text-gray-500'}`}>
                          {overdue ? (
                            <span className="flex items-center">
                              <AlertCircle className="h-3 w-3 mr-1" />
                              Overdue
                            </span>
                          ) : (
                            formatDistanceToNow(new Date(task.due_date), { addSuffix: true })
                          )}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        statusColors[task.status] || statusColors.not_started
                      }`}>
                        {task.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {task.notes || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => {
                            setSelectedTask(task);
                            setIsModalOpen(true);
                          }}
                          className="text-primary-600 hover:text-primary-700 inline-flex items-center px-3 py-1.5 rounded-lg hover:bg-primary-50 transition-all duration-200 font-medium"
                        >
                          <Edit2 className="h-4 w-4 mr-1.5" />
                          Edit
                        </button>
                        <button
                          onClick={() => handleDismiss(task)}
                          className="text-gray-400 hover:text-red-600 p-1.5 rounded-lg hover:bg-red-50 transition-colors"
                          title="Dismiss (hide from list)"
                          aria-label="Dismiss task"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {sortedTasks.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No tasks found</p>
          </div>
        )}
      </div>

      <TaskModal
        task={selectedTask}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedTask(null);
        }}
        onSave={async () => {
          // Reload tasks
          const response = await getTasks();
          setTasks(response.data);
        }}
      />
    </div>
  );
}

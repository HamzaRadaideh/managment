// app/static/src/pages/tasks.ts
// Page-specific logic for the Tasks page

import { listTasks, deleteTask } from '../entities/tasks';
import { toast } from '../ui/toast';
import { debounce } from '../utils'; // Assuming you have a debounce utility

// --- DOM Elements ---
const rowsContainer = document.getElementById('tasks-rows') as HTMLElement;
const searchInput = document.getElementById('task-search') as HTMLInputElement;
const statusFilter = document.getElementById('task-status-filter') as HTMLSelectElement;
const priorityFilter = document.getElementById('task-priority-filter') as HTMLSelectElement;
const createTaskBtn = document.getElementById('create-task-btn') as HTMLButtonElement;

// --- State ---
let currentFilters = {
  q: '',
  status: '',
  priority: ''
};

// --- Helper Functions ---

/**
 * Renders the list of tasks into the table body.
 * @param tasks Array of task objects to render
 */
function renderTasks(tasks: any[]) { // Use 'any' or import Task type
  if (!rowsContainer) return;

  if (tasks.length === 0) {
    rowsContainer.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-gray-500">No tasks found.</td></tr>';
    return;
  }

  rowsContainer.innerHTML = tasks.map(task => `
    <tr data-task-id="${task.id}">
      <td>${task.title}</td>
      <td>${task.status}</td>
      <td>${task.priority}</td>
      <td class="text-right">
        <button class="btn-ghost btn-edit" data-id="${task.id}">Edit</button>
        <button class="btn-ghost btn-delete text-danger-600 hover:text-danger-800" data-id="${task.id}">Delete</button>
      </td>
    </tr>
  `).join('');
}

/**
 * Fetches tasks based on current filters and renders them.
 */
async function loadTasks() {
  if (!rowsContainer) return;
  // Show loading state
  rowsContainer.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-gray-500">Loading tasks...</td></tr>';

  try {
    const tasks = await listTasks(currentFilters);
    renderTasks(tasks);
  } catch (error) {
    console.error("Failed to load tasks:", error);
    rowsContainer.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-red-500">Failed to load tasks.</td></tr>';
    // Error toast is handled by api.ts interceptor
  }
}

/**
 * Updates the local filter state and triggers a reload.
 */
function updateFilters() {
  currentFilters.q = searchInput?.value.trim() ?? '';
  currentFilters.status = statusFilter?.value ?? '';
  currentFilters.priority = priorityFilter?.value ?? '';
  loadTasks();
}

// --- Event Listeners ---

// Debounced search input
const debouncedSearch = debounce(() => {
  currentFilters.q = searchInput.value;
  loadTasks();
}, 300); // Wait 300ms after typing stops

searchInput?.addEventListener('input', debouncedSearch);

// Filter changes
statusFilter?.addEventListener('change', updateFilters);
priorityFilter?.addEventListener('change', updateFilters);

// Create Task Button (Placeholder)
createTaskBtn?.addEventListener('click', () => {
  toast.info('Create Task modal would open here.');
  // Implement modal logic
});

// --- Event Delegation for Row Actions (Edit/Delete) ---
rowsContainer?.addEventListener('click', async (event) => {
  const target = event.target as HTMLElement;
  const row = target.closest('tr[data-task-id]');
  if (!row) return;

  const taskId = Number(row.dataset.taskId);
  if (isNaN(taskId)) return;

  if (target.classList.contains('btn-edit')) {
    toast.info(`Edit Task ${taskId} modal would open here.`);
    // Implement edit modal logic
  }

  if (target.classList.contains('btn-delete')) {
    if (confirm(`Are you sure you want to delete task #${taskId}?`)) {
      try {
        await deleteTask(taskId);
        toast.success('Task deleted successfully.');
        // Reload the list
        loadTasks();
      } catch (error) {
        // Error toast is handled by api.ts interceptor
        console.error("Failed to delete task:", error);
      }
    }
  }
});

// --- Initial Load ---
// Load tasks when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Set initial filter values if needed from URL params or state
    updateFilters(); // This will trigger the initial load
});

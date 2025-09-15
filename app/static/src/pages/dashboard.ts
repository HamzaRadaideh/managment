// app/static/src/pages/dashboard.ts
// Page-specific logic for the Dashboard

import api from '../api';
import { toast } from '../ui/toast';
import { debounce } from '../utils'; // Assuming you have a debounce utility

// --- DOM Elements ---
const globalSearchInput = document.getElementById('global-search') as HTMLInputElement;
const searchResultsContainer = document.getElementById('search-results') as HTMLElement;
const statsElements: Record<string, HTMLElement | null> = {
  tasks: document.querySelector('[data-stat="tasks"]'),
  notes: document.querySelector('[data-stat="notes"]'),
  collections: document.querySelector('[data-stat="collections"]'),
  completedTasks: document.querySelector('[data-stat="completed-tasks"]'),
};

// --- Helper Functions ---

/**
 * Fetches dashboard statistics and updates the UI.
 */
async function loadDashboardStats() {
  try {
    // Fetch counts for tasks, notes, collections
    // You might create specific API endpoints for counts later for efficiency
    // For now, fetch lists and count client-side
    const [tasksRes, notesRes, collectionsRes] = await Promise.all([
      api.get('/tasks/'),
      api.get('/notes/'),
      api.get('/collections/')
    ]);

    const tasks = tasksRes.data;
    const notes = notesRes.data;
    const collections = collectionsRes.data;

    const completedTasksCount = tasks.filter((t: any) => t.status === 'completed').length;

    // Update stats in the DOM
    if (statsElements.tasks) statsElements.tasks.textContent = tasks.length.toString();
    if (statsElements.notes) statsElements.notes.textContent = notes.length.toString();
    if (statsElements.collections) statsElements.collections.textContent = collections.length.toString();
    if (statsElements.completedTasks) statsElements.completedTasks.textContent = completedTasksCount.toString();

  } catch (error) {
    console.error("Failed to load dashboard stats:", error);
    toast.error("Could not load dashboard statistics.");
    // Set stats to '-' or 'Error' on failure
    Object.values(statsElements).forEach(el => { if (el) el.textContent = '-'; });
  }
}

/**
 * Performs a global search and displays results.
 */
async function performGlobalSearch(query: string) {
  if (!searchResultsContainer) return;

  if (!query.trim()) {
    searchResultsContainer.textContent = '';
    return;
  }

  searchResultsContainer.textContent = 'Searching...';

  try {
    const response = await api.get(`/search/global`, { params: { q: query } });
    const results = response.data;

    // Simple display of raw results (improve formatting later)
    if (Object.keys(results).length === 0) {
        searchResultsContainer.textContent = 'No results found.';
    } else {
         searchResultsContainer.innerHTML = `<pre class="bg-gray-100 p-2 rounded text-xs overflow-auto">${JSON.stringify(results, null, 2)}</pre>`;
    }
  } catch (error) {
    console.error("Global search failed:", error);
    searchResultsContainer.textContent = 'Search failed.';
    // Error toast is handled by api.ts
  }
}

// Debounced global search
const debouncedGlobalSearch = debounce((e: Event) => {
  const target = e.target as HTMLInputElement;
  performGlobalSearch(target.value);
}, 300);

// --- Event Listeners ---
globalSearchInput?.addEventListener('input', debouncedGlobalSearch);

// --- Initial Load ---
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
    // Global search is triggered by input
});

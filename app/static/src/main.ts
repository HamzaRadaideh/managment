import { api } from './api';
import { Toast, debounce, storage } from './utils';

// Main application class
class App {
  private currentPage: string;
  private searchDebounced: (query: string) => void;

  constructor() {
    this.currentPage = this.getCurrentPage();
    this.searchDebounced = debounce(this.performSearch.bind(this), 300);
    this.init();
  }

  private getCurrentPage(): string {
    const path = window.location.pathname;
    const segments = path.split('/').filter(Boolean);
    return segments[0] || 'dashboard';
  }

  private init(): void {
    this.initializeComponents();
    this.bindEventListeners();
    this.loadInitialData();
  }

  private initializeComponents(): void {
    // Initialize dropdowns
    this.initDropdowns();
    
    // Initialize modals
    this.initModals();
    
    // Initialize search
    this.initSearch();
    
    // Initialize forms
    this.initForms();
    
    // Initialize navigation
    this.initNavigation();
  }

  private initDropdowns(): void {
    const dropdownTriggers = document.querySelectorAll('[data-dropdown-trigger]');
    
    dropdownTriggers.forEach(trigger => {
      const targetId = trigger.getAttribute('data-dropdown-trigger');
      const dropdown = document.querySelector(`[data-dropdown="${targetId}"]`);
      
      if (dropdown) {
        trigger.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          
          // Close other dropdowns
          document.querySelectorAll('[data-dropdown]').forEach(dd => {
            if (dd !== dropdown) {
              dd.classList.add('hidden');
            }
          });
          
          // Toggle current dropdown
          dropdown.classList.toggle('hidden');
        });
      }
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', () => {
      document.querySelectorAll('[data-dropdown]').forEach(dropdown => {
        dropdown.classList.add('hidden');
      });
    });
  }

  private initModals(): void {
    const modalTriggers = document.querySelectorAll('[data-modal-trigger]');
    
    modalTriggers.forEach(trigger => {
      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = trigger.getAttribute('data-modal-trigger');
        const modal = document.querySelector(`[data-modal="${targetId}"]`);
        
        if (modal) {
          modal.classList.remove('hidden');
          document.body.style.overflow = 'hidden';
        }
      });
    });
    
    // Close modal handlers
    const closeButtons = document.querySelectorAll('[data-modal-close]');
    closeButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const modal = button.closest('[data-modal]');
        if (modal) {
          modal.classList.add('hidden');
          document.body.style.overflow = '';
        }
      });
    });
    
    // Close on backdrop click
    const modalBackdrops = document.querySelectorAll('[data-modal-backdrop]');
    modalBackdrops.forEach(backdrop => {
      backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) {
          const modal = backdrop.closest('[data-modal]');
          if (modal) {
            modal.classList.add('hidden');
            document.body.style.overflow = '';
          }
        }
      });
    });
  }

  private initSearch(): void {
    const searchInput = document.querySelector('[data-search-input]') as HTMLInputElement;
    const searchResults = document.querySelector('[data-search-results]');
    
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        const target = e.target as HTMLInputElement;
        const query = target.value.trim();
        
        if (query.length >= 2) {
          this.searchDebounced(query);
        } else if (searchResults) {
          searchResults.classList.add('hidden');
        }
      });
      
      // Handle search form submission
      const searchForm = searchInput.closest('form');
      if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
          e.preventDefault();
          const query = searchInput.value.trim();
          if (query.length >= 2) {
            window.location.href = `/search?q=${encodeURIComponent(query)}`;
          }
        });
      }
    }
  }

  private async performSearch(query: string): Promise<void> {
    const searchResults = document.querySelector('[data-search-results]');
    if (!searchResults) return;
    
    try {
      const results = await api.globalSearch({ q: query, limit: 5 });
      
      searchResults.innerHTML = this.renderSearchResults(results);
      searchResults.classList.remove('hidden');
    } catch (error) {
      console.error('Search failed:', error);
    }
  }

  private renderSearchResults(results: any): string {
    const { tasks, notes, collections, tags } = results.results;
    
    let html = '<div class="p-4">';
    
    if (tasks.length > 0) {
      html += '<div class="mb-4"><h4 class="font-medium text-secondary-900 mb-2">Tasks</h4>';
      tasks.forEach((task: any) => {
        html += `
          <a href="/tasks/${task.id}" class="block p-2 hover:bg-secondary-50 rounded">
            <div class="font-medium">${task.title}</div>
            <div class="text-sm text-secondary-600">${task.description || ''}</div>
          </a>
        `;
      });
      html += '</div>';
    }
    
    if (notes.length > 0) {
      html += '<div class="mb-4"><h4 class="font-medium text-secondary-900 mb-2">Notes</h4>';
      notes.forEach((note: any) => {
        html += `
          <a href="/notes/${note.id}" class="block p-2 hover:bg-secondary-50 rounded">
            <div class="font-medium">${note.title}</div>
            <div class="text-sm text-secondary-600">${note.description || ''}</div>
          </a>
        `;
      });
      html += '</div>';
    }
    
    if (collections.length > 0) {
      html += '<div class="mb-4"><h4 class="font-medium text-secondary-900 mb-2">Collections</h4>';
      collections.forEach((collection: any) => {
        html += `
          <a href="/collections/${collection.id}" class="block p-2 hover:bg-secondary-50 rounded">
            <div class="font-medium">${collection.title}</div>
            <div class="text-sm text-secondary-600">${collection.description || ''}</div>
          </a>
        `;
      });
      html += '</div>';
    }
    
    if (tags.length > 0) {
      html += '<div class="mb-4"><h4 class="font-medium text-secondary-900 mb-2">Tags</h4>';
      tags.forEach((tag: any) => {
        html += `
          <a href="/tags/${tag.id}" class="block p-2 hover:bg-secondary-50 rounded">
            <div class="font-medium">${tag.title}</div>
          </a>
        `;
      });
      html += '</div>';
    }
    
    if (results.total_count === 0) {
      html += '<div class="text-secondary-500 text-center py-4">No results found</div>';
    } else {
      html += `<div class="border-t pt-2"><a href="/search?q=${encodeURIComponent(results.query)}" class="text-primary-600 hover:text-primary-700 text-sm">View all ${results.total_count} results</a></div>`;
    }
    
    html += '</div>';
    return html;
  }

  private initForms(): void {
    const forms = document.querySelectorAll('form[data-api-form]');
    
    forms.forEach(form => {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formElement = e.target as HTMLFormElement;
        const formData = new FormData(formElement);
        const action = formElement.getAttribute('data-api-form');
        
        if (!action) return;
        
        try {
          await this.handleFormSubmission(action, formData, formElement);
        } catch (error) {
          this.handleFormError(error, formElement);
        }
      });
    });
  }

  private async handleFormSubmission(action: string, formData: FormData, form: HTMLFormElement): Promise<void> {
    const submitButton = form.querySelector('button[type="submit"]') as HTMLButtonElement;
    const originalText = submitButton?.textContent || '';
    
    // Show loading state
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = 'Loading...';
    }
    
    try {
      const data = Object.fromEntries(formData.entries());
      
      switch (action) {
        case 'login':
          await this.handleLogin(data);
          break;
        case 'register':
          await this.handleRegister(data);
          break;
        case 'create-task':
          await this.handleCreateTask(data);
          break;
        case 'create-note':
          await this.handleCreateNote(data);
          break;
        case 'create-collection':
          await this.handleCreateCollection(data);
          break;
        case 'create-tag':
          await this.handleCreateTag(data);
          break;
        default:
          throw new Error('Unknown form action');
      }
      
      Toast.show({ type: 'success', message: 'Success!' });
    } finally {
      // Reset button state
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = originalText;
      }
    }
  }

  private async handleLogin(data: any): Promise<void> {
    await api.login({ username: data.username, password: data.password });
    window.location.href = '/dashboard';
  }

  private async handleRegister(data: any): Promise<void> {
    await api.register(data);
    Toast.show({ type: 'success', message: 'Registration successful! Please log in.' });
    setTimeout(() => {
      window.location.href = '/login';
    }, 2000);
  }

  private async handleCreateTask(data: any): Promise<void> {
    const taskData = {
      title: data.title,
      description: data.description || undefined,
      status: data.status || 'todo',
      priority: data.priority || 'medium',
      collection_id: data.collection_id ? parseInt(data.collection_id) : undefined,
      tag_ids: data.tag_ids ? data.tag_ids.split(',').map((id: string) => parseInt(id.trim())) : undefined,
    };
    
    await api.createTask(taskData);
    window.location.reload();
  }

  private async handleCreateNote(data: any): Promise<void> {
    const noteData = {
      title: data.title,
      description: data.description || undefined,
      collection_id: data.collection_id ? parseInt(data.collection_id) : undefined,
      tag_ids: data.tag_ids ? data.tag_ids.split(',').map((id: string) => parseInt(id.trim())) : undefined,
    };
    
    await api.createNote(noteData);
    window.location.reload();
  }

  private async handleCreateCollection(data: any): Promise<void> {
    const collectionData = {
      title: data.title,
      description: data.description || undefined,
      type: data.type || 'mixed',
      tag_ids: data.tag_ids ? data.tag_ids.split(',').map((id: string) => parseInt(id.trim())) : undefined,
    };
    
    await api.createCollection(collectionData);
    window.location.reload();
  }

  private async handleCreateTag(data: any): Promise<void> {
    await api.createTag({ title: data.title });
    window.location.reload();
  }

  private handleFormError(error: any, form: HTMLFormElement): void {
    console.error('Form submission error:', error);
    
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    Toast.show({ type: 'error', message });
    
    // Clear any existing error messages
    form.querySelectorAll('.form-error').forEach(el => el.remove());
    
    // Show field-specific errors if available
    if (error.response?.data?.errors) {
      Object.entries(error.response.data.errors).forEach(([field, message]) => {
        const input = form.querySelector(`[name="${field}"]`);
        if (input) {
          const errorDiv = document.createElement('div');
          errorDiv.className = 'form-error';
          errorDiv.textContent = message as string;
          input.parentNode?.appendChild(errorDiv);
        }
      });
    }
  }

  private initNavigation(): void {
    // Handle mobile menu toggle
    const mobileMenuButton = document.querySelector('[data-mobile-menu-trigger]');
    const mobileMenu = document.querySelector('[data-mobile-menu]');
    
    if (mobileMenuButton && mobileMenu) {
      mobileMenuButton.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
      });
    }
    
    // Handle logout
    const logoutButtons = document.querySelectorAll('[data-logout]');
    logoutButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        this.handleLogout();
      });
    });
  }

  private async handleLogout(): Promise<void> {
    try {
      await api.logout();
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout error:', error);
      // Force logout even if API call fails
      api.clearToken();
      window.location.href = '/login';
    }
  }

  private async loadInitialData(): Promise<void> {
    if (!api.isAuthenticated() && this.currentPage !== 'login' && this.currentPage !== 'register') {
      window.location.href = '/login';
      return;
    }
    
    // Load page-specific data
    switch (this.currentPage) {
      case 'dashboard':
        await this.loadDashboardData();
        break;
      case 'tasks':
        await this.loadTasksData();
        break;
      case 'notes':
        await this.loadNotesData();
        break;
      case 'collections':
        await this.loadCollectionsData();
        break;
      case 'tags':
        await this.loadTagsData();
        break;
    }
  }

  private async loadDashboardData(): Promise<void> {
    try {
      const [tasks, notes, collections] = await Promise.all([
        api.getTasks(),
        api.getNotes(),
        api.getCollections(),
      ]);
      
      // Update dashboard stats
      this.updateDashboardStats({ tasks, notes, collections });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  }

  private updateDashboardStats(data: any): void {
    const stats = [
      { key: 'tasks', value: data.tasks.length, selector: '[data-stat="tasks"]' },
      { key: 'notes', value: data.notes.length, selector: '[data-stat="notes"]' },
      { key: 'collections', value: data.collections.length, selector: '[data-stat="collections"]' },
      { key: 'completed-tasks', value: data.tasks.filter((t: any) => t.status === 'completed').length, selector: '[data-stat="completed-tasks"]' },
    ];
    
    stats.forEach(({ selector, value }) => {
      const element = document.querySelector(selector);
      if (element) {
        element.textContent = value.toString();
      }
    });
  }

  private async loadTasksData(): Promise<void> {
    // Implementation for tasks page data loading
  }

  private async loadNotesData(): Promise<void> {
    // Implementation for notes page data loading
  }

  private async loadCollectionsData(): Promise<void> {
    // Implementation for collections page data loading
  }

  private async loadTagsData(): Promise<void> {
    // Implementation for tags page data loading
  }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new App();
});
// Utility functions for the frontend

export interface ToastOptions {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

export class Toast {
  private static container: HTMLElement | null = null;

  private static createContainer(): HTMLElement {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'fixed top-4 right-4 z-50 space-y-2';
      document.body.appendChild(this.container);
    }
    return this.container;
  }

  static show({ type, message, duration = 5000 }: ToastOptions): void {
    const container = this.createContainer();
    
    const toast = document.createElement('div');
    toast.className = `
      toast-item transform translate-x-full transition-all duration-300 ease-out
      px-4 py-3 rounded-lg shadow-lg max-w-sm
      ${type === 'success' ? 'bg-success-600 text-white' : ''}
      ${type === 'error' ? 'bg-danger-600 text-white' : ''}
      ${type === 'warning' ? 'bg-warning-600 text-white' : ''}
      ${type === 'info' ? 'bg-primary-600 text-white' : ''}
    `.trim();

    const icon = this.getIcon(type);
    toast.innerHTML = `
      <div class="flex items-center space-x-3">
        <div class="flex-shrink-0">
          ${icon}
        </div>
        <p class="text-sm font-medium">${message}</p>
      </div>
    `;

    container.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(() => {
      toast.classList.remove('translate-x-full');
      toast.classList.add('translate-x-0');
    });

    // Auto remove
    setTimeout(() => {
      toast.classList.add('translate-x-full');
      setTimeout(() => {
        if (container.contains(toast)) {
          container.removeChild(toast);
        }
      }, 300);
    }, duration);
  }

  private static getIcon(type: string): string {
    const icons = {
      success: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>`,
      error: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>`,
      warning: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>`,
      info: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>`,
    };
    return icons[type] || icons.info;
  }
}

// Modal utility
export class Modal {
  private element: HTMLElement;
  private backdrop: HTMLElement;

  constructor(content: string, options: { closable?: boolean; size?: 'sm' | 'md' | 'lg' | 'xl' } = {}) {
    const { closable = true, size = 'md' } = options;
    
    this.backdrop = document.createElement('div');
    this.backdrop.className = 'modal-overlay fixed inset-0 bg-black bg-opacity-50 z-50';
    
    this.element = document.createElement('div');
    this.element.className = `modal-container fixed inset-0 z-50 overflow-y-auto flex items-center justify-center p-4`;
    
    const sizeClasses = {
      sm: 'max-w-sm',
      md: 'max-w-md',
      lg: 'max-w-2xl',
      xl: 'max-w-4xl'
    };
    
    this.element.innerHTML = `
      <div class="modal-content bg-white rounded-lg shadow-xl ${sizeClasses[size]} w-full">
        ${closable ? `
          <button class="absolute top-4 right-4 text-secondary-400 hover:text-secondary-600 z-10">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        ` : ''}
        ${content}
      </div>
    `;

    if (closable) {
      const closeBtn = this.element.querySelector('button');
      closeBtn?.addEventListener('click', () => this.close());
      
      this.backdrop.addEventListener('click', () => this.close());
      
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') this.close();
      });
    }
  }

  show(): void {
    document.body.appendChild(this.backdrop);
    document.body.appendChild(this.element);
    document.body.style.overflow = 'hidden';
  }

  close(): void {
    document.body.removeChild(this.backdrop);
    document.body.removeChild(this.element);
    document.body.style.overflow = '';
  }
}

// Date formatting utilities
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (days > 7) {
    return formatDate(dateString);
  } else if (days > 0) {
    return `${days} day${days > 1 ? 's' : ''} ago`;
  } else if (hours > 0) {
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  } else if (minutes > 0) {
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  } else {
    return 'Just now';
  }
};

// Form validation utilities
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validateRequired = (value: string): boolean => {
  return value.trim().length > 0;
};

export const validateMinLength = (value: string, minLength: number): boolean => {
  return value.length >= minLength;
};

export const validateMaxLength = (value: string, maxLength: number): boolean => {
  return value.length <= maxLength;
};

// Debounce utility
export const debounce = <T extends (...args: any[]) => void>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

// Local storage utilities with error handling
export const storage = {
  get<T>(key: string, defaultValue: T): T {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch {
      return defaultValue;
    }
  },

  set(key: string, value: any): void {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    }
  },

  remove(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to remove from localStorage:', error);
    }
  },

  clear(): void {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Failed to clear localStorage:', error);
    }
  }
};

// URL utilities
export const updateURLParams = (params: Record<string, string | null>): void => {
  const url = new URL(window.location.href);
  
  Object.entries(params).forEach(([key, value]) => {
    if (value === null) {
      url.searchParams.delete(key);
    } else {
      url.searchParams.set(key, value);
    }
  });
  
  window.history.replaceState({}, '', url.toString());
};

export const getURLParams = (): Record<string, string> => {
  const params: Record<string, string> = {};
  const urlParams = new URLSearchParams(window.location.search);
  
  for (const [key, value] of urlParams.entries()) {
    params[key] = value;
  }
  
  return params;
};

// Element utilities
export const createElement = (
  tag: string,
  className?: string,
  innerHTML?: string
): HTMLElement => {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (innerHTML) element.innerHTML = innerHTML;
  return element;
};

export const toggleClass = (element: Element, className: string): void => {
  element.classList.toggle(className);
};

export const addClasses = (element: Element, ...classNames: string[]): void => {
  element.classList.add(...classNames);
};

export const removeClasses = (element: Element, ...classNames: string[]): void => {
  element.classList.remove(...classNames);
};
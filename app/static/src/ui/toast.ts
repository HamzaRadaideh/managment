// app/static/src/ui/toast.ts
// Global toast system using CustomEvent

// Get the container element where toasts will be appended
const mount = document.getElementById("toasts");
if (!mount) {
    console.warn("Toast container (#toasts) not found in DOM. Toasts will not be displayed.");
}

/**
 * Helper function to create DOM elements
 * @param tag The HTML tag name
 * @param cls Optional CSS classes
 * @param text Optional text content
 * @returns The created HTMLElement
 */
function el(tag: string, cls?: string, text?: string): HTMLElement {
  const element = document.createElement(tag);
  if (cls) element.className = cls;
  if (text) element.textContent = text;
  return element;
}

/**
 * Shows a toast message
 * @param type The type of toast (success, error, info, warning)
 * @param message The message to display
 */
function showToast(type: "success" | "error" | "info" | "warning", message: string): void {
  if (!mount) return; // Don't show if container is missing

  // Create toast element
  const toast = el("div", `toast toast-${type} flex items-center p-4 mb-2 rounded-lg shadow-lg transform transition-transform duration-300 translate-x-full`);
  // const toastMsg = el("div", "toast-msg", message); // Optional inner div for message
  // toast.appendChild(toastMsg);
  toast.textContent = message; // Simpler approach

  // Append to container
  mount.appendChild(toast);

  // Trigger entrance animation
  requestAnimationFrame(() => {
    toast.classList.remove('translate-x-full');
    toast.classList.add('translate-x-0');
  });

  // Auto remove after duration
  const duration = 3500; // ms
  setTimeout(() => {
    toast.classList.remove('translate-x-0');
    toast.classList.add('translate-x-full');
    // Remove element after animation
    setTimeout(() => {
      if (mount.contains(toast)) {
        mount.removeChild(toast);
      }
    }, 300); // Match CSS transition duration
  }, duration);
}

// Listen for global 'toast' CustomEvents
window.addEventListener("toast", (event: CustomEvent) => {
  const detail = event.detail;
  if (detail && typeof detail.type === 'string' && typeof detail.message === 'string') {
    showToast(detail.type, detail.message);
  } else {
    console.warn("Invalid toast event detail:", detail);
  }
});

// Export helper functions to dispatch toasts easily
export const toast = {
  success: (message: string) => window.dispatchEvent(new CustomEvent("toast", { detail: { type: "success", message } })),
  error: (message: string) => window.dispatchEvent(new CustomEvent("toast", { detail: { type: "error", message } })),
  info: (message: string) => window.dispatchEvent(new CustomEvent("toast", { detail: { type: "info", message } })),
  warning: (message: string) => window.dispatchEvent(new CustomEvent("toast", { detail: { type: "warning", message } })),
};

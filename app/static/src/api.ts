import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
}

export interface User {
  id: number;
  username: string;
  email: string;
  fname: string;
  lname: string;
  phone?: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  user_id: number;
  collection_id?: number;
  title: string;
  description?: string;
  status: 'todo' | 'in-progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  tag_ids: number[];
  created_at: string;
  updated_at: string;
}

export interface Note {
  id: number;
  user_id: number;
  collection_id?: number;
  title: string;
  description?: string;
  tag_ids: number[];
  created_at: string;
  updated_at: string;
}

export interface Collection {
  id: number;
  user_id: number;
  title: string;
  description?: string;
  type: 'mixed' | 'tasks-only' | 'notes-only';
  tag_ids: number[];
  task_count?: number;
  note_count?: number;
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  fname: string;
  lname: string;
  phone?: string;
  password: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  status?: 'todo' | 'in-progress' | 'completed';
  priority?: 'low' | 'medium' | 'high';
  collection_id?: number;
  tag_ids?: number[];
}

export interface NoteCreate {
  title: string;
  description?: string;
  collection_id?: number;
  tag_ids?: number[];
}

export interface CollectionCreate {
  title: string;
  description?: string;
  type?: 'mixed' | 'tasks-only' | 'notes-only';
  tag_ids?: number[];
}

export interface TagCreate {
  title: string;
}

export interface SearchResults {
  query: string;
  results: {
    tasks: Task[];
    notes: Note[];
    collections: Collection[];
    tags: Tag[];
  };
  total_count: number;
}

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor(baseURL: string = '/api/v1') {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearToken();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );

    // Initialize token from localStorage
    this.token = localStorage.getItem('auth_token');
  }

  private getToken(): string | null {
    return this.token || localStorage.getItem('auth_token');
  }

  public setToken(token: string): void {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  public clearToken(): void {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  public isAuthenticated(): boolean {
    return !!this.getToken();
  }

  // Auth methods
  async login(credentials: LoginRequest): Promise<Token> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await this.client.post<Token>('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    this.setToken(response.data.access_token);
    return response.data;
  }

  async register(userData: RegisterRequest): Promise<User> {
    const response = await this.client.post<User>('/auth/register', userData);
    return response.data;
  }

  async logout(): Promise<void> {
    this.clearToken();
  }

  // Task methods
  async getTasks(params?: {
    status?: string;
    priority?: string;
    collection_id?: number;
  }): Promise<Task[]> {
    const response = await this.client.get<Task[]>('/tasks/', { params });
    return response.data;
  }

  async getTask(id: number): Promise<Task> {
    const response = await this.client.get<Task>(`/tasks/${id}`);
    return response.data;
  }

  async createTask(task: TaskCreate): Promise<Task> {
    const response = await this.client.post<Task>('/tasks/', task);
    return response.data;
  }

  async updateTask(id: number, task: Partial<TaskCreate>): Promise<Task> {
    const response = await this.client.put<Task>(`/tasks/${id}`, task);
    return response.data;
  }

  async deleteTask(id: number): Promise<void> {
    await this.client.delete(`/tasks/${id}`);
  }

  async searchTasks(params: {
    q: string;
    status?: string;
    priority?: string;
    collection_id?: number;
    skip?: number;
    limit?: number;
  }): Promise<Task[]> {
    const response = await this.client.get<Task[]>('/tasks/search', { params });
    return response.data;
  }

  // Note methods
  async getNotes(collection_id?: number): Promise<Note[]> {
    const params = collection_id ? { collection_id } : {};
    const response = await this.client.get<Note[]>('/notes/', { params });
    return response.data;
  }

  async getNote(id: number): Promise<Note> {
    const response = await this.client.get<Note>(`/notes/${id}`);
    return response.data;
  }

  async createNote(note: NoteCreate): Promise<Note> {
    const response = await this.client.post<Note>('/notes/', note);
    return response.data;
  }

  async updateNote(id: number, note: Partial<NoteCreate>): Promise<Note> {
    const response = await this.client.put<Note>(`/notes/${id}`, note);
    return response.data;
  }

  async deleteNote(id: number): Promise<void> {
    await this.client.delete(`/notes/${id}`);
  }

  async searchNotes(params: {
    q: string;
    collection_id?: number;
    skip?: number;
    limit?: number;
  }): Promise<Note[]> {
    const response = await this.client.get<Note[]>('/notes/search', { params });
    return response.data;
  }

  // Collection methods
  async getCollections(type?: string): Promise<Collection[]> {
    const params = type ? { type } : {};
    const response = await this.client.get<Collection[]>('/collections/', { params });
    return response.data;
  }

  async getCollection(id: number): Promise<Collection> {
    const response = await this.client.get<Collection>(`/collections/${id}`);
    return response.data;
  }

  async createCollection(collection: CollectionCreate): Promise<Collection> {
    const response = await this.client.post<Collection>('/collections/', collection);
    return response.data;
  }

  async updateCollection(id: number, collection: Partial<CollectionCreate>): Promise<Collection> {
    const response = await this.client.put<Collection>(`/collections/${id}`, collection);
    return response.data;
  }

  async deleteCollection(id: number): Promise<void> {
    await this.client.delete(`/collections/${id}`);
  }

  async searchCollections(params: {
    q: string;
    type?: string;
    skip?: number;
    limit?: number;
  }): Promise<Collection[]> {
    const response = await this.client.get<Collection[]>('/collections/search', { params });
    return response.data;
  }

  // Tag methods
  async getTags(): Promise<Tag[]> {
    const response = await this.client.get<Tag[]>('/tags/');
    return response.data;
  }

  async getTag(id: number): Promise<Tag> {
    const response = await this.client.get<Tag>(`/tags/${id}`);
    return response.data;
  }

  async createTag(tag: TagCreate): Promise<Tag> {
    const response = await this.client.post<Tag>('/tags/', tag);
    return response.data;
  }

  async updateTag(id: number, tag: TagCreate): Promise<Tag> {
    const response = await this.client.put<Tag>(`/tags/${id}`, tag);
    return response.data;
  }

  async deleteTag(id: number): Promise<void> {
    await this.client.delete(`/tags/${id}`);
  }

  async searchTags(params: {
    q: string;
    skip?: number;
    limit?: number;
  }): Promise<Tag[]> {
    const response = await this.client.get<Tag[]>('/tags/search', { params });
    return response.data;
  }

  // Global search
  async globalSearch(params: {
    q: string;
    limit?: number;
  }): Promise<SearchResults> {
    const response = await this.client.get<SearchResults>('/search/global', { params });
    return response.data;
  }
}

// Create and export a singleton instance
export const api = new ApiClient();

// Export the class for custom instances if needed
export default ApiClient;
// app/static/src/entities/tasks.ts
// Wrapper around API calls for Tasks, using DTO types

import api from '../api';
import { Task, TaskCreate, TaskUpdate } from '../../types'; // Adjust path if needed

const TASKS_ENDPOINT = '/tasks';

/**
 * Fetches a list of tasks, optionally filtered.
 * @param params Optional query parameters for filtering/searching
 * @returns Promise resolving to an array of Task objects
 */
export async function listTasks(params: Record<string, any> = {}): Promise<Task[]> {
  const response = await api.get<Task[]>(TASKS_ENDPOINT, { params });
  return response.data;
}

/**
 * Fetches a single task by its ID.
 * @param id The ID of the task
 * @returns Promise resolving to the Task object
 */
export async function getTask(id: number): Promise<Task> {
  const response = await api.get<Task>(`${TASKS_ENDPOINT}/${id}`);
  return response.data;
}

/**
 * Creates a new task.
 * @param taskData The data for the new task
 * @returns Promise resolving to the created Task object
 */
export async function createTask(taskData: TaskCreate): Promise<Task> {
  const response = await api.post<Task>(TASKS_ENDPOINT, taskData);
  return response.data;
}

/**
 * Updates an existing task.
 * @param id The ID of the task to update
 * @param taskData The partial data to update
 * @returns Promise resolving to the updated Task object
 */
export async function updateTask(id: number, taskData: TaskUpdate): Promise<Task> {
  const response = await api.put<Task>(`${TASKS_ENDPOINT}/${id}`, taskData);
  return response.data;
}

/**
 * Deletes a task by its ID.
 * @param id The ID of the task to delete
 * @returns Promise resolving when deletion is complete
 */
export async function deleteTask(id: number): Promise<void> {
  await api.delete(`${TASKS_ENDPOINT}/${id}`);
}

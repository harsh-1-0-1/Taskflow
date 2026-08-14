import { request } from './client'

export function createTask(task) {
  return request('/api/tasks', {
    method: 'POST',
    body: JSON.stringify(task),
  })
}

export function updateTask(id, task) {
  return request(`/api/tasks/${id}`, {
    method: 'PUT',
    body: JSON.stringify(task),
  })
}

export function moveTask(id, columnId) {
  return request(`/api/tasks/${id}/move`, {
    method: 'PUT',
    body: JSON.stringify({ column_id: columnId }),
  })
}

export function deleteTask(id) {
  return request(`/api/tasks/${id}`, {
    method: 'DELETE',
  })
}

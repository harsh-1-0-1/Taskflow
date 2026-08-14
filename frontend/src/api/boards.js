import { request } from './client'

export function getBoard() {
  return request('/api/boards/1')
}

export function getTasksByPriority(priority) {
  return request(`/api/boards/1/tasks?priority=${encodeURIComponent(priority)}`)
}

export function getColumnCounts() {
  return request('/api/boards/1/columns/counts')
}

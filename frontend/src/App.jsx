import { useEffect, useState, useCallback } from 'react'
import Board from './components/Board'
import TaskForm from './components/TaskForm'
import { getBoard, getTasksByPriority } from './api/boards'
import { createTask, updateTask, deleteTask, moveTask } from './api/tasks'

const BOARD_ID = 1

function applyFilter(board, filteredTasks) {
  if (!filteredTasks) return board
  const byColumn = new Map()
  for (const t of filteredTasks) byColumn.set(t.column_id, (byColumn.get(t.column_id) ?? []).concat(t))
  return {
    ...board,
    columns: board.columns.map((c) => ({ ...c, tasks: byColumn.get(c.id) ?? [] })),
  }
}

export default function App() {
  const [board, setBoard] = useState({ name: 'Loading…', columns: [] })
  const [priority, setPriority] = useState('')
  const [error, setError] = useState('')
  const [form, setForm] = useState(null)

  const loadBoard = useCallback(async (filter) => {
    try {
      const data = await getBoard()
      const filtered = filter ? await getTasksByPriority(filter) : null
      setBoard(applyFilter(data, filtered))
      setError('')
    } catch (e) {
      setError(e.message)
    }
  }, [])

  useEffect(() => {
    loadBoard(priority)
  }, [loadBoard, priority])

  const handleCreate = async (payload) => {
    try {
      await createTask(payload)
      setForm(null)
      loadBoard(priority)
    } catch (e) {
      setError(e.message)
    }
  }

  const handleUpdate = async (payload) => {
    try {
      await updateTask(form.task.id, payload)
      setForm(null)
      loadBoard(priority)
    } catch (e) {
      setError(e.message)
    }
  }

  const handleDelete = async (taskId) => {
    if (!window.confirm('Delete this task?')) return
    try {
      await deleteTask(taskId)
      loadBoard(priority)
    } catch (e) {
      setError(e.message)
    }
  }

  const handleMove = async (taskId, columnId) => {
    try {
      await moveTask(taskId, columnId)
      loadBoard(priority)
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <>
      <Board
        board={board}
        columns={board.columns}
        filters={{ priority }}
        error={error}
        onCreateTask={(columnId) => setForm({ mode: 'create', columnId })}
        onEditTask={(task) => setForm({ mode: 'edit', task })}
        onDeleteTask={handleDelete}
        onMoveTask={handleMove}
        onFilterChange={(value) => setPriority(value)}
        onDismissError={() => setError('')}
      />
      {form && (
        <div className="modal-overlay" onClick={() => setForm(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <TaskForm
              columns={board.columns}
              initialTask={form.mode === 'edit' ? form.task : null}
              defaultColumnId={form.columnId}
              onSubmit={form.mode === 'create' ? handleCreate : handleUpdate}
              onCancel={() => setForm(null)}
            />
          </div>
        </div>
      )}
    </>
  )
}

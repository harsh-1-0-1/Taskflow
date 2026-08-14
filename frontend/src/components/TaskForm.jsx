import { useState } from 'react'

export default function TaskForm({ columns, initialTask = null, defaultColumnId = null, onSubmit, onCancel }) {
  const [columnId, setColumnId] = useState(
    initialTask ? initialTask.column_id : defaultColumnId ?? columns[0]?.id ?? ''
  )
  const [title, setTitle] = useState(initialTask ? initialTask.title : '')
  const [description, setDescription] = useState(initialTask ? initialTask.description ?? '' : '')
  const [priority, setPriority] = useState(initialTask ? initialTask.priority : 'Medium')

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({ column_id: columnId, title, description: description || null, priority })
  }

  return (
    <form className="task-form" onSubmit={handleSubmit}>
      <label>
        Title *
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What needs doing?"
          required
        />
      </label>
      <label>
        Description
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional details"
          rows="3"
        />
      </label>
      <label>
        Priority
        <select value={priority} onChange={(e) => setPriority(e.target.value)}>
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
        </select>
      </label>
      {!initialTask && (
        <label>
          Column
          <select value={columnId} onChange={(e) => setColumnId(Number(e.target.value))}>
            {columns.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </label>
      )}
      <div className="task-form-actions">
        <button type="submit">{initialTask ? 'Save' : 'Create task'}</button>
        <button type="button" className="secondary" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  )
}

export default function TaskCard({ task, columns, onEdit, onDelete, onMove }) {
  return (
    <div className={`task-card priority-${task.priority.toLowerCase()}`}>
      <div className="task-card-header">
        <span className="task-title">{task.title}</span>
        <span className={`priority-badge ${task.priority.toLowerCase()}`}>{task.priority}</span>
      </div>
      {task.description && <p className="task-description">{task.description}</p>}
      <div className="task-card-actions">
        <label>
          Move to
          <select
            value={task.column_id}
            onChange={(e) => onMove(task.id, Number(e.target.value))}
          >
            {columns.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </label>
        <button className="secondary" onClick={() => onEdit(task)}>
          Edit
        </button>
        <button className="danger" onClick={() => onDelete(task.id)}>
          Delete
        </button>
      </div>
    </div>
  )
}

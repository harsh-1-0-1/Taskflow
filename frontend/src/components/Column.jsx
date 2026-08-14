import TaskCard from './TaskCard'

export default function Column({ column, columns, onCreateTask, onEditTask, onDeleteTask, onMoveTask }) {
  return (
    <div className="column">
      <div className="column-header">
        <h3>{column.name}</h3>
        <span className="task-count">{column.tasks.length}</span>
      </div>
      <div className="task-list">
        {column.tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            columns={columns}
            onEdit={onEditTask}
            onDelete={onDeleteTask}
            onMove={onMoveTask}
          />
        ))}
        {column.tasks.length === 0 && <p className="empty-column">No tasks</p>}
      </div>
      <button className="add-task" onClick={() => onCreateTask(column.id)}>
        + Add task
      </button>
    </div>
  )
}

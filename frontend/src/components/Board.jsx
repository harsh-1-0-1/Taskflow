import Column from './Column'
import FilterBar from './FilterBar'
import ErrorBanner from './ErrorBanner'

export default function Board({ board, columns, filters, error, onCreateTask, onEditTask, onDeleteTask, onMoveTask, onFilterChange, onDismissError }) {
  return (
    <div className="board">
      <header className="board-header">
        <h1>{board.name}</h1>
        <FilterBar value={filters.priority} onChange={onFilterChange} />
      </header>
      <ErrorBanner message={error} onDismiss={onDismissError} />
      <div className="board-columns">
        {columns.map((column) => (
          <Column
            key={column.id}
            column={column}
            columns={columns}
            onCreateTask={onCreateTask}
            onEditTask={onEditTask}
            onDeleteTask={onDeleteTask}
            onMoveTask={onMoveTask}
          />
        ))}
      </div>
    </div>
  )
}

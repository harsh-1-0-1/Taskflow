const PRIORITIES = ['Low', 'Medium', 'High']

export default function FilterBar({ value, onChange }) {
  return (
    <div className="filter-bar">
      <label htmlFor="priority-filter">Filter by priority:</label>
      <select
        id="priority-filter"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">All</option>
        {PRIORITIES.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>
    </div>
  )
}

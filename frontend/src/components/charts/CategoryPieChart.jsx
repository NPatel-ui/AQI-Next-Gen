import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';
import { CATEGORY_DISTRIBUTION } from '../../utils/datasetInfo';

function CustomPieTooltip({ active, payload }) {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-[#102C22] text-white p-3 rounded-xl shadow-lg border border-[#173D2D] text-xs">
        <p className="font-semibold text-white">{data.name}</p>
        <p className="text-sm font-bold text-[#B7E46A] mt-1">
          {data.value}% <span className="text-[10px] text-[#A8BFA9]">({data.count} days)</span>
        </p>
      </div>
    );
  }
  return null;
}

export function CategoryPieChart({ height = 220 }) {
  return (
    <div style={{ width: '100%', height }} className="min-w-0 flex items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Tooltip content={<CustomPieTooltip />} />
          <Pie
            data={CATEGORY_DISTRIBUTION}
            innerRadius="60%"
            outerRadius="85%"
            paddingAngle={3}
            dataKey="value"
          >
            {CATEGORY_DISTRIBUTION.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} stroke="#FFFFFF" strokeWidth={1.5} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}


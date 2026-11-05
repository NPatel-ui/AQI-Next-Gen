import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';

function CustomComparisonTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#102C22] text-white p-3 rounded-xl shadow-lg border border-[#173D2D] text-xs space-y-2">
        <p className="font-semibold text-[#A8BFA9] border-b border-[#173D2D] pb-1">
          {label} (Historical Monthly Mean)
        </p>
        {payload.map((item) => (
          <div key={item.name} className="flex items-center justify-between gap-4">
            <span style={{ color: item.color }} className="font-medium">
              {item.name}:
            </span>
            <span className="font-mono font-bold text-white">{Math.round(item.value)} AQI</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
}

export function ComparisonLineChart({
  data,
  cityA = 'Delhi',
  cityB = 'Mumbai',
  height = 280,
}) {
  return (
    <div style={{ width: '100%', height }} className="min-w-0">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 15, right: 15, left: -15, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E3E8E1" />
          <XAxis
            dataKey="month"
            stroke="#69766E"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#E3E8E1' }}
          />
          <YAxis
            stroke="#69766E"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#E3E8E1' }}
          />
          <Tooltip content={<CustomComparisonTooltip />} />
          <Legend
            verticalAlign="top"
            align="right"
            wrapperStyle={{ paddingBottom: '10px', fontSize: '12px' }}
          />
          <Line
            type="monotone"
            dataKey={cityA}
            name={cityA}
            stroke="#173D2D"
            strokeWidth={3}
            dot={{ r: 4, fill: '#173D2D' }}
            activeDot={{ r: 6 }}
          />
          <Line
            type="monotone"
            dataKey={cityB}
            name={cityB}
            stroke="#10B981"
            strokeWidth={3}
            strokeDasharray="4 4"
            dot={{ r: 4, fill: '#10B981' }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}


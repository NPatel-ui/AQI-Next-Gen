import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts';

function CustomBarTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    const val = payload[0].value;
    return (
      <div className="bg-[#102C22] text-white p-3 rounded-xl shadow-lg border border-[#173D2D] text-xs space-y-1">
        <p className="font-semibold text-white">{label}</p>
        <p className="text-sm font-bold text-[#B7E46A] font-mono">
          {val} <span className="text-[10px] text-[#A8BFA9]">Average AQI</span>
        </p>
      </div>
    );
  }
  return null;
}

export function CityBarChart({ data, height = 240 }) {
  // Sort or take top 10 for clean presentation
  const chartData = (data || []).slice(0, 10);

  return (
    <div style={{ width: '100%', height }} className="min-w-0">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E3E8E1" />
          <XAxis
            dataKey="name"
            stroke="#69766E"
            fontSize={10}
            tickLine={false}
            axisLine={{ stroke: '#E3E8E1' }}
            angle={-30}
            textAnchor="end"
            interval={0}
          />
          <YAxis
            stroke="#69766E"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#E3E8E1' }}
          />
          <Tooltip content={<CustomBarTooltip />} />
          <Bar dataKey="avgAqi" radius={[6, 6, 0, 0]}>
            {chartData.map((entry, index) => {
              const aqi = entry.avgAqi;
              let fill = '#10B981';
              if (aqi > 200) fill = '#F97316';
              else if (aqi > 100) fill = '#F59E0B';
              else if (aqi > 50) fill = '#22C55E';
              return <Cell key={`cell-${index}`} fill={fill} />;
            })}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}


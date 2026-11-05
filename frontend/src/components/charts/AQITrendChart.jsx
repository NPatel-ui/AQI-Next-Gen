import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    const val = payload[0].value;
    return (
      <div className="bg-[#102C22] text-white p-3 rounded-xl shadow-lg border border-[#173D2D] text-xs space-y-1">
        <p className="font-semibold text-[#A8BFA9]">{label}</p>
        <p className="text-base font-bold text-white font-mono">
          {Math.round(val)} <span className="text-xs font-normal text-[#B7E46A]">AQI</span>
        </p>
        <p className="text-[10px] text-[#A8BFA9]/80">CPCB Historical Monthly Median</p>
      </div>
    );
  }
  return null;
}

export function AQITrendChart({ data, height = 240, dataKey = 'allAvg', city = 'All Cities' }) {
  return (
    <div style={{ width: '100%', height }} className="min-w-0">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="aqiForestGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#173D2D" stopOpacity={0.45} />
              <stop offset="95%" stopColor="#173D2D" stopOpacity={0.0} />
            </linearGradient>
          </defs>
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
            domain={[0, 'auto']}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey={dataKey}
            name={city}
            stroke="#173D2D"
            strokeWidth={2.5}
            fillOpacity={1}
            fill="url(#aqiForestGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}


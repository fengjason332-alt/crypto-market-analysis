/**
 * PriceChart — Recharts-based price line chart
 *
 * Reusable chart component for price trends, technical overlays, etc.
 * Supports multiple series (e.g., price + SMA lines).
 */

import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ReferenceLine,
} from "recharts";
import { formatUSD, formatDate, formatCompact } from "../utils/formatters";

const GRID_COLOR = "#2b2f36";
const AXIS_COLOR = "#5e6673";

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;

  return (
    <div className="bg-bg-card border border-bg-border rounded-lg px-4 py-3 shadow-xl">
      <div className="text-xs text-text-muted mb-2">{label}</div>
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center gap-2 text-sm">
          <span
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-text-secondary">{entry.name}:</span>
          <span className="text-text-primary font-medium">
            {typeof entry.value === "number"
              ? entry.value > 1000
                ? formatUSD(entry.value)
                : entry.value.toFixed(2)
              : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function PriceChart({
  data,
  lines = [],
  areas = [],
  bars = [],
  height = 400,
  yDomain,
  referenceLines = [],
  showGrid = true,
  formatY = (v) => formatCompact(v),
}) {
  if (!data || data.length === 0) {
    return (
      <div className="card flex items-center justify-center" style={{ height }}>
        <span className="text-text-muted text-sm">No data</span>
      </div>
    );
  }

  return (
    <div className="card p-0 overflow-hidden">
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={data} margin={{ top: 16, right: 16, bottom: 0, left: 0 }}>
          {showGrid && (
            <CartesianGrid strokeDasharray="3 3" stroke={GRID_COLOR} vertical={false} />
          )}

          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            stroke={AXIS_COLOR}
            tick={{ fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            minTickGap={60}
          />

          <YAxis
            stroke={AXIS_COLOR}
            tick={{ fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={formatY}
            domain={yDomain || ["auto", "auto"]}
            width={70}
          />

          <Tooltip content={<CustomTooltip />} />

          {areas.map(({ key, color, opacity = 0.1 }) => (
            <Area
              key={key}
              type="monotone"
              dataKey={key}
              stroke={color}
              strokeWidth={1}
              fill={color}
              fillOpacity={opacity}
              dot={false}
            />
          ))}

          {lines.map(({ key, color, width = 2, dash = false, name }) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              name={name || key}
              stroke={color}
              strokeWidth={width}
              strokeDasharray={dash ? "5 5" : undefined}
              dot={false}
              activeDot={{ r: 4, fill: color }}
            />
          ))}

          {bars.map(({ key, colorPositive, colorNegative }) => (
            <Bar
              key={key}
              dataKey={key}
              name={key}
              opacity={0.7}
              fill={colorPositive}
              // Custom coloring handled in data preprocessing
            />
          ))}

          {referenceLines.map(({ y, color, label, dash = true }, i) => (
            <ReferenceLine
              key={i}
              y={y}
              stroke={color}
              strokeDasharray={dash ? "3 3" : undefined}
              label={{
                value: label,
                position: "right",
                fill: color,
                fontSize: 11,
              }}
            />
          ))}

          <Legend
            verticalAlign="top"
            height={36}
            wrapperStyle={{ fontSize: 12, color: AXIS_COLOR }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

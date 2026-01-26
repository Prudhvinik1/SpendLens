"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { SpendingByCategory } from "@/lib/api";
import {
  formatCurrency,
  formatPercentage,
  getCategoryColor,
  getCategoryLabel,
} from "@/lib/utils";

interface CategoryChartProps {
  data: SpendingByCategory[];
}

export function CategoryChart({ data }: CategoryChartProps) {
  const chartData = data.slice(0, 6).map((item) => ({
    name: getCategoryLabel(item.category),
    value: item.total,
    percentage: item.percentage,
    color: getCategoryColor(item.category),
    category: item.category,
  }));

  const total = data.reduce((sum, item) => sum + item.total, 0);

  return (
    <div className="rounded-card bg-bg-card border border-border-subtle p-6">
      <h3 className="text-xs font-medium uppercase tracking-wider text-text-muted mb-6">
        Spending by Category
      </h3>

      <div className="flex flex-col lg:flex-row items-center gap-8">
        <div className="w-48 h-48 relative">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-bg-secondary border border-border-subtle rounded-lg px-3 py-2 shadow-lg">
                        <p className="text-text-primary text-sm font-medium">
                          {data.name}
                        </p>
                        <p className="text-text-secondary text-xs">
                          {formatCurrency(data.value)} ({formatPercentage(data.percentage)})
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <p className="text-xl font-bold text-text-primary">
                {formatCurrency(total)}
              </p>
              <p className="text-xs text-text-muted">Total</p>
            </div>
          </div>
        </div>

        <div className="flex-1 space-y-3">
          {chartData.map((item) => (
            <div key={item.category} className="flex items-center gap-3">
              <div
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-text-primary text-sm flex-1">
                {item.name}
              </span>
              <span className="text-text-secondary text-sm tabular-nums">
                {formatCurrency(item.value)}
              </span>
              <span className="text-text-muted text-xs w-12 text-right tabular-nums">
                {formatPercentage(item.percentage)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

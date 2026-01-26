"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

interface CategoryData {
  name: string;
  value: number;
  percentage: number;
  color: string;
}

interface CategoryChartProps {
  data: CategoryData[];
  total: number;
}

const COLORS = ["#f97316", "#8b5cf6", "#14b8a6", "#ef4444", "#a1a1aa"];

export default function CategoryChart({ data, total }: CategoryChartProps) {
  const chartData = data.map((item) => ({
    name: item.name,
    value: item.value,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>SPENDING BY CATEGORY</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col md:flex-row items-center gap-8">
          <div className="w-full md:w-64 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number) => `$${value.toFixed(2)}`}
                  contentStyle={{
                    backgroundColor: "#1a1a1a",
                    border: "1px solid #27272a",
                    borderRadius: "8px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex-1 space-y-3">
            {data.map((item, index) => (
              <div key={item.name} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  />
                  <span className="text-text-primary">{item.name}</span>
                </div>
                <div className="text-right">
                  <span className="text-text-primary font-semibold tabular-nums">
                    ${item.value.toFixed(2)}
                  </span>
                  <span className="text-text-muted ml-2">{item.percentage}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}


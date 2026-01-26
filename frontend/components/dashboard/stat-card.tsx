"use client";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  subtext?: string;
  trend?: "up" | "down";
  trendValue?: string;
}

export default function StatCard({
  label,
  value,
  subtext,
  trend,
  trendValue,
}: StatCardProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <p className="text-xs uppercase tracking-wide text-text-muted mb-2">
          {label}
        </p>
        <p className="text-3xl font-bold tabular-nums mb-2">{value}</p>
        {subtext && (
          <div className="flex items-center space-x-1 text-sm">
            {trend === "up" && (
              <TrendingUp className="h-4 w-4 text-accent-teal" />
            )}
            {trend === "down" && (
              <TrendingDown className="h-4 w-4 text-accent-red" />
            )}
            <span
              className={cn(
                trend === "up" && "text-accent-teal",
                trend === "down" && "text-accent-red",
                !trend && "text-text-secondary"
              )}
            >
              {subtext}
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}


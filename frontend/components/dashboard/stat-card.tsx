import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  subtext?: string;
  trend?: "up" | "down" | "neutral";
  icon?: LucideIcon;
  className?: string;
}

export function StatCard({
  label,
  value,
  subtext,
  trend,
  icon: Icon,
  className,
}: StatCardProps) {
  return (
    <div
      className={cn(
        "card-hover rounded-card bg-bg-card border border-border-subtle p-6",
        className
      )}
    >
      <div className="flex items-start justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-text-muted">
          {label}
        </span>
        {Icon && <Icon className="w-5 h-5 text-text-muted" />}
      </div>

      <div className="mt-3">
        <span className="text-3xl font-bold text-text-primary tabular-nums">
          {value}
        </span>
      </div>

      {subtext && (
        <p
          className={cn(
            "text-sm mt-2",
            trend === "up" && "text-accent-teal",
            trend === "down" && "text-accent-red",
            trend === "neutral" && "text-text-muted"
          )}
        >
          {subtext}
        </p>
      )}
    </div>
  );
}

import { cn } from "@/lib/utils";
import { AlertTriangle, CheckCircle, Info, Lightbulb, RefreshCw, TrendingUp } from "lucide-react";
import { Insight } from "@/lib/api";

interface InsightCardProps {
  insight: Insight;
}

const typeIcons = {
  subscription: RefreshCw,
  anomaly: AlertTriangle,
  trend: TrendingUp,
  tip: Lightbulb,
};

const severityStyles = {
  info: {
    border: "border-l-accent-teal",
    icon: "text-accent-teal",
    bg: "",
  },
  warning: {
    border: "border-l-accent-orange",
    icon: "text-accent-orange",
    bg: "",
  },
  alert: {
    border: "border-l-accent-red",
    icon: "text-accent-red",
    bg: "bg-accent-red/5",
  },
};

export function InsightCard({ insight }: InsightCardProps) {
  const Icon = typeIcons[insight.type as keyof typeof typeIcons] || Info;
  const styles = severityStyles[insight.severity as keyof typeof severityStyles] || severityStyles.info;

  return (
    <div
      className={cn(
        "rounded-lg bg-bg-card border border-border-subtle border-l-4 p-4",
        styles.border,
        styles.bg
      )}
    >
      <div className="flex items-start gap-3">
        <Icon className={cn("w-5 h-5 flex-shrink-0 mt-0.5", styles.icon)} />
        <div className="flex-1 min-w-0">
          <h4 className="text-text-primary font-medium text-sm">
            {insight.title}
          </h4>
          <p className="text-text-secondary text-sm mt-1">
            {insight.description}
          </p>
          {insight.action_suggestion && (
            <p className="text-text-muted text-xs mt-2 italic">
              {insight.action_suggestion}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

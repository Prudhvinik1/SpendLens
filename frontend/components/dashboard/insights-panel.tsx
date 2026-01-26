import { Insight } from "@/lib/api";
import { InsightCard } from "./insight-card";
import { Lightbulb } from "lucide-react";

interface InsightsPanelProps {
  insights: Insight[];
}

export function InsightsPanel({ insights }: InsightsPanelProps) {
  if (insights.length === 0) {
    return (
      <div className="rounded-card bg-bg-card border border-border-subtle p-6">
        <h3 className="text-xs font-medium uppercase tracking-wider text-text-muted mb-4 flex items-center gap-2">
          <Lightbulb className="w-4 h-4" />
          Insights
        </h3>
        <p className="text-text-secondary text-sm">
          No insights generated yet. Upload more transaction data for better analysis.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-card bg-bg-card border border-border-subtle p-6">
      <h3 className="text-xs font-medium uppercase tracking-wider text-text-muted mb-4 flex items-center gap-2">
        <Lightbulb className="w-4 h-4" />
        Insights
      </h3>

      <div className="space-y-3">
        {insights.map((insight) => (
          <InsightCard key={insight.id} insight={insight} />
        ))}
      </div>
    </div>
  );
}

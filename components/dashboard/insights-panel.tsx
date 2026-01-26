"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import InsightCard from "./insight-card";

interface Insight {
  type: "warning" | "info" | "success" | "tip";
  title: string;
  description: string;
  suggestion?: string;
}

interface InsightsPanelProps {
  insights: Insight[];
}

export default function InsightsPanel({ insights }: InsightsPanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>💡 INSIGHTS</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {insights.map((insight, index) => (
          <InsightCard key={index} {...insight} />
        ))}
      </CardContent>
    </Card>
  );
}


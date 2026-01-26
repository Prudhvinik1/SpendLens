"use client";

import { Card, CardContent } from "@/components/ui/card";
import { AlertTriangle, Info, CheckCircle, Lightbulb } from "lucide-react";
import { cn } from "@/lib/utils";

interface InsightCardProps {
  type: "warning" | "info" | "success" | "tip";
  title: string;
  description: string;
  suggestion?: string;
}

const iconMap = {
  warning: AlertTriangle,
  info: Info,
  success: CheckCircle,
  tip: Lightbulb,
};

const borderColorMap = {
  warning: "border-l-accent-orange",
  info: "border-l-accent-teal",
  success: "border-l-accent-teal",
  tip: "border-l-accent-purple",
};

export default function InsightCard({
  type,
  title,
  description,
  suggestion,
}: InsightCardProps) {
  const Icon = iconMap[type];

  return (
    <Card className={cn("border-l-4", borderColorMap[type])}>
      <CardContent className="pt-6">
        <div className="flex items-start space-x-3">
          <Icon className="h-5 w-5 text-accent-orange flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="font-semibold text-base mb-1">{title}</h4>
            <p className="text-sm text-text-secondary mb-2">{description}</p>
            {suggestion && (
              <p className="text-xs text-text-muted italic flex items-center space-x-1">
                <Lightbulb className="h-3 w-3" />
                <span>{suggestion}</span>
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}


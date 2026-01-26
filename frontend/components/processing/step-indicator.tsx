"use client";

import { Check, Circle } from "lucide-react";
import { cn } from "@/lib/utils";

interface Step {
  id: string;
  label: string;
  status: "completed" | "processing" | "pending";
  count?: number;
}

interface StepIndicatorProps {
  steps: Step[];
}

export default function StepIndicator({ steps }: StepIndicatorProps) {
  return (
    <div className="space-y-4">
      {steps.map((step) => (
        <div key={step.id} className="flex items-center space-x-4">
          <div className="flex-shrink-0">
            {step.status === "completed" ? (
              <div className="rounded-full bg-accent-teal p-1">
                <Check className="h-4 w-4 text-white" />
              </div>
            ) : step.status === "processing" ? (
              <div className="rounded-full bg-accent-orange p-1 animate-pulse-slow">
                <Circle className="h-4 w-4 text-accent-orange fill-accent-orange" />
              </div>
            ) : (
              <div className="rounded-full border-2 border-border-subtle p-1">
                <Circle className="h-4 w-4 text-text-muted" />
              </div>
            )}
          </div>
          <div className="flex-1">
            <p
              className={cn(
                "font-mono text-sm",
                step.status === "completed"
                  ? "text-accent-teal"
                  : step.status === "processing"
                  ? "text-accent-orange"
                  : "text-text-muted"
              )}
            >
              {step.label}
              {step.count !== undefined && ` (${step.count} found)`}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}


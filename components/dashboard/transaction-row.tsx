"use client";

import { Badge } from "@/components/ui/badge";
import { AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

interface TransactionRowProps {
  date: string;
  merchant: string;
  category: string;
  amount: number;
  isAnomaly?: boolean;
  anomalyNote?: string;
}

export default function TransactionRow({
  date,
  merchant,
  category,
  amount,
  isAnomaly,
  anomalyNote,
}: TransactionRowProps) {
  return (
    <div
      className={cn(
        "flex items-center space-x-4 py-3 px-4 rounded-lg transition-colors hover:bg-bg-card-hover group",
        isAnomaly && "border-l-2 border-l-accent-orange"
      )}
    >
      <div className="flex-shrink-0">
        <div
          className={cn(
            "w-2 h-2 rounded-full",
            isAnomaly ? "bg-accent-orange" : "bg-accent-teal"
          )}
        />
      </div>
      <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-2 md:gap-4 items-center">
        <span className="font-mono text-sm text-text-muted">{date}</span>
        <span className="text-text-primary">{merchant}</span>
        <Badge variant="outline" className="w-fit">
          {category}
        </Badge>
        <div className="flex items-center justify-start md:justify-end space-x-2">
          <span className="text-text-primary font-semibold tabular-nums">
            ${Math.abs(amount).toFixed(2)}
          </span>
          {isAnomaly && anomalyNote && (
            <div className="flex items-center space-x-1 text-accent-orange">
              <AlertTriangle className="h-4 w-4" />
              <span className="text-xs hidden sm:inline">{anomalyNote}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


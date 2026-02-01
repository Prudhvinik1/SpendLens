import { formatCurrency, formatDate } from "@/lib/utils";
import { RefreshCw } from "lucide-react";
import { Transaction } from "@/lib/api";

interface SubscriptionCardProps {
  transaction: Transaction;
}

export function SubscriptionCard({ transaction }: SubscriptionCardProps) {
  const monthlyCost = Math.abs(transaction.amount);
  const dailyCost = monthlyCost / 30;

  return (
    <div className="flex-shrink-0 w-44 rounded-lg bg-bg-card border border-border-subtle p-4 card-hover">
      <div className="w-10 h-10 rounded-lg bg-accent-teal/10 flex items-center justify-center mb-3">
        <RefreshCw className="w-5 h-5 text-accent-teal" />
      </div>

      <h4 className="text-text-primary font-medium text-sm truncate">
        {transaction.merchant || transaction.description.slice(0, 20)}
      </h4>

      <div className="mt-2 space-y-1">
        <p className="text-text-primary font-semibold text-sm tabular-nums">
          {formatCurrency(monthlyCost)}/mo
        </p>
        <p className="text-accent-orange text-xs font-medium tabular-nums">
          ≈ {formatCurrency(dailyCost)}/day
        </p>
      </div>

      <p className="text-text-muted text-xs mt-2">
        Last: {formatDate(transaction.date)}
      </p>
    </div>
  );
}

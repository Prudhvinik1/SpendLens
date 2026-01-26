import { formatCurrency, formatDate } from "@/lib/utils";
import { RefreshCw } from "lucide-react";
import { Transaction } from "@/lib/api";

interface SubscriptionCardProps {
  transaction: Transaction;
}

export function SubscriptionCard({ transaction }: SubscriptionCardProps) {
  return (
    <div className="flex-shrink-0 w-40 rounded-lg bg-bg-card border border-border-subtle p-4 card-hover">
      <div className="w-10 h-10 rounded-lg bg-accent-teal/10 flex items-center justify-center mb-3">
        <RefreshCw className="w-5 h-5 text-accent-teal" />
      </div>

      <h4 className="text-text-primary font-medium text-sm truncate">
        {transaction.merchant || transaction.description.slice(0, 20)}
      </h4>

      <p className="text-accent-orange font-semibold text-sm mt-1 tabular-nums">
        {formatCurrency(Math.abs(transaction.amount))}/mo
      </p>

      <p className="text-text-muted text-xs mt-1">
        Last: {formatDate(transaction.date)}
      </p>
    </div>
  );
}

import { Transaction } from "@/lib/api";
import { SubscriptionCard } from "./subscription-card";
import { formatCurrency } from "@/lib/utils";
import { RefreshCw } from "lucide-react";

interface SubscriptionListProps {
  transactions: Transaction[];
}

export function SubscriptionList({ transactions }: SubscriptionListProps) {
  const subscriptions = transactions.filter((t) => t.is_recurring);

  if (subscriptions.length === 0) {
    return (
      <div className="rounded-card bg-bg-card border border-border-subtle p-6">
        <h3 className="text-xs font-medium uppercase tracking-wider text-text-muted mb-4 flex items-center gap-2">
          <RefreshCw className="w-4 h-4" />
          Subscriptions Detected
        </h3>
        <p className="text-text-secondary text-sm">
          No recurring subscriptions detected in this statement.
        </p>
      </div>
    );
  }

  const totalMonthly = subscriptions.reduce(
    (sum, t) => sum + Math.abs(t.amount),
    0
  );

  return (
    <div className="rounded-card bg-bg-card border border-border-subtle p-6">
      <h3 className="text-xs font-medium uppercase tracking-wider text-text-muted mb-4 flex items-center gap-2">
        <RefreshCw className="w-4 h-4" />
        Subscriptions Detected
      </h3>

      <div className="flex gap-4 overflow-x-auto pb-2 -mx-2 px-2">
        {subscriptions.map((transaction) => (
          <SubscriptionCard key={transaction.id} transaction={transaction} />
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-border-subtle">
        <p className="text-text-secondary text-sm">
          Total:{" "}
          <span className="text-text-primary font-semibold">
            {formatCurrency(totalMonthly)}/month
          </span>
        </p>
      </div>
    </div>
  );
}

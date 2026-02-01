import Link from "next/link";
import { Transaction } from "@/lib/api";
import { SubscriptionCard } from "./subscription-card";
import { formatCurrency } from "@/lib/utils";
import { RefreshCw, ArrowRight, DollarSign } from "lucide-react";
import { Button } from "@/components/ui/button";

interface SubscriptionListProps {
  transactions: Transaction[];
  statementId?: number;
}

export function SubscriptionList({ transactions, statementId }: SubscriptionListProps) {
  const subscriptions = transactions.filter((t) => t.is_recurring && t.amount < 0);

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
  const totalDaily = totalMonthly / 30;

  return (
    <div className="rounded-card bg-bg-card border border-border-subtle p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-medium uppercase tracking-wider text-text-muted flex items-center gap-2">
          <RefreshCw className="w-4 h-4" />
          Subscriptions Detected
        </h3>
        {statementId && (
          <Link href={`/subscriptions/${statementId}`}>
            <Button variant="ghost" size="sm" className="text-accent-orange">
              Manage All
              <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </Link>
        )}
      </div>

      <div className="flex gap-4 overflow-x-auto pb-2 -mx-2 px-2">
        {subscriptions.map((transaction) => (
          <SubscriptionCard key={transaction.id} transaction={transaction} />
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-border-subtle flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-6">
          <p className="text-text-secondary text-sm">
            Monthly:{" "}
            <span className="text-text-primary font-semibold">
              {formatCurrency(totalMonthly)}
            </span>
          </p>
          <p className="text-text-secondary text-sm flex items-center gap-1">
            <DollarSign className="w-3 h-3 text-accent-orange" />
            Daily:{" "}
            <span className="text-accent-orange font-semibold">
              {formatCurrency(totalDaily)}
            </span>
          </p>
        </div>

        {statementId && (
          <Link
            href={`/subscriptions/${statementId}`}
            className="text-sm text-text-muted hover:text-accent-orange transition-colors"
          >
            See daily breakdown & manage →
          </Link>
        )}
      </div>
    </div>
  );
}

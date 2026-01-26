"use client";

import { useState } from "react";
import { Transaction } from "@/lib/api";
import {
  formatCurrency,
  formatDate,
  getCategoryColor,
  getCategoryLabel,
  cn,
} from "@/lib/utils";
import { AlertTriangle, RefreshCw, Search } from "lucide-react";

interface TransactionTableProps {
  transactions: Transaction[];
}

export function TransactionTable({ transactions }: TransactionTableProps) {
  const [filter, setFilter] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [showAnomaliesOnly, setShowAnomaliesOnly] = useState(false);

  const categories = Array.from(
    new Set(transactions.map((t) => t.category))
  ).sort();

  const filteredTransactions = transactions.filter((t) => {
    if (filter !== "all" && t.category !== filter) return false;
    if (showAnomaliesOnly && !t.is_anomaly) return false;
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      return (
        t.description.toLowerCase().includes(search) ||
        t.merchant?.toLowerCase().includes(search) ||
        t.category.toLowerCase().includes(search)
      );
    }
    return true;
  });

  return (
    <div className="rounded-card bg-bg-card border border-border-subtle">
      <div className="p-4 border-b border-border-subtle">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <h3 className="text-xs font-medium uppercase tracking-wider text-text-muted">
            Activity Log
          </h3>

          <div className="flex flex-wrap items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 pr-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-orange/50"
              />
            </div>

            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-sm text-text-primary focus:outline-none focus:border-accent-orange/50"
            >
              <option value="all">All Categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {getCategoryLabel(cat)}
                </option>
              ))}
            </select>

            <label className="flex items-center gap-2 text-sm text-text-secondary cursor-pointer">
              <input
                type="checkbox"
                checked={showAnomaliesOnly}
                onChange={(e) => setShowAnomaliesOnly(e.target.checked)}
                className="rounded border-border-subtle bg-bg-secondary text-accent-orange focus:ring-accent-orange"
              />
              Show anomalies only
            </label>
          </div>
        </div>
      </div>

      <div className="divide-y divide-border-subtle max-h-[500px] overflow-y-auto">
        {filteredTransactions.length === 0 ? (
          <div className="p-8 text-center text-text-muted">
            No transactions found matching your filters.
          </div>
        ) : (
          filteredTransactions.map((transaction) => (
            <div
              key={transaction.id}
              className={cn(
                "flex items-center gap-4 p-4 hover:bg-bg-card-hover transition-colors",
                transaction.is_anomaly && "border-l-2 border-l-accent-orange"
              )}
            >
              {/* Status dot */}
              <div className="flex-shrink-0">
                {transaction.is_anomaly ? (
                  <AlertTriangle className="w-4 h-4 text-accent-orange" />
                ) : transaction.is_recurring ? (
                  <RefreshCw className="w-4 h-4 text-accent-teal" />
                ) : (
                  <div className="w-2 h-2 rounded-full bg-accent-teal" />
                )}
              </div>

              {/* Date */}
              <span className="font-mono text-text-muted text-sm w-16 flex-shrink-0">
                {formatDate(transaction.date)}
              </span>

              {/* Merchant */}
              <span className="text-text-primary flex-1 truncate">
                {transaction.merchant || transaction.description}
              </span>

              {/* Category badge */}
              <span
                className="px-2 py-1 rounded text-xs font-medium flex-shrink-0"
                style={{
                  backgroundColor: `${getCategoryColor(transaction.category)}20`,
                  color: getCategoryColor(transaction.category),
                }}
              >
                {getCategoryLabel(transaction.category)}
              </span>

              {/* Amount */}
              <span
                className={cn(
                  "font-mono text-sm w-24 text-right flex-shrink-0 tabular-nums",
                  transaction.amount < 0
                    ? "text-text-primary"
                    : "text-accent-teal"
                )}
              >
                {transaction.amount < 0 ? "-" : "+"}
                {formatCurrency(transaction.amount)}
              </span>

              {/* Anomaly indicator */}
              {transaction.is_anomaly && transaction.anomaly_reason && (
                <div className="flex-shrink-0 group relative">
                  <div className="absolute right-0 bottom-full mb-2 hidden group-hover:block w-48 p-2 bg-bg-secondary border border-border-subtle rounded-lg text-xs text-text-secondary shadow-lg z-10">
                    {transaction.anomaly_reason}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      <div className="p-4 border-t border-border-subtle text-center">
        <p className="text-text-muted text-sm">
          Showing {filteredTransactions.length} of {transactions.length}{" "}
          transactions
        </p>
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import TransactionRow from "./transaction-row";
import { Search } from "lucide-react";

interface Transaction {
  date: string;
  merchant: string;
  category: string;
  amount: number;
  isAnomaly?: boolean;
  anomalyNote?: string;
}

interface TransactionTableProps {
  transactions: Transaction[];
}

export default function TransactionTable({
  transactions,
}: TransactionTableProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [showAnomaliesOnly, setShowAnomaliesOnly] = useState(false);

  const categories = Array.from(
    new Set(transactions.map((t) => t.category))
  ).sort();

  const filteredTransactions = transactions.filter((t) => {
    const matchesSearch =
      t.merchant.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory =
      selectedCategory === "All" || t.category === selectedCategory;
    const matchesAnomalyFilter = !showAnomaliesOnly || t.isAnomaly;

    return matchesSearch && matchesCategory && matchesAnomalyFilter;
  });

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>ACTIVITY LOG</CardTitle>
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-text-muted" />
            <Input
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-bg-secondary border-border-subtle"
            />
          </div>
        </div>
        <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-2 mt-4 gap-2">
          <div className="flex items-center space-x-2 flex-wrap gap-2">
            <Button
              variant={selectedCategory === "All" ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory("All")}
            >
              All
            </Button>
            {categories.map((cat) => (
              <Button
                key={cat}
                variant={selectedCategory === cat ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCategory(cat)}
              >
                {cat}
              </Button>
            ))}
          </div>
          <div className="flex items-center space-x-2 sm:ml-auto">
            <input
              type="checkbox"
              id="anomalies-only"
              checked={showAnomaliesOnly}
              onChange={(e) => setShowAnomaliesOnly(e.target.checked)}
              className="rounded"
            />
            <label
              htmlFor="anomalies-only"
              className="text-sm text-text-secondary cursor-pointer whitespace-nowrap"
            >
              Show anomalies only
            </label>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-1">
          {filteredTransactions.map((transaction, index) => (
            <TransactionRow key={index} {...transaction} />
          ))}
        </div>
        {filteredTransactions.length === 0 && (
          <div className="text-center py-8 text-text-muted">
            No transactions found
          </div>
        )}
        {filteredTransactions.length > 10 && (
          <div className="mt-4 text-center">
            <Button variant="outline" size="sm">
              Load more
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}


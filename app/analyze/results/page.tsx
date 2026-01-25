"use client";

import { Button } from "@/components/ui/button";
import StatCard from "@/components/dashboard/stat-card";
import CategoryChart from "@/components/dashboard/category-chart";
import InsightsPanel from "@/components/dashboard/insights-panel";
import SubscriptionList from "@/components/dashboard/subscription-list";
import TransactionTable from "@/components/dashboard/transaction-table";
import { Upload, FileDown } from "lucide-react";

// Mock data - replace with actual API data
const mockStats = {
  totalSpent: 3247,
  income: 450,
  transactions: 87,
  dailyAvg: 104.77,
};

const mockCategories = [
  { name: "Dining", value: 847, percentage: 26, color: "#f97316" },
  { name: "Shopping", value: 634, percentage: 20, color: "#8b5cf6" },
  { name: "Groceries", value: 423, percentage: 13, color: "#14b8a6" },
  { name: "Transport", value: 312, percentage: 10, color: "#ef4444" },
  { name: "Other", value: 1031, percentage: 31, color: "#a1a1aa" },
];

const mockInsights = [
  {
    type: "warning" as const,
    title: "High Dining Spend",
    description: "You spent $847 on dining (26% of total)",
    suggestion: "Try meal prepping on Sundays to cut costs.",
  },
  {
    type: "info" as const,
    title: "Subscription Creep",
    description: "5 subscriptions = $94/month",
  },
  {
    type: "success" as const,
    title: "Low Bank Fees",
    description: "Only $4 in fees. Nice!",
  },
];

const mockSubscriptions = [
  { name: "Netflix", amount: 15.99, lastDate: "Jan 15" },
  { name: "Spotify", amount: 9.99, lastDate: "Jan 12" },
  { name: "ChatGPT", amount: 20.0, lastDate: "Jan 16" },
  { name: "Gym", amount: 45.0, lastDate: "Jan 1" },
];

const mockTransactions = [
  { date: "01/15", merchant: "Amazon", category: "Shopping", amount: -47.99 },
  {
    date: "01/15",
    merchant: "Whole Foods",
    category: "Groceries",
    amount: -89.23,
  },
  {
    date: "01/14",
    merchant: "Uber",
    category: "Transportation",
    amount: -23.4,
  },
  {
    date: "01/14",
    merchant: "DoorDash",
    category: "Dining",
    amount: -34.56,
    isAnomaly: true,
    anomalyNote: "3rd this week",
  },
  {
    date: "01/13",
    merchant: "Shell Gas",
    category: "Transportation",
    amount: -45.0,
  },
  {
    date: "01/12",
    merchant: "Netflix",
    category: "Subscriptions",
    amount: -15.99,
  },
  {
    date: "01/11",
    merchant: "Target",
    category: "Shopping",
    amount: -67.43,
  },
];

export default function ResultsPage() {
  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header Actions */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-semibold mb-1">January 1 - January 31, 2025</h1>
        </div>
        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <Button variant="outline" size="sm" className="flex-1 sm:flex-initial">
            <Upload className="h-4 w-4 mr-2" />
            <span className="hidden sm:inline">Upload New</span>
            <span className="sm:hidden">Upload</span>
          </Button>
          <Button variant="outline" size="sm" className="flex-1 sm:flex-initial">
            <FileDown className="h-4 w-4 mr-2" />
            <span className="hidden sm:inline">Export PDF</span>
            <span className="sm:hidden">Export</span>
          </Button>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          label="TOTAL SPENT"
          value={`$${mockStats.totalSpent.toLocaleString()}`}
          subtext="↑12% vs last month"
          trend="up"
        />
        <StatCard
          label="INCOME"
          value={`$${mockStats.income.toLocaleString()}`}
        />
        <StatCard
          label="TRANSACTIONS"
          value={mockStats.transactions.toString()}
        />
        <StatCard
          label="DAILY AVG"
          value={`$${mockStats.dailyAvg.toFixed(2)}`}
        />
      </div>

      {/* Category Chart and Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CategoryChart data={mockCategories} total={mockStats.totalSpent} />
        <InsightsPanel insights={mockInsights} />
      </div>

      {/* Subscriptions */}
      <SubscriptionList subscriptions={mockSubscriptions} />

      {/* Transactions */}
      <TransactionTable transactions={mockTransactions} />
    </div>
  );
}


"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Header } from "@/components/layout/header";
import { StatCard } from "@/components/dashboard/stat-card";
import { CategoryChart } from "@/components/dashboard/category-chart";
import { InsightsPanel } from "@/components/dashboard/insights-panel";
import { SubscriptionList } from "@/components/dashboard/subscription-list";
import { TransactionTable } from "@/components/dashboard/transaction-table";
import { Progress } from "@/components/ui/progress";
import { getAnalysis, getStatus, FullAnalysisResponse } from "@/lib/api";
import {
  formatCurrency,
  formatDateLong,
} from "@/lib/utils";
import {
  DollarSign,
  TrendingDown,
  TrendingUp,
  Receipt,
  Calendar,
  CheckCircle,
  Loader2,
} from "lucide-react";

type ProcessingStep = {
  label: string;
  status: "pending" | "processing" | "completed";
};

export default function AnalyzePage() {
  const params = useParams();
  const statementId = Number(params.id);

  const [analysis, setAnalysis] = useState<FullAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [progress, setProgress] = useState(0);
  const [steps, setSteps] = useState<ProcessingStep[]>([
    { label: "Parsing transactions", status: "processing" },
    { label: "Categorizing spending", status: "pending" },
    { label: "Detecting patterns", status: "pending" },
    { label: "Generating insights", status: "pending" },
  ]);

  useEffect(() => {
    let isMounted = true;
    let pollCount = 0;

    const fetchAnalysis = async () => {
      try {
        // First check status
        const status = await getStatus(statementId);

        if (status.status === "processing") {
          // Update progress animation
          pollCount++;
          const simulatedProgress = Math.min(pollCount * 15, 85);
          setProgress(simulatedProgress);

          // Update steps based on progress
          const newSteps = [...steps];
          if (simulatedProgress > 20) {
            newSteps[0].status = "completed";
            newSteps[1].status = "processing";
          }
          if (simulatedProgress > 40) {
            newSteps[1].status = "completed";
            newSteps[2].status = "processing";
          }
          if (simulatedProgress > 60) {
            newSteps[2].status = "completed";
            newSteps[3].status = "processing";
          }
          setSteps(newSteps);

          // Poll again
          setTimeout(fetchAnalysis, 2000);
          return;
        }

        if (status.status === "failed") {
          setError(status.error_message || "Processing failed");
          setIsLoading(false);
          return;
        }

        // Get full analysis
        const data = await getAnalysis(statementId);

        if (isMounted) {
          // Complete all steps
          setSteps(steps.map((s) => ({ ...s, status: "completed" as const })));
          setProgress(100);

          // Short delay for animation
          setTimeout(() => {
            setAnalysis(data);
            setIsLoading(false);
          }, 500);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load analysis");
          setIsLoading(false);
        }
      }
    };

    fetchAnalysis();

    return () => {
      isMounted = false;
    };
  }, [statementId]);

  // Loading / Processing state
  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 flex items-center justify-center px-4">
          <div className="w-full max-w-md text-center">
            <h2 className="text-2xl font-semibold text-text-primary mb-8">
              Analyzing your spending...
            </h2>

            <div className="bg-bg-card border border-border-subtle rounded-card p-6 text-left">
              <div className="space-y-4 mb-6">
                {steps.map((step, index) => (
                  <div key={index} className="flex items-center gap-3">
                    {step.status === "completed" ? (
                      <CheckCircle className="w-5 h-5 text-accent-teal" />
                    ) : step.status === "processing" ? (
                      <Loader2 className="w-5 h-5 text-accent-orange animate-spin" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border-2 border-border-subtle" />
                    )}
                    <span
                      className={
                        step.status === "completed"
                          ? "text-text-primary"
                          : step.status === "processing"
                          ? "text-accent-orange"
                          : "text-text-muted"
                      }
                    >
                      {step.label}
                    </span>
                  </div>
                ))}
              </div>

              <Progress value={progress} className="mb-3" />

              <p className="text-text-muted text-sm text-center">
                {progress < 100
                  ? "This usually takes about 15-30 seconds..."
                  : "Almost there..."}
              </p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 flex items-center justify-center px-4">
          <div className="text-center">
            <h2 className="text-2xl font-semibold text-accent-red mb-4">
              Analysis Failed
            </h2>
            <p className="text-text-secondary mb-8">{error}</p>
            <a
              href="/"
              className="inline-flex items-center gap-2 px-4 py-2 bg-accent-orange text-white rounded-lg hover:bg-accent-orange-dim transition-colors"
            >
              Try Again
            </a>
          </div>
        </main>
      </div>
    );
  }

  if (!analysis) return null;

  const { summary, spending_by_category, transactions, insights } = analysis;

  return (
    <div className="min-h-screen flex flex-col bg-bg-primary">
      <Header showActions />

      <main className="flex-1 container mx-auto px-4 py-8">
        {/* Period header */}
        <div className="flex items-center gap-2 text-text-secondary mb-8">
          <Calendar className="w-4 h-4" />
          <span>
            {summary.period_start && summary.period_end
              ? `${formatDateLong(summary.period_start)} - ${formatDateLong(
                  summary.period_end
                )}`
              : "Statement Period"}
          </span>
        </div>

        {/* Stat cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            label="Total Spent"
            value={formatCurrency(summary.total_spent)}
            icon={TrendingDown}
          />
          <StatCard
            label="Income"
            value={formatCurrency(summary.total_income)}
            icon={TrendingUp}
          />
          <StatCard
            label="Transactions"
            value={summary.total_transactions.toString()}
            icon={Receipt}
          />
          <StatCard
            label="Net Change"
            value={formatCurrency(Math.abs(summary.net_change))}
            subtext={summary.net_change >= 0 ? "Surplus" : "Deficit"}
            trend={summary.net_change >= 0 ? "up" : "down"}
            icon={DollarSign}
          />
        </div>

        {/* Charts and Insights row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <CategoryChart data={spending_by_category} />
          <InsightsPanel insights={insights} />
        </div>

        {/* Subscriptions */}
        <div className="mb-8">
          <SubscriptionList transactions={transactions} />
        </div>

        {/* Transactions table */}
        <TransactionTable transactions={transactions} />
      </main>
    </div>
  );
}

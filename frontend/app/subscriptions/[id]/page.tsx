"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Header } from "@/components/layout/header";
import { SubscriptionManager } from "@/components/dashboard/subscription-manager";
import { getAnalysis, FullAnalysisResponse } from "@/lib/api";
import { ArrowLeft, Loader2 } from "lucide-react";

export default function SubscriptionsPage() {
  const params = useParams();
  const statementId = Number(params.id);

  const [analysis, setAnalysis] = useState<FullAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getAnalysis(statementId);
        setAnalysis(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [statementId]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header showActions />
        <main className="flex-1 flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-accent-orange animate-spin" />
        </main>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header showActions />
        <main className="flex-1 flex items-center justify-center px-4">
          <div className="text-center">
            <h2 className="text-2xl font-semibold text-accent-red mb-4">
              Failed to Load
            </h2>
            <p className="text-text-secondary mb-8">{error}</p>
            <Link
              href="/"
              className="inline-flex items-center gap-2 px-4 py-2 bg-accent-orange text-white rounded-lg hover:bg-accent-orange-dim transition-colors"
            >
              Go Home
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-bg-primary">
      <Header showActions />

      <main className="flex-1 container mx-auto px-4 py-8">
        {/* Back link */}
        <Link
          href={`/analyze/${statementId}`}
          className="inline-flex items-center gap-2 text-text-secondary hover:text-text-primary transition-colors mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>

        {/* Page title */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            Subscription Manager
          </h1>
          <p className="text-text-secondary">
            Track your recurring charges, see daily costs, and manage cancellation reminders.
          </p>
        </div>

        {/* Subscription Manager Component */}
        <SubscriptionManager
          transactions={analysis.transactions}
          statementId={statementId}
        />
      </main>
    </div>
  );
}

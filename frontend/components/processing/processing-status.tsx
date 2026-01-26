"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import StepIndicator from "./step-indicator";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent } from "@/components/ui/card";

interface Step {
  id: string;
  label: string;
  status: "completed" | "processing" | "pending";
  count?: number;
}

export default function ProcessingStatus() {
  const router = useRouter();
  const [progress, setProgress] = useState(65);
  const [steps, setSteps] = useState<Step[]>([
    { id: "parse", label: "Parsing transactions", status: "completed", count: 87 },
    { id: "categorize", label: "Categorizing spending", status: "completed" },
    { id: "patterns", label: "Detecting patterns...", status: "processing" },
    { id: "insights", label: "Generating insights", status: "pending" },
  ]);

  useEffect(() => {
    // Simulate processing
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          // Navigate to results after completion
          setTimeout(() => {
            router.push("/analyze/results");
          }, 1000);
          return 100;
        }
        return prev + 5;
      });
    }, 500);

    return () => clearInterval(interval);
  }, [router]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] px-4">
      <Card className="w-full max-w-2xl">
        <CardContent className="pt-6">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold mb-2">Analyzing your spending...</h2>
          </div>

          <StepIndicator steps={steps} />

          <div className="mt-8 space-y-2">
            <Progress value={progress} className="h-2" />
            <p className="text-sm text-text-muted text-center">
              Estimated time: ~{Math.max(0, Math.ceil((100 - progress) / 5) * 0.5)} seconds
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}


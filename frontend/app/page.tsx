"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/layout/header";
import { UploadZone } from "@/components/landing/upload-zone";
import { FeatureCards } from "@/components/landing/feature-cards";
import { Button } from "@/components/ui/button";
import { uploadStatement, processDemoData } from "@/lib/api";
import { Loader2 } from "lucide-react";

export default function HomePage() {
  const router = useRouter();
  const [isUploading, setIsUploading] = useState(false);
  const [isDemoLoading, setIsDemoLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (file: File) => {
    setIsUploading(true);
    setError(null);

    try {
      const response = await uploadStatement(file);

      if (response.success && response.statement_id) {
        router.push(`/analyze/${response.statement_id}`);
      } else {
        setError(response.error || "Upload failed. Please try again.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleSampleData = async (sampleId: string = "sample_bofa") => {
    setIsDemoLoading(true);
    setError(null);

    try {
      const response = await processDemoData(sampleId);

      if (response.success && response.statement_id) {
        router.push(`/analyze/${response.statement_id}`);
      } else {
        setError(response.error || "Failed to load sample data.");
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Demo processing failed. Is the backend running?"
      );
    } finally {
      setIsDemoLoading(false);
    }
  };

  const isLoading = isUploading || isDemoLoading;

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 flex flex-col items-center justify-center px-4 py-16">
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-4xl md:text-5xl font-bold text-text-primary mb-4">
            Where does your money
            <br />
            <span className="text-accent-orange">actually go?</span>
          </h1>
          <p className="text-text-secondary text-lg max-w-md mx-auto">
            Upload your bank statement and get AI-powered insights in seconds.
          </p>
        </div>

        <div className="w-full max-w-xl mb-8 animate-slide-up">
          <UploadZone
            onFileSelect={handleFileSelect}
            isUploading={isUploading}
            error={error}
          />

          <div className="flex flex-col items-center gap-3 mt-6">
            <p className="text-text-muted text-sm">Or try with sample data:</p>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => handleSampleData("sample_bofa")}
                disabled={isLoading}
                className="min-w-[140px]"
              >
                {isDemoLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                ) : null}
                Bank of America
              </Button>
              <Button
                variant="outline"
                onClick={() => handleSampleData("sample_discover")}
                disabled={isLoading}
                className="min-w-[140px]"
              >
                {isDemoLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                ) : null}
                Discover Card
              </Button>
            </div>
          </div>
        </div>

        <div className="w-full border-t border-border-subtle pt-12 mt-8">
          <FeatureCards />
        </div>
      </main>
    </div>
  );
}

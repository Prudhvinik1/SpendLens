"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/layout/header";
import { UploadZone } from "@/components/landing/upload-zone";
import { FeatureCards } from "@/components/landing/feature-cards";
import { Button } from "@/components/ui/button";
import { uploadStatement } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [isUploading, setIsUploading] = useState(false);
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

  const handleSampleData = async () => {
    setIsUploading(true);
    setError(null);

    try {
      // Fetch sample data from the backend's sample_data folder
      const response = await fetch("/sample_bofa.csv");
      const blob = await response.blob();
      const file = new File([blob], "sample_bofa.csv", { type: "text/csv" });

      const uploadResponse = await uploadStatement(file);

      if (uploadResponse.success && uploadResponse.statement_id) {
        router.push(`/analyze/${uploadResponse.statement_id}`);
      } else {
        setError(uploadResponse.error || "Failed to load sample data.");
      }
    } catch (err) {
      // If fetching sample file fails, show helpful message
      setError(
        "Sample data not available. Please upload your own CSV file."
      );
    } finally {
      setIsUploading(false);
    }
  };

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

          <div className="text-center mt-6">
            <Button
              variant="outline"
              onClick={handleSampleData}
              disabled={isUploading}
            >
              Try with sample data
            </Button>
          </div>
        </div>

        <div className="w-full border-t border-border-subtle pt-12 mt-8">
          <FeatureCards />
        </div>
      </main>
    </div>
  );
}

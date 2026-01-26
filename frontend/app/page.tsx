"use client";

import { useRouter } from "next/navigation";
import UploadZone from "@/components/landing/upload-zone";
import FeatureCards from "@/components/landing/feature-cards";
import SampleDataButton from "@/components/landing/sample-data-button";

export default function Home() {
  const router = useRouter();

  const handleFileSelect = (file: File) => {
    // TODO: Upload file and navigate to processing page
    console.log("File selected:", file.name);
    router.push("/analyze/processing");
  };

  const handleSampleData = () => {
    // TODO: Load sample data and navigate to processing
    router.push("/analyze/processing");
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] px-4 py-16">
      <div className="text-center mb-12 space-y-4 animate-fade-in">
        <h1 className="text-5xl md:text-6xl font-bold text-text-primary">
          Where does your money
          <br />
          actually go?
        </h1>
        <p className="text-xl text-text-secondary max-w-2xl mx-auto">
          Upload your bank statement and get AI-powered insights in seconds.
        </p>
      </div>

      <div className="w-full max-w-2xl mb-8">
        <UploadZone onFileSelect={handleFileSelect} />
        <SampleDataButton onClick={handleSampleData} />
      </div>

      <FeatureCards />
    </div>
  );
}


"use client";

import { useCallback, useState } from "react";
import { Upload, FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
}

export default function UploadZone({ onFileSelect }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) {
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={cn(
          "relative border-2 border-dashed rounded-xl p-12 transition-all cursor-pointer",
          isDragging
            ? "border-accent-orange bg-bg-card scale-[1.01]"
            : "border-border-accent hover:border-accent-orange hover:bg-bg-card"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileInput}
        />
        <label
          htmlFor="file-upload"
          className="flex flex-col items-center justify-center space-y-4 cursor-pointer"
        >
          <div className="rounded-full bg-bg-card p-4">
            <Upload className="h-8 w-8 text-accent-orange" />
          </div>
          <div className="text-center space-y-2">
            <p className="text-lg font-medium text-text-primary">
              Drag & drop your statement here
            </p>
            <p className="text-text-secondary">────── or ──────</p>
            <Button variant="outline" type="button" className="mt-4">
              Browse Files
            </Button>
          </div>
        </label>
      </div>
      <div className="mt-4 text-center text-sm text-text-muted">
        <p>CSV • Bank of America • Discover Card</p>
      </div>
    </div>
  );
}


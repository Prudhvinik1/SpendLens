"use client";

import React, { useCallback, useState } from "react";
import { Upload, FileText, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  isUploading: boolean;
  error?: string | null;
}

export function UploadZone({ onFileSelect, isUploading, error }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

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
      if (file && file.name.endsWith(".csv")) {
        setSelectedFile(file);
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        setSelectedFile(file);
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  return (
    <div className="w-full max-w-xl mx-auto">
      <div
        className={cn(
          "upload-zone relative border-2 border-dashed rounded-card p-12 text-center transition-all cursor-pointer",
          isDragging
            ? "border-accent-orange bg-accent-orange/5 scale-[1.01]"
            : "border-border-subtle hover:border-accent-orange/50",
          isUploading && "opacity-50 pointer-events-none"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => document.getElementById("file-input")?.click()}
      >
        <input
          id="file-input"
          type="file"
          accept=".csv"
          className="hidden"
          onChange={handleFileInput}
          disabled={isUploading}
        />

        <div className="flex flex-col items-center gap-4">
          {selectedFile ? (
            <>
              <div className="w-16 h-16 rounded-full bg-accent-orange/10 flex items-center justify-center">
                <FileText className="w-8 h-8 text-accent-orange" />
              </div>
              <div>
                <p className="text-text-primary font-medium">{selectedFile.name}</p>
                <p className="text-text-muted text-sm mt-1">
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </p>
              </div>
            </>
          ) : (
            <>
              <div className="w-16 h-16 rounded-full bg-bg-card-hover flex items-center justify-center">
                <Upload className="w-8 h-8 text-accent-orange" />
              </div>
              <div>
                <p className="text-text-primary font-medium">
                  Drag & drop your statement here
                </p>
                <p className="text-text-muted text-sm mt-2">
                  ─────── or ───────
                </p>
              </div>
              <button
                type="button"
                className="px-4 py-2 bg-bg-card-hover border border-border-subtle rounded-lg text-text-primary text-sm hover:border-accent-orange/30 transition-colors"
              >
                Browse Files
              </button>
              <p className="text-text-muted text-xs mt-2">
                CSV • Bank of America • Discover Card
              </p>
            </>
          )}
        </div>

        {isUploading && (
          <div className="absolute inset-0 flex items-center justify-center bg-bg-primary/80 rounded-card">
            <div className="flex items-center gap-3">
              <div className="w-5 h-5 border-2 border-accent-orange border-t-transparent rounded-full animate-spin" />
              <span className="text-text-primary">Uploading...</span>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-4 bg-accent-red/10 border border-accent-red/20 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-accent-red flex-shrink-0 mt-0.5" />
          <p className="text-accent-red text-sm">{error}</p>
        </div>
      )}
    </div>
  );
}

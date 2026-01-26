"use client";

import { Button } from "@/components/ui/button";
import { FileText } from "lucide-react";

interface SampleDataButtonProps {
  onClick: () => void;
}

export default function SampleDataButton({ onClick }: SampleDataButtonProps) {
  return (
    <Button
      variant="outline"
      onClick={onClick}
      className="w-full max-w-md mx-auto mt-6"
    >
      <FileText className="h-4 w-4 mr-2" />
      Try with sample data
    </Button>
  );
}


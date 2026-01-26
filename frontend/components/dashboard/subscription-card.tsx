"use client";

import { Card, CardContent } from "@/components/ui/card";

interface SubscriptionCardProps {
  name: string;
  amount: number;
  lastDate: string;
  icon?: string;
}

export default function SubscriptionCard({
  name,
  amount,
  lastDate,
}: SubscriptionCardProps) {
  return (
    <Card className="min-w-[200px]">
      <CardContent className="pt-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-full bg-bg-secondary mx-auto mb-3 flex items-center justify-center">
            <span className="text-xl">{name[0]}</span>
          </div>
          <h4 className="font-semibold">{name}</h4>
          <p className="text-accent-orange font-semibold tabular-nums">
            ${amount.toFixed(2)}/mo
          </p>
          <p className="text-xs text-text-muted">Last: {lastDate}</p>
        </div>
      </CardContent>
    </Card>
  );
}


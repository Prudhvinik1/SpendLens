"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import SubscriptionCard from "./subscription-card";

interface Subscription {
  name: string;
  amount: number;
  lastDate: string;
}

interface SubscriptionListProps {
  subscriptions: Subscription[];
}

export default function SubscriptionList({
  subscriptions,
}: SubscriptionListProps) {
  const total = subscriptions.reduce((sum, sub) => sum + sub.amount, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>📋 SUBSCRIPTIONS DETECTED</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex gap-4 overflow-x-auto pb-4 md:grid md:grid-cols-4">
          {subscriptions.map((sub, index) => (
            <SubscriptionCard key={index} {...sub} />
          ))}
        </div>
        <div className="mt-4 pt-4 border-t border-border-subtle">
          <p className="text-sm text-text-secondary">
            Total: <span className="text-accent-orange font-semibold tabular-nums">${total.toFixed(2)}/month</span>
          </p>
        </div>
      </CardContent>
    </Card>
  );
}


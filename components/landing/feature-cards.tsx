import { Lock, Zap, Target } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

export default function FeatureCards() {
  const features = [
    {
      icon: Lock,
      title: "Private",
      description: "Your data never stored",
    },
    {
      icon: Zap,
      title: "Instant",
      description: "Analysis in under 30s",
    },
    {
      icon: Target,
      title: "Actionable",
      description: "Get real insights",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto mt-16">
      {features.map((feature) => {
        const Icon = feature.icon;
        return (
          <Card key={feature.title} className="text-center">
            <CardContent className="pt-6">
              <div className="flex justify-center mb-4">
                <div className="rounded-full bg-bg-secondary p-3">
                  <Icon className="h-6 w-6 text-accent-orange" />
                </div>
              </div>
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-sm text-text-secondary">{feature.description}</p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}


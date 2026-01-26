import { Shield, Zap, Target } from "lucide-react";

const features = [
  {
    icon: Shield,
    title: "Private",
    description: "Your data never stored on our servers",
  },
  {
    icon: Zap,
    title: "Instant",
    description: "Analysis in under 30 seconds",
  },
  {
    icon: Target,
    title: "Actionable",
    description: "Get real, specific insights",
  },
];

export function FeatureCards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto">
      {features.map((feature) => (
        <div
          key={feature.title}
          className="flex flex-col items-center text-center p-6 rounded-card bg-bg-card/50 border border-border-subtle"
        >
          <feature.icon className="w-8 h-8 text-accent-orange mb-3" />
          <h3 className="text-text-primary font-medium">{feature.title}</h3>
          <p className="text-text-muted text-sm mt-1">{feature.description}</p>
        </div>
      ))}
    </div>
  );
}

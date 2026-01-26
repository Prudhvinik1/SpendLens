import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(Math.abs(amount));
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
  }).format(date);
}

export function formatDateLong(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

export function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`;
}

export const categoryColors: Record<string, string> = {
  housing: "#6366f1",
  utilities: "#8b5cf6",
  groceries: "#22c55e",
  dining: "#f97316",
  transportation: "#3b82f6",
  shopping: "#ec4899",
  entertainment: "#a855f7",
  health: "#ef4444",
  personal_care: "#f472b6",
  subscriptions: "#14b8a6",
  travel: "#06b6d4",
  education: "#eab308",
  financial: "#64748b",
  income: "#10b981",
  other: "#71717a",
};

export function getCategoryColor(category: string): string {
  return categoryColors[category.toLowerCase()] || categoryColors.other;
}

export function getCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    housing: "Housing",
    utilities: "Utilities",
    groceries: "Groceries",
    dining: "Dining",
    transportation: "Transportation",
    shopping: "Shopping",
    entertainment: "Entertainment",
    health: "Health",
    personal_care: "Personal Care",
    subscriptions: "Subscriptions",
    travel: "Travel",
    education: "Education",
    financial: "Financial",
    income: "Income",
    other: "Other",
  };
  return labels[category.toLowerCase()] || category;
}

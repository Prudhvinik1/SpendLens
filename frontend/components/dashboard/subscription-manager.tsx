"use client";

import { useState, useEffect } from "react";
import { formatCurrency } from "@/lib/utils";
import {
  RefreshCw,
  Trash2,
  CheckCircle,
  Circle,
  Plus,
  Calendar,
  DollarSign,
  TrendingDown,
  AlertTriangle
} from "lucide-react";
import { Transaction } from "@/lib/api";
import { Button } from "@/components/ui/button";

interface SubscriptionTodo {
  id: string;
  subscriptionName: string;
  action: string;
  dueDate?: string;
  completed: boolean;
  createdAt: string;
}

interface SubscriptionWithMetrics extends Transaction {
  dailyCost: number;
  monthlyCost: number;
  yearlyCost: number;
}

interface SubscriptionManagerProps {
  transactions: Transaction[];
  statementId: number;
}

export function SubscriptionManager({ transactions, statementId }: SubscriptionManagerProps) {
  const [todos, setTodos] = useState<SubscriptionTodo[]>([]);
  const [newTodoSubscription, setNewTodoSubscription] = useState<string>("");
  const [newTodoAction, setNewTodoAction] = useState<string>("");
  const [showAddTodo, setShowAddTodo] = useState(false);

  // Load todos from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(`spendlens-todos-${statementId}`);
    if (stored) {
      setTodos(JSON.parse(stored));
    }
  }, [statementId]);

  // Save todos to localStorage
  useEffect(() => {
    localStorage.setItem(`spendlens-todos-${statementId}`, JSON.stringify(todos));
  }, [todos, statementId]);

  // Get subscriptions and calculate metrics
  const subscriptions: SubscriptionWithMetrics[] = transactions
    .filter((t) => t.is_recurring && t.amount < 0)
    .map((t) => ({
      ...t,
      monthlyCost: Math.abs(t.amount),
      dailyCost: Math.abs(t.amount) / 30,
      yearlyCost: Math.abs(t.amount) * 12,
    }))
    .sort((a, b) => b.monthlyCost - a.monthlyCost);

  const totalMonthly = subscriptions.reduce((sum, s) => sum + s.monthlyCost, 0);
  const totalDaily = subscriptions.reduce((sum, s) => sum + s.dailyCost, 0);
  const totalYearly = subscriptions.reduce((sum, s) => sum + s.yearlyCost, 0);

  const addTodo = () => {
    if (!newTodoSubscription || !newTodoAction) return;

    const todo: SubscriptionTodo = {
      id: Date.now().toString(),
      subscriptionName: newTodoSubscription,
      action: newTodoAction,
      completed: false,
      createdAt: new Date().toISOString(),
    };

    setTodos([...todos, todo]);
    setNewTodoSubscription("");
    setNewTodoAction("");
    setShowAddTodo(false);
  };

  const toggleTodo = (id: string) => {
    setTodos(
      todos.map((todo) =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      )
    );
  };

  const deleteTodo = (id: string) => {
    setTodos(todos.filter((todo) => todo.id !== id));
  };

  const quickAddCancelReminder = (subscriptionName: string) => {
    const todo: SubscriptionTodo = {
      id: Date.now().toString(),
      subscriptionName,
      action: "Cancel subscription",
      completed: false,
      createdAt: new Date().toISOString(),
    };
    setTodos([...todos, todo]);
  };

  if (subscriptions.length === 0) {
    return (
      <div className="rounded-card bg-bg-card border border-border-subtle p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-2">
          Subscription Manager
        </h3>
        <p className="text-text-secondary">
          No recurring subscriptions detected in this statement.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-card bg-gradient-to-br from-accent-orange/10 to-bg-card border border-accent-orange/20 p-5">
          <div className="flex items-center gap-2 text-accent-orange mb-2">
            <DollarSign className="w-5 h-5" />
            <span className="text-xs uppercase tracking-wider font-medium">Daily Cost</span>
          </div>
          <p className="text-3xl font-bold text-text-primary tabular-nums">
            {formatCurrency(totalDaily)}
          </p>
          <p className="text-text-muted text-sm mt-1">per day on subscriptions</p>
        </div>

        <div className="rounded-card bg-bg-card border border-border-subtle p-5">
          <div className="flex items-center gap-2 text-accent-purple mb-2">
            <Calendar className="w-5 h-5" />
            <span className="text-xs uppercase tracking-wider font-medium">Monthly Cost</span>
          </div>
          <p className="text-3xl font-bold text-text-primary tabular-nums">
            {formatCurrency(totalMonthly)}
          </p>
          <p className="text-text-muted text-sm mt-1">{subscriptions.length} active subscriptions</p>
        </div>

        <div className="rounded-card bg-bg-card border border-border-subtle p-5">
          <div className="flex items-center gap-2 text-accent-red mb-2">
            <TrendingDown className="w-5 h-5" />
            <span className="text-xs uppercase tracking-wider font-medium">Yearly Cost</span>
          </div>
          <p className="text-3xl font-bold text-text-primary tabular-nums">
            {formatCurrency(totalYearly)}
          </p>
          <p className="text-text-muted text-sm mt-1">if all continue</p>
        </div>
      </div>

      {/* Subscription List with Daily Breakdown */}
      <div className="rounded-card bg-bg-card border border-border-subtle p-6">
        <h3 className="text-xs font-medium uppercase tracking-wider text-text-muted mb-4 flex items-center gap-2">
          <RefreshCw className="w-4 h-4" />
          All Subscriptions
        </h3>

        <div className="space-y-3">
          {subscriptions.map((sub) => (
            <div
              key={sub.id}
              className="flex items-center gap-4 p-4 rounded-lg bg-bg-secondary border border-border-subtle hover:border-accent-orange/30 transition-colors"
            >
              {/* Subscription Icon */}
              <div className="w-12 h-12 rounded-lg bg-accent-teal/10 flex items-center justify-center flex-shrink-0">
                <RefreshCw className="w-6 h-6 text-accent-teal" />
              </div>

              {/* Subscription Details */}
              <div className="flex-1 min-w-0">
                <h4 className="text-text-primary font-medium truncate">
                  {sub.merchant || sub.description.slice(0, 30)}
                </h4>
                <p className="text-text-muted text-sm">
                  Last charged: {new Date(sub.date).toLocaleDateString()}
                </p>
              </div>

              {/* Cost Breakdown */}
              <div className="text-right flex-shrink-0">
                <p className="text-text-primary font-semibold tabular-nums">
                  {formatCurrency(sub.monthlyCost)}/mo
                </p>
                <p className="text-accent-orange text-sm font-medium tabular-nums">
                  {formatCurrency(sub.dailyCost)}/day
                </p>
              </div>

              {/* Worth It Indicator */}
              <div className="flex-shrink-0 w-24 text-center">
                {sub.dailyCost > 1 ? (
                  <div className="px-2 py-1 rounded bg-accent-orange/10 text-accent-orange text-xs font-medium">
                    ${sub.dailyCost.toFixed(2)}/day
                  </div>
                ) : (
                  <div className="px-2 py-1 rounded bg-accent-teal/10 text-accent-teal text-xs font-medium">
                    ${sub.dailyCost.toFixed(2)}/day
                  </div>
                )}
              </div>

              {/* Quick Cancel Button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => quickAddCancelReminder(sub.merchant || sub.description.slice(0, 20))}
                className="flex-shrink-0 text-text-muted hover:text-accent-red"
                title="Add cancel reminder"
              >
                <AlertTriangle className="w-4 h-4" />
              </Button>
            </div>
          ))}
        </div>

        {/* Daily Cost Perspective */}
        <div className="mt-6 p-4 rounded-lg bg-accent-orange/5 border border-accent-orange/20">
          <p className="text-text-secondary text-sm">
            <span className="text-accent-orange font-semibold">Daily perspective:</span>{" "}
            You spend {formatCurrency(totalDaily)} every day on subscriptions.
            That's like buying {(totalDaily / 5).toFixed(1)} coffees daily,
            or {formatCurrency(totalDaily * 7)} every week.
          </p>
        </div>
      </div>

      {/* Todo List for Cancellations */}
      <div className="rounded-card bg-bg-card border border-border-subtle p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xs font-medium uppercase tracking-wider text-text-muted flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            Subscription Action Items
          </h3>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAddTodo(!showAddTodo)}
          >
            <Plus className="w-4 h-4 mr-1" />
            Add Reminder
          </Button>
        </div>

        {/* Add Todo Form */}
        {showAddTodo && (
          <div className="mb-4 p-4 rounded-lg bg-bg-secondary border border-border-subtle">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
              <div>
                <label className="block text-text-muted text-xs mb-1">Subscription</label>
                <select
                  value={newTodoSubscription}
                  onChange={(e) => setNewTodoSubscription(e.target.value)}
                  className="w-full px-3 py-2 bg-bg-card border border-border-subtle rounded-lg text-text-primary text-sm focus:outline-none focus:border-accent-orange/50"
                >
                  <option value="">Select subscription...</option>
                  {subscriptions.map((sub) => (
                    <option key={sub.id} value={sub.merchant || sub.description.slice(0, 20)}>
                      {sub.merchant || sub.description.slice(0, 20)}
                    </option>
                  ))}
                  <option value="Other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-text-muted text-xs mb-1">Action</label>
                <input
                  type="text"
                  value={newTodoAction}
                  onChange={(e) => setNewTodoAction(e.target.value)}
                  placeholder="e.g., Cancel before renewal"
                  className="w-full px-3 py-2 bg-bg-card border border-border-subtle rounded-lg text-text-primary text-sm placeholder:text-text-muted focus:outline-none focus:border-accent-orange/50"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button size="sm" onClick={addTodo}>
                Add
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setShowAddTodo(false)}>
                Cancel
              </Button>
            </div>
          </div>
        )}

        {/* Todo List */}
        {todos.length === 0 ? (
          <p className="text-text-muted text-sm text-center py-4">
            No reminders yet. Click "Add Reminder" or the ⚠️ button on a subscription to add one.
          </p>
        ) : (
          <div className="space-y-2">
            {todos.map((todo) => (
              <div
                key={todo.id}
                className={`flex items-center gap-3 p-3 rounded-lg border transition-colors ${
                  todo.completed
                    ? "bg-accent-teal/5 border-accent-teal/20"
                    : "bg-bg-secondary border-border-subtle"
                }`}
              >
                <button
                  onClick={() => toggleTodo(todo.id)}
                  className="flex-shrink-0"
                >
                  {todo.completed ? (
                    <CheckCircle className="w-5 h-5 text-accent-teal" />
                  ) : (
                    <Circle className="w-5 h-5 text-text-muted hover:text-accent-orange" />
                  )}
                </button>

                <div className="flex-1 min-w-0">
                  <p
                    className={`text-sm ${
                      todo.completed
                        ? "text-text-muted line-through"
                        : "text-text-primary"
                    }`}
                  >
                    <span className="font-medium">{todo.subscriptionName}:</span>{" "}
                    {todo.action}
                  </p>
                </div>

                <button
                  onClick={() => deleteTodo(todo.id)}
                  className="flex-shrink-0 text-text-muted hover:text-accent-red transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Completed count */}
        {todos.length > 0 && (
          <div className="mt-4 pt-4 border-t border-border-subtle">
            <p className="text-text-muted text-sm">
              {todos.filter((t) => t.completed).length} of {todos.length} completed
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

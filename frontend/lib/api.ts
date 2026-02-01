const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types matching backend schemas
export interface UploadResponse {
  success: boolean;
  message: string;
  statement_id: number | null;
  error: string | null;
}

export interface StatementStatus {
  id: number;
  status: string;
  error_message: string | null;
  total_transactions: number;
}

export interface Transaction {
  id: number;
  statement_id: number;
  date: string;
  description: string;
  merchant: string | null;
  amount: number;
  category: string;
  category_confidence: number;
  needs_review: boolean;
  is_recurring: boolean;
  is_anomaly: boolean;
  anomaly_reason: string | null;
}

export interface Insight {
  id: number;
  statement_id: number;
  type: string;
  title: string;
  description: string;
  severity: string;
  category: string | null;
  amount: number | null;
  action_suggestion: string | null;
}

export interface SpendingByCategory {
  category: string;
  total: number;
  count: number;
  percentage: number;
}

export interface AnalysisSummary {
  total_transactions: number;
  total_spent: number;
  total_income: number;
  net_change: number;
  period_start: string | null;
  period_end: string | null;
  detected_format: string | null;
}

export interface Statement {
  id: number;
  filename: string;
  original_filename: string;
  upload_date: string;
  period_start: string | null;
  period_end: string | null;
  total_transactions: number;
  total_spent: number;
  total_income: number;
  status: string;
  error_message: string | null;
  detected_format: string | null;
}

export interface FullAnalysisResponse {
  statement: Statement;
  summary: AnalysisSummary;
  spending_by_category: SpendingByCategory[];
  transactions: Transaction[];
  insights: Insight[];
  needs_review_count: number;
}

export interface SupportedFormat {
  name: string;
  id: string;
  columns: string;
}

// API Functions
export async function uploadStatement(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(error.detail || "Upload failed");
  }

  return response.json();
}

export async function getStatus(statementId: number): Promise<StatementStatus> {
  const response = await fetch(`${API_BASE_URL}/api/status/${statementId}`);

  if (!response.ok) {
    throw new Error("Failed to get status");
  }

  return response.json();
}

export async function getAnalysis(statementId: number): Promise<FullAnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/api/analysis/${statementId}`);

  if (!response.ok) {
    if (response.status === 202) {
      throw new Error("Still processing");
    }
    const error = await response.json().catch(() => ({ detail: "Failed to get analysis" }));
    throw new Error(error.detail || "Failed to get analysis");
  }

  return response.json();
}

export async function updateTransaction(
  transactionId: number,
  updates: { category?: string; merchant?: string; is_recurring?: boolean }
): Promise<Transaction> {
  const response = await fetch(`${API_BASE_URL}/api/transactions/${transactionId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(updates),
  });

  if (!response.ok) {
    throw new Error("Failed to update transaction");
  }

  return response.json();
}

export async function getCategories(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/api/categories`);

  if (!response.ok) {
    throw new Error("Failed to get categories");
  }

  const data = await response.json();
  return data.categories;
}

export async function getSupportedFormats(): Promise<SupportedFormat[]> {
  const response = await fetch(`${API_BASE_URL}/api/formats`);

  if (!response.ok) {
    throw new Error("Failed to get formats");
  }

  const data = await response.json();
  return data.formats;
}

export interface SampleData {
  name: string;
  filename: string;
  id: string;
}

export async function getSampleData(): Promise<SampleData[]> {
  const response = await fetch(`${API_BASE_URL}/api/sample-data`);

  if (!response.ok) {
    throw new Error("Failed to get sample data");
  }

  const data = await response.json();
  return data.samples;
}

export async function processDemoData(sampleId: string): Promise<UploadResponse> {
  const response = await fetch(`${API_BASE_URL}/api/demo/${sampleId}`, {
    method: "POST",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Demo processing failed" }));
    throw new Error(error.detail || "Demo processing failed");
  }

  return response.json();
}

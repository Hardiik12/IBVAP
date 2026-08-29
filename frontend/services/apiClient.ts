const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

export async function fetchApi<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { timeoutMs = 8000, ...fetchOptions } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  // Automatically attach auth token if present
  let authHeader: Record<string, string> = {};
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("ibvap_access_token");
    if (token) {
      authHeader["Authorization"] = `Bearer ${token}`;
    }
  }

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...authHeader,
        ...fetchOptions.headers,
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: response.statusText };
      }
      throw new ApiError(
        errorData?.detail?.message || errorData?.detail || `API Error: ${response.status}`,
        response.status,
        errorData
      );
    }

    return (await response.json()) as T;
  } catch (error: any) {
    clearTimeout(timeoutId);
    throw error;
  }
}

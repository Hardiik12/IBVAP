/**
 * IBVAP Centralized Authenticated REST Client
 * Automatically normalizes API base path to /api/v1 and injects Bearer JWT.
 */

const getApiBaseUrl = (): string => {
  let base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  if (base.endsWith("/")) base = base.slice(0, -1);
  if (!base.endsWith("/api/v1")) {
    base = `${base}/api/v1`;
  }
  return base;
};

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

export interface RequestOptions extends RequestInit {
  timeoutMs?: number;
  skipAuth?: boolean;
}

export async function fetchApi<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { timeoutMs = 8000, skipAuth = false, ...fetchOptions } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const base = getApiBaseUrl();
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${base}${cleanEndpoint}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
    ...(fetchOptions.headers as Record<string, string>),
  };

  // Inject JWT Bearer Token if available and not skipped
  if (!skipAuth && typeof window !== "undefined") {
    const token = localStorage.getItem("ibvap_token") || localStorage.getItem("ibvap_access_token");
    if (token && !headers["Authorization"]) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorData: any;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: response.statusText };
      }

      // Handle 401 Unauthorized globally
      if (response.status === 401 && typeof window !== "undefined") {
        const isLoginReq = cleanEndpoint.includes("/auth/login") || cleanEndpoint.includes("/auth/mfa");
        if (!isLoginReq) {
          localStorage.removeItem("ibvap_token");
          localStorage.removeItem("ibvap_access_token");
          localStorage.removeItem("ibvap_user");
          if (!window.location.pathname.startsWith("/login") && !window.location.pathname.startsWith("/mfa")) {
            window.location.href = "/login";
          }
        }
      }

      const errorMessage =
        errorData?.error?.message ||
        errorData?.detail?.message ||
        errorData?.detail ||
        `HTTP ${response.status}: ${response.statusText}`;

      throw new ApiError(errorMessage, response.status, errorData);
    }

    // Return empty object on 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return (await response.json()) as T;
  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error.name === "AbortError") {
      throw new ApiError("Request timed out", 408);
    }
    throw error;
  }
}

export const apiClient = {
  get: async <T>(endpoint: string, config?: { params?: Record<string, any> }): Promise<{ data: T }> => {
    let finalUrl = endpoint;
    if (config?.params) {
      const searchParams = new URLSearchParams();
      Object.entries(config.params).forEach(([key, val]) => {
        if (val !== undefined && val !== null) {
          searchParams.append(key, String(val));
        }
      });
      const qs = searchParams.toString();
      if (qs) finalUrl += (finalUrl.includes("?") ? "&" : "?") + qs;
    }
    const data = await fetchApi<T>(finalUrl, { method: "GET" });
    return { data };
  },

  post: async <T>(endpoint: string, body?: any): Promise<{ data: T }> => {
    const data = await fetchApi<T>(endpoint, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
    return { data };
  },

  patch: async <T>(endpoint: string, body?: any): Promise<{ data: T }> => {
    const data = await fetchApi<T>(endpoint, {
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    });
    return { data };
  },

  delete: async <T>(endpoint: string): Promise<{ data: T }> => {
    const data = await fetchApi<T>(endpoint, { method: "DELETE" });
    return { data };
  },
};

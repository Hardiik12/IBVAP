import { LoginResponse, MfaSetupResponse, TokenResponse, User } from "@/types/auth";

const TOKEN_KEY = "ibvap_access_token";
const MFA_PENDING_KEY = "ibvap_mfa_pending";

export const authService = {
  getStoredToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(TOKEN_KEY);
  },

  setStoredToken(token: string): void {
    if (typeof window === "undefined") return;
    localStorage.setItem(TOKEN_KEY, token);
  },

  removeStoredToken(): void {
    if (typeof window === "undefined") return;
    localStorage.removeItem(TOKEN_KEY);
  },

  getStoredMfaPending(): { mfaToken: string; mfaSetupRequired: boolean; username: string } | null {
    if (typeof window === "undefined") return null;
    const raw = sessionStorage.getItem(MFA_PENDING_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  },

  setStoredMfaPending(data: { mfaToken: string; mfaSetupRequired: boolean; username: string }): void {
    if (typeof window === "undefined") return;
    sessionStorage.setItem(MFA_PENDING_KEY, JSON.stringify(data));
  },

  clearStoredMfaPending(): void {
    if (typeof window === "undefined") return;
    sessionStorage.removeItem(MFA_PENDING_KEY);
  },

  async login(usernameOrEmail: string, password: string): Promise<LoginResponse> {
    const res = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username_or_email: usernameOrEmail, password }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const message = err?.detail || err?.error?.message || "ACCESS DENIED: Invalid operator credentials.";
      throw new Error(message);
    }

    const data: LoginResponse = await res.json();
    this.setStoredMfaPending({
      mfaToken: data.mfa_token,
      mfaSetupRequired: data.mfa_setup_required,
      username: data.username,
    });
    return data;
  },

  async getMfaSetup(mfaToken: string): Promise<MfaSetupResponse> {
    const res = await fetch(`/api/v1/auth/mfa/setup?mfa_token=${encodeURIComponent(mfaToken)}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err?.detail || err?.error?.message || "Failed to load MFA setup QR code.");
    }
    return res.json();
  },

  async enableMfa(mfaToken: string, secret: string, code: string): Promise<TokenResponse> {
    const res = await fetch("/api/v1/auth/mfa/enable", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mfa_token: mfaToken, secret, code }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err?.detail || err?.error?.message || "Invalid 6-digit code. Please verify and try again.");
    }

    const data: TokenResponse = await res.json();
    this.setStoredToken(data.access_token);
    this.clearStoredMfaPending();
    return data;
  },

  async verifyMfa(mfaToken: string, code: string): Promise<TokenResponse> {
    const res = await fetch("/api/v1/auth/mfa/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mfa_token: mfaToken, code }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err?.detail || err?.error?.message || "MFA VERIFICATION FAILED: Code is invalid or expired.");
    }

    const data: TokenResponse = await res.json();
    this.setStoredToken(data.access_token);
    this.clearStoredMfaPending();
    return data;
  },

  async getCurrentUser(): Promise<User> {
    const token = this.getStoredToken();
    if (!token) {
      throw new Error("No authentication token found.");
    }

    const res = await fetch("/api/v1/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) {
      this.removeStoredToken();
      throw new Error("Session expired or invalid.");
    }

    return res.json();
  },

  async logout(): Promise<void> {
    const token = this.getStoredToken();
    if (token) {
      try {
        await fetch("/api/v1/auth/logout", {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch (err) {
        console.warn("Logout request failed:", err);
      }
    }
    this.removeStoredToken();
    this.clearStoredMfaPending();
  },
};

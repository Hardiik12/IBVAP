import { apiClient } from "./apiClient";
import {
  LoginResponse,
  FaceVerificationResponse,
  FaceEnrollmentResponse,
  MfaSetupResponse,
  MfaVerifyResponse,
  TokenResponse,
  CurrentUser,
} from "@/types/auth";

const TOKEN_KEY = "ibvap_access_token";
const TEMP_TOKEN_KEY = "ibvap_temp_token";
const MFA_TOKEN_KEY = "ibvap_mfa_token";
const FACE_TOKEN_KEY = "ibvap_face_token";
const USER_KEY = "ibvap_current_user";

export const authService = {
  getStoredToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(TOKEN_KEY) || localStorage.getItem("ibvap_token");
  },

  getToken(): string | null {
    return this.getStoredToken();
  },

  setStoredToken(token: string): void {
    if (typeof window === "undefined") return;
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem("ibvap_token", token);
  },

  removeStoredToken(): void {
    if (typeof window === "undefined") return;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem("ibvap_token");
  },

  isAuthenticated(): boolean {
    return !!this.getToken();
  },

  getStoredTempToken(): string | null {
    if (typeof window === "undefined") return null;
    return sessionStorage.getItem(TEMP_TOKEN_KEY);
  },

  getStoredMfaToken(): string | null {
    if (typeof window === "undefined") return null;
    return sessionStorage.getItem(MFA_TOKEN_KEY) || sessionStorage.getItem(TEMP_TOKEN_KEY);
  },

  getStoredFaceToken(): string | null {
    if (typeof window === "undefined") return null;
    return sessionStorage.getItem(FACE_TOKEN_KEY) || sessionStorage.getItem(MFA_TOKEN_KEY) || sessionStorage.getItem(TEMP_TOKEN_KEY);
  },

  setStoredTokens(tokens: { accessToken?: string; tempToken?: string; mfaToken?: string; faceToken?: string }) {
    if (typeof window === "undefined") return;
    if (tokens.accessToken) localStorage.setItem(TOKEN_KEY, tokens.accessToken);
    if (tokens.tempToken) sessionStorage.setItem(TEMP_TOKEN_KEY, tokens.tempToken);
    if (tokens.mfaToken) sessionStorage.setItem(MFA_TOKEN_KEY, tokens.mfaToken);
    if (tokens.faceToken) sessionStorage.setItem(FACE_TOKEN_KEY, tokens.faceToken);
  },

  getStoredUser(): CurrentUser | null {
    if (typeof window === "undefined") return null;
    const data = localStorage.getItem(USER_KEY);
    if (!data) return null;
    try {
      return JSON.parse(data);
    } catch {
      return null;
    }
  },

  setStoredUser(user: CurrentUser) {
    if (typeof window === "undefined") return;
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  clearAllAuth() {
    if (typeof window === "undefined") return;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    sessionStorage.removeItem(TEMP_TOKEN_KEY);
    sessionStorage.removeItem(MFA_TOKEN_KEY);
    sessionStorage.removeItem(FACE_TOKEN_KEY);
  },

  // Step 1: Password Login
  async login(username_or_email: string, password: string): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>("/auth/login", {
      username_or_email,
      password,
    });
    this.setStoredTokens({
      tempToken: response.data.temp_token,
      mfaToken: response.data.temp_token,
    });
    return response.data;
  },

  // Step 2: MFA Setup (Get TOTP Secret & QR Code)
  async getMfaSetup(mfa_token: string): Promise<MfaSetupResponse> {
    const response = await apiClient.get<MfaSetupResponse>("/auth/mfa/setup", {
      params: { mfa_token },
    });
    return response.data;
  },

  // Step 2: MFA Activation (Initial Code)
  async enableMfa(mfa_token: string, secret: string, code: string): Promise<MfaVerifyResponse> {
    const response = await apiClient.post<MfaVerifyResponse>("/auth/mfa/enable", {
      mfa_token,
      secret,
      code,
    });
    const faceToken = response.data.face_token || response.data.access_token;
    if (faceToken) {
      this.setStoredTokens({ faceToken });
    }
    if (response.data.user) {
      this.setStoredUser(response.data.user);
    }
    return response.data;
  },

  // Step 2: MFA Verification (Rotating 6-Digit Code)
  async verifyMfa(mfa_token: string, code: string): Promise<MfaVerifyResponse> {
    const response = await apiClient.post<MfaVerifyResponse>("/auth/mfa/verify", {
      mfa_token,
      code,
    });
    const faceToken = response.data.face_token || response.data.access_token;
    if (faceToken) {
      this.setStoredTokens({ faceToken });
    }
    if (response.data.user) {
      this.setStoredUser(response.data.user);
    }
    return response.data;
  },

  // Step 3: Face Biometric Verification (Webcam Frame)
  async verifyFace(
    temp_token: string,
    image: string,
    liveness_completed: boolean = true
  ): Promise<FaceVerificationResponse> {
    const response = await apiClient.post<FaceVerificationResponse>("/auth/face/verify", {
      temp_token,
      image,
      liveness_completed,
    });
    if (response.data.access_token) {
      this.setStoredTokens({ accessToken: response.data.access_token });
      if (response.data.user) {
        this.setStoredUser(response.data.user);
      }
      sessionStorage.removeItem(TEMP_TOKEN_KEY);
      sessionStorage.removeItem(MFA_TOKEN_KEY);
      sessionStorage.removeItem(FACE_TOKEN_KEY);
    }
    return response.data;
  },

  // Biometric Face Enrollment
  async enrollFace(
    temp_token: string,
    images: string[]
  ): Promise<FaceEnrollmentResponse> {
    const response = await apiClient.post<FaceEnrollmentResponse>("/auth/face/enroll", {
      temp_token,
      images,
    });
    if (response.data.access_token) {
      this.setStoredTokens({ accessToken: response.data.access_token });
      if (response.data.user) {
        this.setStoredUser(response.data.user);
      }
      sessionStorage.removeItem(TEMP_TOKEN_KEY);
      sessionStorage.removeItem(MFA_TOKEN_KEY);
      sessionStorage.removeItem(FACE_TOKEN_KEY);
    }
    return response.data;
  },

  // Current Operator Profile
  async getMe(): Promise<CurrentUser> {
    const response = await apiClient.get<CurrentUser>("/auth/me");
    this.setStoredUser(response.data);
    return response.data;
  },

  // Session Termination
  async logout(): Promise<void> {
    try {
      await apiClient.post("/auth/logout");
    } catch {
      // Ignore network errors on logout
    } finally {
      this.clearAllAuth();
    }
  },
};

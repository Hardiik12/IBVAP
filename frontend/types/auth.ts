export type UserRole = "ADMINISTRATOR" | "OPERATOR" | "ANALYST" | "AUDITOR";

export interface User {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  mfa_enabled: boolean;
  is_active: boolean;
  created_at: string;
  updated_at?: string | null;
}

export type AuthState = "LOADING" | "UNAUTHENTICATED" | "MFA_PENDING" | "AUTHENTICATED";

export interface LoginResponse {
  mfa_required: boolean;
  mfa_setup_required: boolean;
  mfa_token: string;
  temp_token_expires_in: number;
  username: string;
  role: UserRole;
}

export interface MfaSetupResponse {
  secret: string;
  qr_code_base64: string;
  provisioning_uri: string;
  username: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface MfaPendingState {
  mfaToken: string;
  mfaSetupRequired: boolean;
  username: string;
  role: UserRole;
}

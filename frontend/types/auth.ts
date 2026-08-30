export type UserRole = "ADMINISTRATOR" | "OPERATOR" | "ANALYST" | "AUDITOR";

export type AuthState =
  | "UNAUTHENTICATED"
  | "PASSWORD_VERIFIED"
  | "MFA_PENDING"
  | "FACE_VERIFICATION_PENDING"
  | "AUTHENTICATED";

export interface CurrentUser {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  mfa_enabled: boolean;
  face_enrolled: boolean;
  face_enrolled_at?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at?: string | null;
}

export interface LoginResponse {
  face_verification_required: boolean;
  face_enrolled: boolean;
  temp_token: string;
  temp_token_expires_in: number;
  username: string;
  role: UserRole;
  mfa_required: boolean;
  mfa_setup_required: boolean;
  mfa_token?: string;
}

export interface FaceVerificationRequest {
  temp_token: string;
  image: string; // Base64 JPEG data URL
  liveness_completed?: boolean;
}

export interface FaceVerificationResponse {
  verified?: boolean;
  access_token?: string;
  token_type?: string;
  expires_in?: number;
  user?: CurrentUser;
  mfa_token?: string;
  mfa_required?: boolean;
  mfa_setup_required?: boolean;
  username?: string;
  role?: UserRole;
}

export interface FaceEnrollmentRequest {
  temp_token: string;
  images: string[];
}

export interface FaceEnrollmentResponse {
  enrolled: boolean;
  samples_processed: number;
  message: string;
  mfa_token?: string;
  face_token?: string;
  access_token?: string;
  username?: string;
  user?: CurrentUser;
}

export interface MfaSetupResponse {
  secret: string;
  qr_code_base64: string;
  provisioning_uri: string;
  username: string;
  current_code?: string;
}

export interface MfaVerifyResponse {
  face_token?: string;
  face_verification_required?: boolean;
  access_token?: string;
  token_type?: string;
  expires_in?: number;
  user?: CurrentUser;
  message?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: CurrentUser;
}

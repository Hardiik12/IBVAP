"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter, usePathname } from "next/navigation";
import { AuthState, CurrentUser } from "@/types/auth";
import { authService } from "@/services/authService";

interface AuthContextType {
  authState: AuthState;
  user: CurrentUser | null;
  tempToken: string | null;
  mfaToken: string | null;
  faceToken: string | null;
  pendingUsername: string | null;
  isMfaSetupRequired: boolean;
  isFaceEnrolled: boolean;
  isLoading: boolean;
  login: (usernameOrEmail: string, password: string) => Promise<void>;
  verifyMfa: (code: string) => Promise<void>;
  enableMfa: (secret: string, code: string) => Promise<void>;
  verifyFace: (imageBase64: string, livenessCompleted?: boolean) => Promise<void>;
  enrollFace: (imagesBase64: string[]) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  hasRole: (allowedRoles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>("UNAUTHENTICATED");
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [tempToken, setTempToken] = useState<string | null>(null);
  const [mfaToken, setMfaToken] = useState<string | null>(null);
  const [faceToken, setFaceToken] = useState<string | null>(null);
  const [pendingUsername, setPendingUsername] = useState<string | null>(null);
  const [isMfaSetupRequired, setIsMfaSetupRequired] = useState<boolean>(false);
  const [isFaceEnrolled, setIsFaceEnrolled] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const router = useRouter();
  const pathname = usePathname();

  // Restore existing session on initial mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedToken = authService.getStoredToken();
        const storedUser = authService.getStoredUser();

        if (storedToken && storedUser) {
          setUser(storedUser);
          setIsFaceEnrolled(storedUser.face_enrolled || false);
          setAuthState("AUTHENTICATED");
          try {
            const refreshedUser = await authService.getMe();
            setUser(refreshedUser);
            setIsFaceEnrolled(refreshedUser.face_enrolled || false);
          } catch {
            authService.clearAllAuth();
            setUser(null);
            setAuthState("UNAUTHENTICATED");
          }
        } else {
          const storedFace = authService.getStoredFaceToken();
          const storedMfa = authService.getStoredMfaToken();
          const storedTemp = authService.getStoredTempToken();

          if (storedFace) {
            setFaceToken(storedFace);
            setAuthState("FACE_VERIFICATION_PENDING");
          } else if (storedMfa || storedTemp) {
            setMfaToken(storedMfa || storedTemp);
            setAuthState("MFA_PENDING");
          } else {
            setAuthState("UNAUTHENTICATED");
          }
        }
      } catch (e) {
        console.error("Auth init error:", e);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Step 1: Login (Username + Password) ➔ Advances to Step 2 (MFA)
  const login = async (usernameOrEmail: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await authService.login(usernameOrEmail, password);
      setTempToken(response.temp_token);
      setMfaToken(response.temp_token);
      setPendingUsername(response.username);
      setIsFaceEnrolled(response.face_enrolled || false);
      setIsMfaSetupRequired(response.mfa_setup_required);
      setAuthState("MFA_PENDING");

      if (response.mfa_setup_required) {
        router.push("/mfa/setup");
      } else {
        router.push("/mfa");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Step 2: MFA Verification ➔ Advances to Step 3 (Enrollment if first-time, Verification if returning)
  const verifyMfa = async (code: string) => {
    const token = mfaToken || authService.getStoredMfaToken() || tempToken;
    if (!token) {
      throw new Error("MFA challenge token missing. Please log in again.");
    }

    setIsLoading(true);
    try {
      const response = await authService.verifyMfa(token, code);
      const nextToken = response.face_token || response.access_token || token;
      setFaceToken(nextToken);
      if (response.user) {
        setUser(response.user);
        setIsFaceEnrolled(response.user.face_enrolled || false);
      }

      setAuthState("FACE_VERIFICATION_PENDING");

      const enrolled = response.user ? response.user.face_enrolled : isFaceEnrolled;
      if (!enrolled) {
        router.push("/face-enrollment");
      } else {
        router.push("/face-verification");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Step 2: MFA Activation ➔ Advances to Step 3 (Enrollment if first-time, Verification if returning)
  const enableMfa = async (secret: string, code: string) => {
    const token = mfaToken || authService.getStoredMfaToken() || tempToken;
    if (!token) {
      throw new Error("MFA challenge token missing. Please log in again.");
    }

    setIsLoading(true);
    try {
      const response = await authService.enableMfa(token, secret, code);
      const nextToken = response.face_token || response.access_token || token;
      setFaceToken(nextToken);
      if (response.user) {
        setUser(response.user);
        setIsFaceEnrolled(response.user.face_enrolled || false);
      }

      setAuthState("FACE_VERIFICATION_PENDING");

      const enrolled = response.user ? response.user.face_enrolled : isFaceEnrolled;
      if (!enrolled) {
        router.push("/face-enrollment");
      } else {
        router.push("/face-verification");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Step 3 (Returning User): Face Biometric Verification ➔ Dashboard
  const verifyFace = async (imageBase64: string, livenessCompleted: boolean = true) => {
    const token = faceToken || authService.getStoredFaceToken() || mfaToken || tempToken;
    if (!token) {
      throw new Error("Face verification token missing. Please complete login and MFA first.");
    }

    setIsLoading(true);
    try {
      const response = await authService.verifyFace(token, imageBase64, livenessCompleted);
      if (response.user) {
        setUser(response.user);
      }
      setIsFaceEnrolled(true);
      setAuthState("AUTHENTICATED");
      router.push("/dashboard");
    } finally {
      setIsLoading(false);
    }
  };

  // Step 3 (First-Time User): Face Biometric Enrollment ➔ Dashboard
  const enrollFace = async (imagesBase64: string[]) => {
    const token = faceToken || authService.getStoredFaceToken() || mfaToken || tempToken;
    if (!token) {
      throw new Error("Authentication token missing for biometric enrollment.");
    }

    setIsLoading(true);
    try {
      const response = await authService.enrollFace(token, imagesBase64);
      setIsFaceEnrolled(true);
      if (response.user) {
        setUser(response.user);
      }
      setAuthState("AUTHENTICATED");
      router.push("/dashboard");
    } finally {
      setIsLoading(false);
    }
  };

  // Logout
  const logout = async () => {
    setIsLoading(true);
    try {
      await authService.logout();
    } finally {
      setUser(null);
      setTempToken(null);
      setMfaToken(null);
      setFaceToken(null);
      setIsFaceEnrolled(false);
      setAuthState("UNAUTHENTICATED");
      setIsLoading(false);
      router.push("/login");
    }
  };

  const hasRole = (allowedRoles: string[]) => {
    if (!user) return false;
    return allowedRoles.includes(user.role);
  };

  const refreshUser = async () => {
    try {
      const refreshed = await authService.getMe();
      setUser(refreshed);
    } catch {
      // ignore
    }
  };

  return (
    <AuthContext.Provider
      value={{
        authState,
        user,
        tempToken,
        mfaToken,
        faceToken,
        pendingUsername,
        isMfaSetupRequired,
        isFaceEnrolled,
        isLoading,
        login,
        verifyMfa,
        enableMfa,
        verifyFace,
        enrollFace,
        logout,
        refreshUser,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

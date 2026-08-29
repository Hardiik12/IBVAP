"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { User, AuthState, MfaPendingState, LoginResponse, TokenResponse } from "@/types/auth";
import { authService } from "@/services/authService";

interface AuthContextType {
  user: User | null;
  authState: AuthState;
  mfaData: MfaPendingState | null;
  isLoading: boolean;
  login: (usernameOrEmail: string, password: string) => Promise<LoginResponse>;
  verifyMfa: (code: string) => Promise<TokenResponse>;
  enableMfa: (secret: string, code: string) => Promise<TokenResponse>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [authState, setAuthState] = useState<AuthState>("LOADING");
  const [mfaData, setMfaData] = useState<MfaPendingState | null>(null);

  const refreshUser = useCallback(async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
      setAuthState("AUTHENTICATED");
    } catch {
      setUser(null);
      // Check if there is an in-flight MFA pending state
      const pending = authService.getStoredMfaPending();
      if (pending) {
        setMfaData({
          mfaToken: pending.mfaToken,
          mfaSetupRequired: pending.mfaSetupRequired,
          username: pending.username,
          role: "OPERATOR",
        });
        setAuthState("MFA_PENDING");
      } else {
        setAuthState("UNAUTHENTICATED");
      }
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = async (usernameOrEmail: string, password: string): Promise<LoginResponse> => {
    const res = await authService.login(usernameOrEmail, password);
    const pending: MfaPendingState = {
      mfaToken: res.mfa_token,
      mfaSetupRequired: res.mfa_setup_required,
      username: res.username,
      role: res.role,
    };
    setMfaData(pending);
    setAuthState("MFA_PENDING");
    return res;
  };

  const verifyMfa = async (code: string): Promise<TokenResponse> => {
    if (!mfaData?.mfaToken) {
      throw new Error("No active MFA challenge session found. Please log in again.");
    }
    const res = await authService.verifyMfa(mfaData.mfaToken, code);
    setUser(res.user);
    setMfaData(null);
    setAuthState("AUTHENTICATED");
    return res;
  };

  const enableMfa = async (secret: string, code: string): Promise<TokenResponse> => {
    if (!mfaData?.mfaToken) {
      throw new Error("No active MFA setup session found. Please log in again.");
    }
    const res = await authService.enableMfa(mfaData.mfaToken, secret, code);
    setUser(res.user);
    setMfaData(null);
    setAuthState("AUTHENTICATED");
    return res;
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    setMfaData(null);
    setAuthState("UNAUTHENTICATED");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        authState,
        mfaData,
        isLoading: authState === "LOADING",
        login,
        verifyMfa,
        enableMfa,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

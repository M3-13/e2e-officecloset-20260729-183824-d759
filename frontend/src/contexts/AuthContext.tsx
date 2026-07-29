import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import type { UserResponse } from "../api/client";
import { login as apiLogin, register as apiRegister, getMe, deleteAccount as apiDeleteAccount } from "../api/client";

interface AuthContextType {
  user: UserResponse | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, privacyAccepted: boolean) => Promise<void>;
  logout: () => void;
  deleteAccount: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setLoading(false);
      return;
    }
    getMe()
      .then((u) => {
        setUser(u);
      })
      .catch(() => {
        localStorage.removeItem("token");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const loginFn = useCallback(async (email: string, password: string) => {
    const data = await apiLogin(email, password);
    localStorage.setItem("token", data.access_token);
    const u = await getMe();
    setUser(u);
  }, []);

  const registerFn = useCallback(async (email: string, password: string, privacyAccepted: boolean) => {
    const data = await apiRegister(email, password, privacyAccepted);
    localStorage.setItem("token", data.access_token);
    const u = await getMe();
    setUser(u);
  }, []);

  const logoutFn = useCallback(() => {
    localStorage.removeItem("token");
    setUser(null);
  }, []);

  const deleteAccountFn = useCallback(async () => {
    await apiDeleteAccount();
    localStorage.removeItem("token");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: user !== null,
        login: loginFn,
        register: registerFn,
        logout: logoutFn,
        deleteAccount: deleteAccountFn,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

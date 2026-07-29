import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import type { UserResponse } from "../api/client";

interface AuthContextType {
  user: UserResponse | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user] = useState<UserResponse | null>(null);
  const [loading] = useState(false);

  const isAuthenticated = false;

  const loginFn = useCallback(async (_email: string, _password: string) => {
    throw new Error("Not implemented");
  }, []);

  const registerFn = useCallback(async (_email: string, _password: string) => {
    throw new Error("Not implemented");
  }, []);

  const logoutFn = useCallback(() => {
    localStorage.removeItem("token");
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated,
        login: loginFn,
        register: registerFn,
        logout: logoutFn,
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

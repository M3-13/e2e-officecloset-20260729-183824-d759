import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
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

const TOKEN_KEY = "token";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const isAuthenticated = user !== null;

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setLoading(false);
      return;
    }
    import("../api/client")
      .then((api) =>
        api.getMe().then((u) => setUser(u))
      )
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY);
      })
      .finally(() => setLoading(false));
  }, []);

  const loginFn = useCallback(async (email: string, password: string) => {
    const { login: apiLogin } = await import("../api/client");
    const data = await apiLogin(email, password);
    localStorage.setItem(TOKEN_KEY, data.access_token);
    const { getMe } = await import("../api/client");
    const u = await getMe();
    setUser(u);
  }, []);

  const registerFn = useCallback(async (email: string, password: string) => {
    const { register: apiRegister } = await import("../api/client");
    const data = await apiRegister(email, password);
    localStorage.setItem(TOKEN_KEY, data.access_token);
    const { getMe } = await import("../api/client");
    const u = await getMe();
    setUser(u);
  }, []);

  const logoutFn = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
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

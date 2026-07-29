const API_BASE = import.meta.env.VITE_API_URL || "";

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem("token");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      ...authHeaders(),
      ...(options.headers as Record<string, string> | undefined),
    },
  });
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(errorBody || `Request failed with status ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export interface UserResponse {
  id: number;
  email: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface ClothingItemResponse {
  id: number;
  user_id: number;
  name: string;
  category: string;
  image_path: string;
  note: string | null;
}

export interface OutfitResponse {
  id: number;
  user_id: number;
  name: string;
  items: ClothingItemResponse[];
}

export async function register(
  email: string,
  password: string,
  privacyAccepted: boolean,
): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, privacy_accepted: privacyAccepted }),
  });
}

export async function login(
  email: string,
  password: string
): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function getMe(): Promise<UserResponse> {
  return apiFetch<UserResponse>("/api/auth/me");
}

export async function deleteAccount(): Promise<void> {
  return apiFetch<void>("/api/auth/account", { method: "DELETE" });
}

export async function createItem(formData: FormData): Promise<ClothingItemResponse> {
  const token = localStorage.getItem("token");
  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const url = `${API_BASE}/api/wardrobe/`;
  const response = await fetch(url, { method: "POST", headers, body: formData });
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(errorBody || `Request failed with status ${response.status}`);
  }
  return response.json();
}

export async function listItems(category?: string): Promise<ClothingItemResponse[]> {
  const params = category ? `?category=${encodeURIComponent(category)}` : "";
  return apiFetch<ClothingItemResponse[]>(`/api/wardrobe/${params}`);
}

export async function getItem(id: number): Promise<ClothingItemResponse> {
  return apiFetch<ClothingItemResponse>(`/api/wardrobe/${id}`);
}

export async function updateItem(
  id: number,
  data: { name: string; category: string; note?: string | null }
): Promise<ClothingItemResponse> {
  return apiFetch<ClothingItemResponse>(`/api/wardrobe/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteItem(id: number): Promise<void> {
  return apiFetch<void>(`/api/wardrobe/${id}`, { method: "DELETE" });
}

export async function createOutfit(data: {
  name: string;
  item_ids: number[];
}): Promise<OutfitResponse> {
  return apiFetch<OutfitResponse>("/api/outfits/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function listOutfits(): Promise<OutfitResponse[]> {
  return apiFetch<OutfitResponse[]>("/api/outfits/");
}

export async function getOutfit(id: number): Promise<OutfitResponse> {
  return apiFetch<OutfitResponse>(`/api/outfits/${id}`);
}

export async function updateOutfit(
  id: number,
  data: { name?: string; item_ids?: number[] }
): Promise<OutfitResponse> {
  return apiFetch<OutfitResponse>(`/api/outfits/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteOutfit(id: number): Promise<void> {
  return apiFetch<void>(`/api/outfits/${id}`, { method: "DELETE" });
}

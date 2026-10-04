const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

export type Source = {
  source: number;
  document_id?: string;
  filename?: string;
  page?: number;
  chunk_id?: string;
  distance?: number;
};

export type Workspace = {
  id: string;
  name: string;
  is_pinned?: boolean;
  document_count?: number;
  chat_count?: number;
};

export type Document = {
  id?: string;
  document_id: string;
  workspace_id?: string;
  filename: string;
  total_pages?: number;
  total_chunks?: number;
  status?: string;
  file_size?: number;
  created_at?: string;
};

export type Chat = {
  id: string;
  workspace_id?: string;
  title: string;
  is_pinned?: boolean;
  message_count?: number;
};

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  created_at?: string;
};

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...(init.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      Accept: "application/json",
      ...init.headers,
    },
  });

  const contentType = response.headers.get("content-type") || "";
  const payload =
    response.status === 204
      ? undefined
      : contentType.includes("application/json")
        ? await response.json()
        : await response.text();

  if (!response.ok) {
    const detail =
      typeof payload === "object" && payload !== null && "detail" in payload
        ? String((payload as { detail?: unknown }).detail || "Request failed.")
        : typeof payload === "string" && payload
          ? payload
          : "Request failed.";
    throw new ApiError(detail, response.status);
  }

  return payload as T;
}

function listPayload<T>(payload: unknown, key: "workspaces" | "documents" | "chats" | "messages"): T[] {
  if (Array.isArray(payload)) return payload as T[];
  if (typeof payload === "object" && payload !== null) {
    const value = (payload as Record<string, unknown>)[key];
    if (Array.isArray(value)) return value as T[];
  }
  return [];
}

export async function getWorkspaces(): Promise<Workspace[]> {
  const payload = await request<Workspace[] | { workspaces: Workspace[] }>("/workspaces");
  return listPayload<Workspace>(payload, "workspaces");
}

export async function createWorkspace(name: string): Promise<Workspace> {
  return request<Workspace>("/workspaces", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export async function updateWorkspace(
  id: string,
  changes: { name?: string; is_pinned?: boolean },
): Promise<Workspace> {
  return request<Workspace>(`/workspaces/${encodeURIComponent(id)}`, {
    method: "PATCH",
    body: JSON.stringify(changes),
  });
}

export async function deleteWorkspace(id: string): Promise<void> {
  await request<unknown>(`/workspaces/${encodeURIComponent(id)}`, { method: "DELETE" });
}

export async function getDocuments(workspaceId: string): Promise<Document[]> {
  const payload = await request<Document[] | { documents: Document[] }>(
    `/workspaces/${encodeURIComponent(workspaceId)}/documents`,
  );
  return listPayload<Document>(payload, "documents");
}

export async function uploadDocument(workspaceId: string, file: File): Promise<Document> {
  const form = new FormData();
  form.append("file", file);
  return request<Document>(`/workspaces/${encodeURIComponent(workspaceId)}/documents`, {
    method: "POST",
    body: form,
  });
}

export async function getChats(workspaceId: string): Promise<Chat[]> {
  const payload = await request<Chat[] | { chats: Chat[] }>(
    `/workspaces/${encodeURIComponent(workspaceId)}/chats`,
  );
  return listPayload<Chat>(payload, "chats");
}

export async function createChat(workspaceId: string, title: string): Promise<Chat> {
  return request<Chat>(`/workspaces/${encodeURIComponent(workspaceId)}/chats`, {
    method: "POST",
    body: JSON.stringify({ title }),
  });
}

export async function updateChat(
  id: string,
  changes: { title?: string; is_pinned?: boolean },
): Promise<Chat> {
  return request<Chat>(`/chats/${encodeURIComponent(id)}`, {
    method: "PATCH",
    body: JSON.stringify(changes),
  });
}

export async function deleteChat(id: string): Promise<void> {
  await request<unknown>(`/chats/${encodeURIComponent(id)}`, { method: "DELETE" });
}

export async function getMessages(chatId: string): Promise<Message[]> {
  const payload = await request<Message[] | { messages: Message[] }>(
    `/chats/${encodeURIComponent(chatId)}/messages`,
  );
  return listPayload<Message>(payload, "messages");
}

export async function sendMessage(
  chatId: string,
  question: string,
  documentIds: string[] = [],
  topK = 5,
): Promise<{ message?: Message; answer?: string; sources?: Source[] }> {
  return request<{ message?: Message; answer?: string; sources?: Source[] }>(
    `/chats/${encodeURIComponent(chatId)}/messages`,
    {
      method: "POST",
      body: JSON.stringify({
        question,
        document_ids: documentIds,
        top_k: topK,
      }),
    },
  );
}

export async function getNotes(workspaceId: string): Promise<{ content: string }> {
  return request<{ content: string }>(`/workspaces/${encodeURIComponent(workspaceId)}/notes`);
}

export async function saveNotes(workspaceId: string, content: string): Promise<{ content: string }> {
  return request<{ content: string }>(`/workspaces/${encodeURIComponent(workspaceId)}/notes`, {
    method: "PUT",
    body: JSON.stringify({ content }),
  });
}

export async function deleteDocument(documentId: string): Promise<void> {
  await request<unknown>(`/documents/${encodeURIComponent(documentId)}`, {
    method: "DELETE",
  });
}

export { API_BASE };

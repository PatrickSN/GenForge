export type ApiToken = {
  access_token: string;
  token_type: string;
};

export type Project = {
  id: string;
  project_name: string;
  description: string | null;
  owner_id: string;
  created_at: string;
  updated_at: string;
};

export type Variant = {
  id: string;
  project_id: string;
  sample_id: string | null;
  chromosome: string;
  position: number;
  reference: string;
  alternative: string;
  impact: string | null;
  gene_id: string | null;
  source_file_id: string | null;
  created_at: string;
  updated_at: string;
};

export type Page<T> = {
  items: T[];
  total: number;
  limit: number;
  offset: number;
};

export type VariantFile = {
  id: string;
  project_id: string;
  original_filename: string;
  storage_path: string;
  size_bytes: number;
  checksum_sha256: string;
  status: string;
  created_at: string;
  updated_at: string;
};

export type VariantProcessingJob = {
  id: string;
  file_id: string;
  status: string;
  tool: string;
  variants_inserted: number;
  log: string | null;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  finished_at: string | null;
};

export type UploadResult = {
  file: VariantFile;
  job: VariantProcessingJob;
};

type ApiValidationIssue = {
  loc?: Array<string | number>;
  msg?: string;
};

const API_CONNECTION_ERROR_MESSAGE =
  "Nao foi possivel conectar a API GenForge. Verifique se o backend esta ativo e se VITE_API_BASE_URL esta correto.";

function normalizeApiUrl(value: string): string {
  const trimmed = value.trim().replace(/\/+$/, "");
  const baseUrl = trimmed || "http://localhost:8000";
  return baseUrl.endsWith("/api/v1") ? baseUrl : `${baseUrl}/api/v1`;
}

const API_URL = normalizeApiUrl(
  import.meta.env.VITE_API_BASE_URL ?? import.meta.env.VITE_API_URL ?? "http://localhost:8000",
);

function translateKnownError(message: string, status: number): string {
  const normalized = message.toLowerCase();
  if (status === 401) return "Sessao expirada ou credenciais invalidas. Entre novamente.";
  if (status === 403) return "Voce nao tem permissao para acessar este recurso.";
  if (status === 404) return "Recurso nao encontrado ou indisponivel para seu usuario.";
  if (normalized.includes("only .vcf and .vcf.gz files are accepted")) {
    return "Envie um arquivo .vcf ou .vcf.gz.";
  }
  if (normalized.includes("already registered")) {
    return "Este e-mail ja esta cadastrado.";
  }
  if (normalized.includes("invalid credentials")) {
    return "E-mail ou senha invalidos.";
  }
  return message || `Falha na requisicao (HTTP ${status}).`;
}

function formatValidationIssues(issues: ApiValidationIssue[]): string {
  return issues
    .map((issue) => {
      const field = issue.loc?.filter((part) => part !== "body" && part !== "query").join(".");
      return field ? `${field}: ${issue.msg ?? "valor invalido"}` : issue.msg ?? "valor invalido";
    })
    .join("; ");
}

async function readErrorMessage(response: Response): Promise<string> {
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    try {
      const payload = (await response.json()) as { detail?: unknown; message?: unknown };
      if (Array.isArray(payload.detail)) {
        return translateKnownError(formatValidationIssues(payload.detail), response.status);
      }
      if (typeof payload.detail === "string") {
        return translateKnownError(payload.detail, response.status);
      }
      if (typeof payload.message === "string") {
        return translateKnownError(payload.message, response.status);
      }
    } catch {
      return `Falha ao interpretar resposta da API (HTTP ${response.status}).`;
    }
  }
  const detail = await response.text();
  return translateKnownError(detail, response.status);
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers,
    });
  } catch {
    throw new Error(API_CONNECTION_ERROR_MESSAGE);
  }
  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }
  if (response.status === 204) {
    return undefined as T;
  }
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export function login(email: string, password: string): Promise<ApiToken> {
  return request<ApiToken>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function register(email: string, fullName: string, password: string) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, full_name: fullName, password }),
  });
}

export function listProjects(token: string): Promise<Project[]> {
  return request<Project[]>("/projects", {}, token);
}

export function getProject(token: string, projectId: string): Promise<Project> {
  return request<Project>(`/projects/${projectId}`, {}, token);
}

export function createProject(
  token: string,
  payload: { project_name: string; description?: string },
): Promise<Project> {
  return request<Project>(
    "/projects",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    token,
  );
}

export function updateProject(
  token: string,
  projectId: string,
  payload: { project_name?: string; description?: string | null },
): Promise<Project> {
  return request<Project>(
    `/projects/${projectId}`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
    token,
  );
}

export function deleteProject(token: string, projectId: string): Promise<void> {
  return request<void>(
    `/projects/${projectId}`,
    {
      method: "DELETE",
    },
    token,
  );
}

export function listVariants(
  token: string,
  params: {
    projectId: string;
    chromosome?: string;
    geneId?: string;
    impact?: string;
    start?: string;
    end?: string;
    limit?: number;
    offset?: number;
  },
): Promise<Page<Variant>> {
  const search = new URLSearchParams({ project_id: params.projectId });
  if (params.chromosome) search.set("chromosome", params.chromosome);
  if (params.geneId) search.set("gene_id", params.geneId);
  if (params.impact) search.set("impact", params.impact);
  if (params.start) search.set("start", params.start);
  if (params.end) search.set("end", params.end);
  if (params.limit) search.set("limit", String(params.limit));
  if (params.offset !== undefined) search.set("offset", String(params.offset));
  return request<Page<Variant>>(`/variants?${search.toString()}`, {}, token);
}

export function uploadVcf(token: string, projectId: string, file: File): Promise<UploadResult> {
  const form = new FormData();
  form.append("file", file);
  return request<UploadResult>(
    `/variants/upload?project_id=${projectId}`,
    {
      method: "POST",
      body: form,
    },
    token,
  );
}

export function listVariantFiles(
  token: string,
  params: { projectId: string; limit?: number; offset?: number },
): Promise<Page<VariantFile>> {
  const search = new URLSearchParams({ project_id: params.projectId });
  if (params.limit) search.set("limit", String(params.limit));
  if (params.offset !== undefined) search.set("offset", String(params.offset));
  return request<Page<VariantFile>>(`/variants/files?${search.toString()}`, {}, token);
}

export function listVariantJobs(
  token: string,
  params: { projectId: string; status?: string; limit?: number; offset?: number },
): Promise<Page<VariantProcessingJob>> {
  const search = new URLSearchParams({ project_id: params.projectId });
  if (params.status) search.set("status", params.status);
  if (params.limit) search.set("limit", String(params.limit));
  if (params.offset !== undefined) search.set("offset", String(params.offset));
  return request<Page<VariantProcessingJob>>(`/variants/jobs?${search.toString()}`, {}, token);
}

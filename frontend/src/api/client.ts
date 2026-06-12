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
};

export type Page<T> = {
  items: T[];
  total: number;
  limit: number;
  offset: number;
};

export type UploadResult = {
  file: {
    id: string;
    project_id: string;
    original_filename: string;
    storage_path: string;
    size_bytes: number;
    checksum_sha256: string;
    status: string;
    created_at: string;
  };
  job: {
    id: string;
    file_id: string;
    status: string;
    tool: string;
    variants_inserted: number;
    log: string | null;
    created_at: string;
    started_at: string | null;
    finished_at: string | null;
  };
};

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

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

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `HTTP ${response.status}`);
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

export function listVariants(
  token: string,
  params: {
    projectId: string;
    chromosome?: string;
    geneId?: string;
    impact?: string;
    start?: string;
    end?: string;
  },
): Promise<Page<Variant>> {
  const search = new URLSearchParams({ project_id: params.projectId });
  if (params.chromosome) search.set("chromosome", params.chromosome);
  if (params.geneId) search.set("gene_id", params.geneId);
  if (params.impact) search.set("impact", params.impact);
  if (params.start) search.set("start", params.start);
  if (params.end) search.set("end", params.end);
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

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

DEFAULT_VCF = (
    b"##fileformat=VCFv4.2\n"
    b"#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n"
    b"Chr1\t10\t.\tA\tG\t.\tPASS\t"
    b"ANN=G|missense_variant|MODERATE|X|GeneA\tGT\t0/1\n"
)


class SmokeFailure(RuntimeError):
    pass


def normalize_base_url(value: str | None) -> str:
    if not value or not value.strip():
        raise SmokeFailure("API_URL/base URL is empty. Use --base-url http://host:8000.")

    base_url = value.strip().rstrip("/")
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise SmokeFailure(
            "API_URL/base URL must include scheme and host, for example http://127.0.0.1:8000."
        )
    return base_url


def decode_json(raw: bytes, context: str) -> dict[str, Any]:
    if not raw:
        raise SmokeFailure(f"{context}: empty response body; verify that the API is running.")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        preview = raw[:300].decode("utf-8", errors="replace")
        raise SmokeFailure(f"{context}: expected JSON, got: {preview}") from exc
    if not isinstance(payload, dict):
        raise SmokeFailure(f"{context}: expected a JSON object, got {type(payload).__name__}.")
    return payload


def request_json(
    base_url: str,
    method: str,
    path: str,
    *,
    token: str | None = None,
    payload: dict[str, Any] | None = None,
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
    expected: tuple[int, ...] = (200,),
    allow_empty: bool = False,
) -> dict[str, Any]:
    request_headers = dict(headers or {})
    if token:
        request_headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    url = f"{base_url}{path}"
    request = Request(url, data=body, headers=request_headers, method=method)
    context = f"{method} {path}"
    try:
        with urlopen(request, timeout=15) as response:
            raw = response.read()
            if response.status not in expected:
                raise SmokeFailure(f"{context}: expected {expected}, got HTTP {response.status}.")
            if allow_empty and not raw:
                return {}
            return decode_json(raw, context)
    except HTTPError as exc:
        raw = exc.read()
        preview = raw[:300].decode("utf-8", errors="replace")
        raise SmokeFailure(f"{context}: HTTP {exc.code}. Response: {preview}") from exc
    except URLError as exc:
        raise SmokeFailure(f"{context}: could not reach API at {base_url}: {exc.reason}") from exc


def upload_vcf(base_url: str, token: str, project_id: str) -> dict[str, Any]:
    boundary = f"----GenForgeSmoke{uuid.uuid4().hex}"
    body = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            b'Content-Disposition: form-data; name="file"; filename="smoke.vcf"\r\n',
            b"Content-Type: text/plain\r\n\r\n",
            DEFAULT_VCF,
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )
    return request_json(
        base_url,
        "POST",
        f"/api/v1/variants/upload?project_id={project_id}",
        token=token,
        body=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        expected=(202,),
    )


def wait_for_worker(
    base_url: str,
    token: str,
    job_id: str,
    project_id: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    job = request_json(base_url, "GET", f"/api/v1/variants/jobs/{job_id}", token=token)
    while job["status"] not in {"finished", "failed"} and time.monotonic() < deadline:
        time.sleep(1)
        job = request_json(base_url, "GET", f"/api/v1/variants/jobs/{job_id}", token=token)

    if job["status"] != "finished":
        raise SmokeFailure(
            f"Worker did not finish job {job_id}; final status is {job['status']!r}. "
            "Start Redis and the Celery worker, then rerun with --require-worker."
        )

    variants = request_json(
        base_url,
        "GET",
        f"/api/v1/variants?project_id={project_id}&limit=25&offset=0",
        token=token,
    )
    if variants.get("total", 0) < 1:
        raise SmokeFailure("Worker finished but variants endpoint returned no persisted variants.")
    return job


def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    base_url = normalize_base_url(args.base_url)
    email = args.email or f"smoke-{int(time.time())}-{uuid.uuid4().hex[:8]}@example.com"

    token: str | None = None
    project_id: str | None = None
    try:
        request_json(base_url, "GET", "/")
        request_json(base_url, "GET", "/health")
        user = request_json(
            base_url,
            "POST",
            "/api/v1/auth/register",
            payload={"email": email, "full_name": "GenForge Smoke", "password": args.password},
            expected=(201,),
        )
        token_payload = request_json(
            base_url,
            "POST",
            "/api/v1/auth/login",
            payload={"email": email, "password": args.password},
        )
        token = token_payload["access_token"]
        request_json(base_url, "GET", "/api/v1/users/me", token=token)
        project = request_json(
            base_url,
            "POST",
            "/api/v1/projects",
            token=token,
            payload={
                "project_name": f"Smoke VCF {int(time.time())}",
                "description": "phase1 smoke",
            },
            expected=(201,),
        )
        project_id = project["id"]
        upload = upload_vcf(base_url, token, project_id)
        job_id = upload["job"]["id"]
        files = request_json(
            base_url,
            "GET",
            f"/api/v1/variants/files?project_id={project_id}",
            token=token,
        )
        jobs = request_json(
            base_url,
            "GET",
            f"/api/v1/variants/jobs?project_id={project_id}",
            token=token,
        )
        variants = request_json(
            base_url,
            "GET",
            f"/api/v1/variants?project_id={project_id}&limit=25&offset=0",
            token=token,
        )
        worker_job = None
        if args.require_worker:
            worker_job = wait_for_worker(base_url, token, job_id, project_id, args.wait_job_seconds)

        return {
            "base_url": base_url,
            "user_id": user["id"],
            "project_id": project_id,
            "uploaded_file_id": upload["file"]["id"],
            "job_id": job_id,
            "job_status": (worker_job or upload["job"])["status"],
            "files_total": files["total"],
            "jobs_total": jobs["total"],
            "variants_total": variants["total"],
            "worker_required": args.require_worker,
        }
    finally:
        if args.cleanup_project and token and project_id:
            try:
                request_json(
                    base_url,
                    "DELETE",
                    f"/api/v1/projects/{project_id}",
                    token=token,
                    expected=(204,),
                    allow_empty=True,
                )
            except SmokeFailure as exc:
                print(f"SMOKE CLEANUP WARNING: {exc}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run GenForge Phase 1 API smoke checks.")
    parser.add_argument("--base-url", default=os.environ.get("API_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--email", default=os.environ.get("SMOKE_EMAIL"))
    parser.add_argument("--password", default=os.environ.get("SMOKE_PASSWORD", "genforge123"))
    parser.add_argument("--require-worker", action="store_true")
    parser.add_argument("--wait-job-seconds", type=int, default=30)
    parser.add_argument("--cleanup-project", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        summary = run_smoke(args)
    except SmokeFailure as exc:
        print(f"SMOKE FAILED: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

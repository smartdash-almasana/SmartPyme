import json
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import parse, request, error

EXPECTED_PROJECT_REF = "msfcjyssiaqegxbpkdai"
TARGET_USERS = [
    {
        "email": "rls-a@smartpyme.test",
        "tenant_id": "cliente_demo_rls_cli",
        "cliente_id": "cliente_demo_rls_cli",
    },
    {
        "email": "rls-b@smartpyme.test",
        "tenant_id": "cliente_demo_api",
        "cliente_id": "cliente_demo_api",
    },
]


def load_env_file(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def get_cfg(env: dict):
    base_url = env.get("SMARTPYME_SUPABASE_URL") or env.get("SUPABASE_URL") or env.get("NEXT_PUBLIC_SUPABASE_URL")
    service_key = env.get("SMARTPYME_SUPABASE_KEY") or env.get("SUPABASE_SERVICE_ROLE_KEY")
    project_ref_env = env.get("SUPABASE_PROJECT_REF")
    if not base_url or not service_key:
        raise RuntimeError("Missing Supabase URL or service role key in .env.local")

    parsed = parse.urlparse(base_url)
    host = parsed.netloc.lower()
    derived_ref = host.split(".")[0] if host else ""

    if project_ref_env and project_ref_env != EXPECTED_PROJECT_REF:
        raise RuntimeError(f"SUPABASE_PROJECT_REF mismatch: {project_ref_env} != {EXPECTED_PROJECT_REF}")
    if derived_ref and derived_ref != EXPECTED_PROJECT_REF:
        raise RuntimeError(f"URL project ref mismatch: {derived_ref} != {EXPECTED_PROJECT_REF}")

    return base_url.rstrip("/"), service_key, EXPECTED_PROJECT_REF


class Api:
    def __init__(self, base_url: str, service_key: str):
        self.base_url = base_url
        self.service_key = service_key

    def call(self, method: str, path: str, query: dict | None = None, payload: dict | None = None):
        url = self.base_url + path
        if query:
            url += "?" + parse.urlencode(query, doseq=True)
        body = None
        headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Accept": "application/json",
        }
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = request.Request(url=url, data=body, method=method.upper(), headers=headers)
        try:
            with request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else None
        except error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"HTTP {e.code} {method} {path}: {detail[:300]}") from e


def ensure_clientes_exist(api: Api, cliente_ids: list[str]):
    for cid in cliente_ids:
        data = api.call(
            "GET",
            "/rest/v1/clientes",
            query={"select": "cliente_id", "cliente_id": f"eq.{cid}", "limit": "1"},
        )
        if not data:
            raise RuntimeError(f"cliente_id not found in public.clientes: {cid}")


def list_users(api: Api) -> list[dict]:
    page = 1
    users = []
    while True:
        res = api.call("GET", "/auth/v1/admin/users", query={"page": str(page), "per_page": "200"})
        batch = res.get("users", []) if isinstance(res, dict) else []
        users.extend(batch)
        if len(batch) < 200:
            break
        page += 1
    return users


def strong_password() -> str:
    return secrets.token_urlsafe(18) + "!Aa1"


def main():
    env = load_env_file(Path(".env.local"))
    base_url, service_key, project_ref = get_cfg(env)
    api = Api(base_url, service_key)

    ensure_clientes_exist(api, [u["cliente_id"] for u in TARGET_USERS])

    existing = {u.get("email", "").lower(): u for u in list_users(api)}
    backups = []
    summary = []

    for target in TARGET_USERS:
        email = target["email"].lower()
        tenant_id = target["tenant_id"]
        cliente_id = target["cliente_id"]
        user = existing.get(email)

        if user:
            user_id = user.get("id")
            before = user.get("app_metadata") or {}
            merged = dict(before)
            merged["tenant_id"] = tenant_id
            merged["cliente_id"] = cliente_id

            api.call("PUT", f"/auth/v1/admin/users/{user_id}", payload={
                "app_metadata": merged,
                "email_confirm": True,
            })
            after_user = api.call("GET", f"/auth/v1/admin/users/{user_id}")
            after_meta = (after_user or {}).get("app_metadata") or {}
            if after_meta.get("tenant_id") != tenant_id or after_meta.get("cliente_id") != cliente_id:
                raise RuntimeError(f"Verification failed for {email}")

            backups.append({
                "email": email,
                "user_id": user_id,
                "action": "updated",
                "app_metadata_before": before,
                "app_metadata_after": after_meta,
            })
            summary.append({
                "email": email,
                "user_id": user_id,
                "action": "updated",
                "tenant_id": tenant_id,
                "cliente_id": cliente_id,
                "verified": True,
                "temporary_password": None,
            })
        else:
            tmp_pass = strong_password()
            created = api.call("POST", "/auth/v1/admin/users", payload={
                "email": email,
                "password": tmp_pass,
                "email_confirm": True,
                "app_metadata": {
                    "tenant_id": tenant_id,
                    "cliente_id": cliente_id,
                },
            })
            user_id = created.get("id")
            if not user_id:
                raise RuntimeError(f"Creation failed for {email}")

            after_user = api.call("GET", f"/auth/v1/admin/users/{user_id}")
            after_meta = (after_user or {}).get("app_metadata") or {}
            if after_meta.get("tenant_id") != tenant_id or after_meta.get("cliente_id") != cliente_id:
                raise RuntimeError(f"Verification failed for {email}")

            backups.append({
                "email": email,
                "user_id": user_id,
                "action": "created",
                "app_metadata_before": None,
                "app_metadata_after": after_meta,
            })
            summary.append({
                "email": email,
                "user_id": user_id,
                "action": "created",
                "tenant_id": tenant_id,
                "cliente_id": cliente_id,
                "verified": True,
                "temporary_password": tmp_pass,
            })

    backup_path = Path(".local/staging_auth_backup.json")
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_ref": project_ref,
        "mode": "staging/dev",
        "entries": backups,
    }
    backup_path.write_text(json.dumps(backup_data, indent=2), encoding="utf-8")

    safe_summary = [
        {
            "email": s["email"],
            "user_id": s["user_id"],
            "action": s["action"],
            "tenant_id": s["tenant_id"],
            "cliente_id": s["cliente_id"],
            "verified": s["verified"],
            "temporary_password": s["temporary_password"],
        }
        for s in summary
    ]

    print(json.dumps({
        "project_ref": project_ref,
        "backup_path": str(backup_path).replace('\\\\', '/'),
        "users": safe_summary,
    }, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

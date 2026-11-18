"""
Cria um tenant e um usuário dono, para desenvolvimento.

Uso:
  uv run python -m api.scripts.seed --tenant-name "Loja Teste" --slug loja-teste \
      --email erick@test.com --name Erick --password "SenhaForte123"
"""

import argparse
from datetime import UTC, datetime

from core.db import system_session, tenant_session
from core.models import Membership, Tenant, User
from core.security import hash_password


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a dev tenant and owner user")
    parser.add_argument("--tenant-name", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--segment", default="retail")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    with system_session() as s:
        tenant = Tenant(
            name=args.tenant_name,
            slug=args.slug,
            segment=args.segment,
            metric_pack=f"{args.segment}@1",
        )
        user = User(
            email=args.email.lower(),
            name=args.name,
            password_hash=hash_password(args.password),
        )
        s.add_all([tenant, user])
        s.flush()
        tenant_id, user_id = tenant.id, user.id

    with tenant_session(tenant_id) as s:
        s.add(
            Membership(
                tenant_id=tenant_id,
                user_id=user_id,
                role="owner",
                accepted_at=datetime.now(UTC),
            )
        )

    print(f"tenant_id: {tenant_id}")
    print(f"user_id:   {user_id}")


if __name__ == "__main__":
    main()

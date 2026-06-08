from __future__ import annotations

from datetime import datetime
from typing import Iterable

from models import Permission, Role, RolePermission


DEFAULT_ROLES: list[dict[str, str]] = [
    {
        "name": "Admin",
        "slug": "admin",
        "description": "Full access: users, roles, permissions, settings, datasets, analytics, audit logs, models, moderation, platform configuration.",
    },
    {
        "name": "Farmer",
        "slug": "farmer",
        "description": "Create predictions, upload crop images, view own history, manage own profile, view recommendations.",
    },
    {
        "name": "Researcher",
        "slug": "researcher",
        "description": "View datasets, analyze predictions, access dashboards, export reports, access aggregated analytics.",
    },
    {
        "name": "Moderator",
        "slug": "moderator",
        "description": "Review submissions, moderate reports, manage flagged content, review community activity.",
    },
]


DEFAULT_PERMISSIONS: list[dict[str, str]] = [
    # Users
    {"slug": "users:create", "name": "users:create", "resource": "users", "action": "create"},
    {"slug": "users:read", "name": "users:read", "resource": "users", "action": "read"},
    {"slug": "users:update", "name": "users:update", "resource": "users", "action": "update"},
    {"slug": "users:delete", "name": "users:delete", "resource": "users", "action": "delete"},

    # Roles
    {"slug": "roles:create", "name": "roles:create", "resource": "roles", "action": "create"},
    {"slug": "roles:read", "name": "roles:read", "resource": "roles", "action": "read"},
    {"slug": "roles:update", "name": "roles:update", "resource": "roles", "action": "update"},
    {"slug": "roles:delete", "name": "roles:delete", "resource": "roles", "action": "delete"},

    # Permissions
    {"slug": "permissions:create", "name": "permissions:create", "resource": "permissions", "action": "create"},
    {"slug": "permissions:read", "name": "permissions:read", "resource": "permissions", "action": "read"},
    {"slug": "permissions:update", "name": "permissions:update", "resource": "permissions", "action": "update"},
    {"slug": "permissions:delete", "name": "permissions:delete", "resource": "permissions", "action": "delete"},

    # Predictions
    {"slug": "predictions:create", "name": "predictions:create", "resource": "predictions", "action": "create"},
    {"slug": "predictions:read", "name": "predictions:read", "resource": "predictions", "action": "read"},
    {"slug": "predictions:update", "name": "predictions:update", "resource": "predictions", "action": "update"},
    {"slug": "predictions:delete", "name": "predictions:delete", "resource": "predictions", "action": "delete"},

    # Datasets
    {"slug": "datasets:read", "name": "datasets:read", "resource": "datasets", "action": "read"},
    {"slug": "datasets:export", "name": "datasets:export", "resource": "datasets", "action": "export"},

    # Reports
    {"slug": "reports:export", "name": "reports:export", "resource": "reports", "action": "export"},

    # Analytics
    {"slug": "analytics:view", "name": "analytics:view", "resource": "analytics", "action": "view"},

    # Content moderation
    {"slug": "content:moderate", "name": "content:moderate", "resource": "content", "action": "moderate"},

    # Settings & models
    {"slug": "settings:manage", "name": "settings:manage", "resource": "settings", "action": "manage"},
    {"slug": "models:manage", "name": "models:manage", "resource": "models", "action": "manage"},

    # Audit
    {"slug": "audit:read", "name": "audit:read", "resource": "audit", "action": "read"},
]


DEFAULT_ROLE_PERMISSIONS: dict[str, list[str]] = {
    # Admin: everything in the current default permission set
    "admin": [p["slug"] for p in DEFAULT_PERMISSIONS],

    # Farmer: create predictions, read predictions
    "farmer": [
        "predictions:create",
        "predictions:read",
    ],

    # Researcher: datasets + analytics + reports export
    "researcher": [
        "datasets:read",
        "datasets:export",
        "analytics:view",
        "reports:export",
        "predictions:read",
    ],

    # Moderator: moderation permissions
    "moderator": [
        "content:moderate",
        "predictions:read",
    ],
}


def seed_rbac_permissions_and_roles() -> None:
    """Idempotent seeding for RBAC roles/permissions/mappings.

    Intended to be called during app startup (inside app.app_context()).
    """

    # Seed roles
    for r in DEFAULT_ROLES:
        role = Role.query.filter_by(slug=r["slug"], deleted_at=None).first()
        if role is None:
            Role.query.session.add(
                Role(
                    name=r["name"],
                    slug=r["slug"],
                    description=r.get("description"),
                )
            )
    Role.query.session.commit()

    # Seed permissions
    for p in DEFAULT_PERMISSIONS:
        perm = Permission.query.filter_by(slug=p["slug"]).first()
        if perm is None:
            Permission.query.session.add(
                Permission(
                    slug=p["slug"],
                    name=p["name"],
                    description=p.get("description"),
                    resource=p.get("resource"),
                    action=p.get("action"),
                )
            )
    Permission.query.session.commit()

    # Seed mappings
    for role_slug, permission_slugs in DEFAULT_ROLE_PERMISSIONS.items():
        role = Role.query.filter_by(slug=role_slug, deleted_at=None).first()
        if role is None:
            continue

        for perm_slug in permission_slugs:
            perm = Permission.query.filter_by(slug=perm_slug).first()
            if perm is None:
                continue

            exists = (
                RolePermission.query.filter_by(role_id=role.id, permission_id=perm.id).first()
                is not None
            )
            if not exists:
                RolePermission.query.session.add(
                    RolePermission(role_id=role.id, permission_id=perm.id, created_at=datetime.utcnow())
                )

    RolePermission.query.session.commit()


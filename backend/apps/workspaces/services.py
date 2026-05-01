from django.db import transaction

from .models import Workspace, WorkspaceMembership


@transaction.atomic
def create_workspace_with_creator(*, creator, name, description=""):
    workspace = Workspace.objects.create(name=name, description=description, creator=creator)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=creator,
        role=WorkspaceMembership.Role.ADMIN,
    )
    return workspace


@transaction.atomic
def set_member_role(*, workspace, actor, target_user_id, role):
    actor_membership = WorkspaceMembership.objects.filter(
        workspace=workspace,
        user=actor,
        role=WorkspaceMembership.Role.ADMIN,
    ).first()
    if not actor_membership:
        raise PermissionError("Only workspace admins can update member roles")

    membership = WorkspaceMembership.objects.select_for_update().filter(
        workspace=workspace,
        user_id=target_user_id,
    ).first()
    if not membership:
        raise ValueError("Workspace member not found")

    if membership.role == role:
        return membership

    if membership.user_id == actor.id and role == WorkspaceMembership.Role.MEMBER:
        admin_count = WorkspaceMembership.objects.filter(
            workspace=workspace,
            role=WorkspaceMembership.Role.ADMIN,
        ).count()
        if admin_count <= 1:
            raise ValueError("Cannot demote the last workspace admin")

    membership.role = role
    membership.save(update_fields=["role"])
    return membership


@transaction.atomic
def remove_workspace_member(*, workspace, actor, target_user_id):
    actor_is_admin = WorkspaceMembership.objects.filter(
        workspace=workspace,
        user=actor,
        role=WorkspaceMembership.Role.ADMIN,
    ).exists()
    if not actor_is_admin:
        raise PermissionError("Only workspace admins can remove members")

    membership = WorkspaceMembership.objects.select_for_update().filter(
        workspace=workspace,
        user_id=target_user_id,
    ).first()
    if not membership:
        raise ValueError("Workspace member not found")

    if membership.role == WorkspaceMembership.Role.ADMIN:
        admin_count = WorkspaceMembership.objects.filter(
            workspace=workspace,
            role=WorkspaceMembership.Role.ADMIN,
        ).count()
        if admin_count <= 1:
            raise ValueError("Cannot remove the last workspace admin")

    membership.delete()

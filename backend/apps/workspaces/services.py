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

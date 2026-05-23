from rest_framework import permissions, viewsets

from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.filter(owner=self.request.user)
        status = self.request.query_params.get("status")
        due_before = self.request.query_params.get("due_before")

        if status:
            queryset = queryset.filter(status=status)
        if due_before:
            queryset = queryset.filter(due_date__lte=due_before)

        return queryset

    def perform_create(self, serializer: TaskSerializer) -> None:
        serializer.save(owner=self.request.user)

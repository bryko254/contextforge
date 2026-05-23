from rest_framework import serializers

from apps.tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "owner",
            "owner_username",
            "title",
            "description",
            "status",
            "due_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "owner_username", "created_at", "updated_at"]

    def validate_title(self, value: str) -> str:
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Task title must be at least 3 characters.")
        return value.strip()

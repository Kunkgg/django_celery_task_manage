"""URL 配置模块"""

from django.urls import path
from .views import TaskSubmitView, TaskDetailView, TaskListView, TaskTypeListView

urlpatterns = [
    path("task-types/", TaskTypeListView.as_view(), name="task_type_list"),
    path("tasks/", TaskSubmitView.as_view(), name="task_submit"),
    path("tasks/list/", TaskListView.as_view(), name="task_list"),
    path("tasks/<int:task_id>/", TaskDetailView.as_view(), name="task_detail"),
]

"""URL 配置模块"""

from django.urls import path
from .views import TaskSubmitView, TaskDetailView, TaskListView

urlpatterns = [
    path("tasks/", TaskSubmitView.as_view(), name="task_submit"),
    path("tasks/list/", TaskListView.as_view(), name="task_list"),
    path("tasks/<int:task_id>/", TaskDetailView.as_view(), name="task_detail"),
]

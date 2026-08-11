import os

from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from trainer.views import (
    attempt_detail,
    respond,
    scenario_detail,
    scenario_list,
    start_attempt,
)

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("api/scenarios/", scenario_list),
    path("api/scenarios/<slug:scenario_key>/", scenario_detail),
    path("api/scenarios/<slug:scenario_key>/start/", start_attempt),
    path("api/attempts/<uuid:attempt_id>/respond/", respond),
    path("api/attempts/<uuid:attempt_id>/", attempt_detail),
    path("privacy/", TemplateView.as_view(template_name="privacy.html"), name="privacy"),
    path("terms/", TemplateView.as_view(template_name="terms.html"), name="terms"),
]

if os.getenv("ENABLE_DJANGO_ADMIN", "false").lower() == "true":
    urlpatterns.append(path("admin/", admin.site.urls))

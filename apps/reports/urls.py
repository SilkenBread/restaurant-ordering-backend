from django.urls import path
from .views.sales_report_views import GenerateReportView, ReportStatusView, DownloadReportView


urlpatterns = [
    path('generate/', GenerateReportView.as_view(), name='generate_report'),
    path('<int:id>/status/', ReportStatusView.as_view(), name='report_status'),
    path('<int:report_id>/download/', DownloadReportView.as_view(), name='download_report'),
]

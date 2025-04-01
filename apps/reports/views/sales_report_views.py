from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import FileResponse
import os

from apps.reports.tasks import generate_sales_report

from ..serializers.sales_report_serializers import SalesReportSerializer
from ..models import SalesReport


class GenerateReportView(APIView):
    def post(self, request):
        restaurant_id = request.data.get('restaurant_id')
        month = request.data.get('month')
        year = request.data.get('year')

        if not all([restaurant_id, month, year]):
            return Response({"error": "Todos los campos son requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        report = SalesReport.objects.create(
            restaurant_id=restaurant_id, month=month, year=year, status="pending"
        )
        
        generate_sales_report.delay(report.id)

        return Response({"message": "Reporte en proceso", "report_id": report.id}, status=status.HTTP_202_ACCEPTED)


class ReportStatusView(generics.RetrieveAPIView):
    queryset = SalesReport.objects.all()
    serializer_class = SalesReportSerializer
    lookup_field = 'id'


class DownloadReportView(APIView):
    def get(self, request, report_id):
        try:
            report = SalesReport.objects.get(id=report_id, status="completed")
            file_path = report.report_file.path

            response = FileResponse(open(file_path, 'rb'), as_attachment=True)
            
            # borrar el archivo despues de la descarga
            os.remove(file_path)
            report.report_file.delete()
            report.delete()

            return response
        except SalesReport.DoesNotExist:
            return Response({"error": "El reporte no está disponible."}, status=status.HTTP_404_NOT_FOUND)

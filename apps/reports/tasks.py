import os
import csv
import logging
from celery import shared_task
from django.core.files.base import ContentFile
from django.core.files import File
from django.core.files.storage import default_storage
from django.conf import settings

from apps.orders.models import Order
from apps.reports.models import SalesReport

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def generate_sales_report(self, report_id):
    try:
        report = SalesReport.objects.get(id=report_id)
        report.status = 'processing'
        report.save()

        orders = Order.objects.filter(
            restaurant=report.restaurant,
            created_at__year=report.year,
            created_at__month=report.month
        )

        # Nombre del archivo
        filename = f"reports/sales_report_{report.restaurant.id}_{report.year}_{report.month}.csv"
        
        # Asegurar que el directorio reports/ existe
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'reports'), exist_ok=True)
        
        # Ruta completa temporal del archivo
        temp_path = os.path.join(settings.MEDIA_ROOT, filename)
        
        # Guardar CSV en disco temporalmente
        with open(temp_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["ID Restaurante", "Nombre", "Total Ventas", "Total Precio Ventas"])
            total_sales = orders.count()
            total_price = sum(order.total_amount for order in orders)
            writer.writerow([report.restaurant.id, report.restaurant.name, total_sales, total_price])
        
        # Abrir el archivo recién creado y guardarlo en el campo FileField
        with open(temp_path, 'rb') as f:
            # Usar solo el nombre de archivo sin la ruta completa
            report.report_file.save(os.path.basename(filename), File(f), save=True)
        
        # Eliminar el archivo temporal
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        report.status = 'completed'
        report.save()
        
        logger.info(f"Reporte generado en: {report.report_file.path}")
        
        return f"Reporte guardado en {report.report_file.path}"
        
    except SalesReport.DoesNotExist:
        logger.error(f"Error: Reporte con ID {report_id} no encontrado")
        return f"Error: Reporte con ID {report_id} no encontrado"
        
    except Exception as e:
        report.status = 'failed'
        report.save()
        logger.error(f"Error al generar el reporte: {str(e)}")
        raise e

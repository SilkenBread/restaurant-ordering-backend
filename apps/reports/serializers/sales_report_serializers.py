from rest_framework import serializers
from apps.reports.models import SalesReport

class SalesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesReport
        fields = '__all__'

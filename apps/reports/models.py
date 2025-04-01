from django.db import models

class SalesReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE)
    report_file = models.FileField(upload_to='reports/', null=True, blank=True)
    month = models.IntegerField()
    year = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sales Report for {self.restaurant.name} - {self.month}/{self.year} ({self.status})"
    
    class Meta:
        verbose_name = 'Sales Report'
        verbose_name_plural = 'Sales Reports'
        ordering = ['-year', '-month']

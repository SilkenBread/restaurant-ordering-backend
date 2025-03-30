from django.db import models
from django.utils.translation import gettext_lazy as _

class Restaurant(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        CLOSED = 'closed', _('Closed')
        MAINTENANCE = 'maintenance', _('Under Maintenance')

    name = models.CharField(max_length=255, verbose_name=_('Name'))
    address = models.TextField(verbose_name=_('Address'))
    rating = models.DecimalField(
        max_digits=2, 
        decimal_places=1,
        verbose_name=_('Rating'),
        help_text=_('Rating from 0.0 to 5.0')
    )
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.OPEN,
        verbose_name=_('Status')
    )
    category = models.CharField(max_length=100, verbose_name=_('Category'))
    latitude = models.DecimalField(max_digits=14, decimal_places=11, verbose_name=_('Latitude'))
    longitude = models.DecimalField(max_digits=14, decimal_places=11, verbose_name=_('Longitude'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        db_table = 'RESTAURANTS'
        verbose_name = _('Restaurant')
        verbose_name_plural = _('Restaurants')
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=0, rating__lte=5),
                name='rating_range'
            ),
        ]

    def __str__(self):
        return self.name

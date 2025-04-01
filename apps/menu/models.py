from django.db import models
from django.utils.translation import gettext_lazy as _

class MenuItem(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.TextField(verbose_name=_('Description'))
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Price'),
        help_text=_('Price in USD')
    )
    preparation_time = models.IntegerField(
        verbose_name=_('Preparation Time'),
        help_text=_('Preparation time in minutes')
    )
    category = models.CharField(max_length=100, verbose_name=_('Category'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    is_available = models.BooleanField(default=True, verbose_name=_('Is Available'))
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name=_('Restaurant')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    image = models.ImageField(upload_to='menu/item_images/', null=True, blank=True, verbose_name=_('Image'))

    class Meta:
        db_table = 'MENU_ITEMS'
        verbose_name = _('Menu Item')
        verbose_name_plural = _('Menu Items')
        unique_together = ('name', 'restaurant')
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='price_positive'
            ),
            models.CheckConstraint(
                check=models.Q(preparation_time__gte=0),
                name='preparation_time_positive'
            ),
        ]
        indexes = [
            models.Index(fields=['name'], name='idx_menu_item_name'),
            models.Index(fields=['category'], name='idx_menu_item_category'),
            models.Index(fields=['restaurant'], name='idx_menu_item_restaurant'),
            models.Index(fields=['is_available'], name='idx_menu_item_availability'),
        ]

    def __str__(self):
        return self.name

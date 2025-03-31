from django.db import models

class Order(models.Model):
    is_active = models.BooleanField(default=True)
    customer = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    delivery_address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    special_instructions = models.TextField(
        blank=True,
        null=True,
    )
    estimated_delivery_time = models.DateTimeField(
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Order {self.id} - {self.customer.username} - {self.status}"
    
    class Meta:
        db_table = "ORDERS"
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]

class OrderItem(models.Model):
    is_active = models.BooleanField(default=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_items",
    )
    menu_item = models.ForeignKey(
        "menu.MenuItem",
        on_delete=models.CASCADE,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    note = models.TextField(
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"OrderItem {self.id} - {self.order.id} - {self.menu_item.name}"
    
    class Meta:
        db_table = "ORDER_ITEMS"
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ["-created_at"]

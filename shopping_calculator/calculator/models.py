from django.db import models
from decimal import Decimal

class ShoppingItem(models.Model):
    name = models.CharField(max_length=100, verbose_name='商品名')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=1,
        verbose_name='価格',
        help_text='小数点以下1桁まで入力可能です'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ¥{self.price}"

class CalculationResult(models.Model):
    total_amount = models.DecimalField(max_digits=10, decimal_places=0)
    calculated_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"計算結果: ¥{self.total_amount} ({self.status})"

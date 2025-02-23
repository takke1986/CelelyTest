from django.core.management.base import BaseCommand
from calculator.models import CalculationResult
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = '古い計算結果を削除します'

    def handle(self, *args, **options):
        # 24時間以上前の計算結果を削除
        old_results = CalculationResult.objects.filter(
            calculated_at__lt=timezone.now() - timedelta(hours=24)
        )
        count = old_results.count()
        old_results.delete()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} old calculation results')
        ) 
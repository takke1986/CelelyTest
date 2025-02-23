from celery import shared_task
from .models import ShoppingItem, CalculationResult
from decimal import Decimal, ROUND_DOWN
import logging
import time
from celery.utils.log import get_task_logger
from datetime import datetime

# Celery専用のロガーを使用
logger = get_task_logger(__name__)

@shared_task(bind=True)
def calculate_total(self):
    task_id = self.request.id
    start_time = datetime.now()
    logger.info(f"Starting calculate_total task (ID: {task_id}) at {start_time}")
    
    try:
        # 初期処理（データ収集）
        logger.info("Step 1/3: Starting data collection...")
        time.sleep(0.5)  # 固定で1秒待機
        logger.info("Data collection completed")
        
        # 計算処理
        calc_start = datetime.now()
        logger.info("Step 2/3: Starting calculation...")
        items = ShoppingItem.objects.all()
        total = sum(item.price for item in items)
        total = Decimal(str(total)).quantize(Decimal('1'), rounding=ROUND_DOWN)
        time.sleep(0.5)  # 固定で1秒待機
        calc_end = datetime.now()
        logger.info(f"Calculation completed. Total: {total}")
        
        # 保存処理
        save_start = datetime.now()
        logger.info("Step 3/3: Saving results...")
        time.sleep(0.5)  # 固定で1秒待機
        
        result = CalculationResult.objects.create(
            total_amount=total,
            status='completed'
        )
        save_end = datetime.now()
        logger.info("Results saved successfully")
        
        end_time = datetime.now()
        total_duration = end_time - start_time
        logger.info(f"Task completed in {total_duration}")
        return str(result.total_amount)
    except Exception as e:
        logger.error(f"Task {task_id} failed with error: {str(e)}")
        raise
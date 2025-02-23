from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from .models import ShoppingItem, CalculationResult
from .tasks import calculate_total
from .forms import ShoppingItemForm
from django.contrib import messages
from celery.exceptions import OperationalError
from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
import logging
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class ShoppingListView(ListView):
    model = ShoppingItem
    template_name = 'calculator/shopping_list.html'
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ShoppingItemForm()
        # 最新の計算結果を取得（calculated_atで降順ソート）
        result = CalculationResult.objects.order_by('-calculated_at').first()
        logger.info(f"Latest calculation result: {result.total_amount if result else 'None'}")
        context['result'] = result
        return context

    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            logger.info("Received AJAX POST request")
            logger.debug(f"POST data: {request.POST}")
            logger.debug(f"Request headers: {request.headers}")

            # 削除処理
            if 'delete_item' in request.POST:
                item_id = request.POST.get('delete_item')
                logger.info(f"Processing delete request for item ID: {item_id}")
                try:
                    item = get_object_or_404(ShoppingItem, id=item_id)
                    item_name = item.name  # 削除前に名前を保存
                    item.delete()
                    logger.info(f"Item '{item_name}' deleted successfully")
                    
                    task = calculate_total.delay()
                    logger.info(f"Task scheduled with id: {task.id}")
                    logger.info(f"Task state: {task.state}")
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': f"{item_name}を削除しました"
                    })
                except ShoppingItem.DoesNotExist:
                    logger.error(f"Item with id {item_id} not found")
                    return JsonResponse({
                        'status': 'error',
                        'message': "商品が見つかりませんでした"
                    }, status=404)
                except Exception as e:
                    logger.error(f"Error during item deletion: {str(e)}")
                    return JsonResponse({
                        'status': 'error',
                        'message': f"削除中にエラーが発生しました: {str(e)}"
                    }, status=500)

            # 商品追加処理
            elif 'name' in request.POST and 'price' in request.POST:
                logger.info("Processing add item request")
                form = ShoppingItemForm(request.POST)
                if form.is_valid():
                    try:
                        item = form.save()
                        logger.info(f"Item saved: {item.name}")
                        
                        task = calculate_total.delay()
                        logger.info(f"Task scheduled with id: {task.id}")
                        logger.info(f"Task state: {task.state}")
                        
                        return JsonResponse({
                            'status': 'success',
                            'message': f"{item.name}を追加しました"
                        })
                    except Exception as e:
                        logger.error(f"Error during item addition: {str(e)}")
                        return JsonResponse({
                            'status': 'error',
                            'message': f"商品の追加中にエラーが発生しました: {str(e)}"
                        }, status=500)
                else:
                    errors = '; '.join([f"{field}: {', '.join(error)}" for field, error in form.errors.items()])
                    logger.warning(f"Form validation failed: {errors}")
                    return JsonResponse({
                        'status': 'error',
                        'message': f"入力内容に問題があります: {errors}"
                    }, status=400)

            # 不正なリクエスト
            logger.warning("Invalid request received")
            logger.debug(f"Request POST data: {request.POST}")
            logger.debug(f"Request headers: {request.headers}")
            return JsonResponse({
                'status': 'error',
                'message': '不正なリクエストです'
            }, status=400)

        # 非AJAXリクエストの場合
        form = ShoppingItemForm(request.POST)
        if form.is_valid():
            try:
                item = form.save()
                messages.success(request, f"{item.name}を追加しました")
                task = calculate_total.delay()
            except Exception as e:
                messages.error(request, f"エラーが発生しました: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        return HttpResponseRedirect(reverse('shopping-list'))

    def get_calculation_result(self, request):
        result = CalculationResult.objects.order_by('-calculated_at').first()
        if result:
            # 日時フォーマットを日本時間に合わせて修正
            calculated_at = result.calculated_at.astimezone()
            return JsonResponse({
                'total_amount': str(result.total_amount),
                'calculated_at': calculated_at.strftime('%Y/%m/%d %H:%M'),
                'status': 'success',
                'processing_time': 3000  # ワーカーの合計処理時間（ミリ秒）
            })
        return JsonResponse({'status': 'no_result'})

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if request.headers.get('X-Update-Items'):
                # 商品一覧のデータを返す
                items = ShoppingItem.objects.all()
                return JsonResponse({
                    'items': [
                        {
                            'id': item.id,
                            'name': item.name,
                            'price': str(item.price)
                        } for item in items
                    ]
                })
            return self.get_calculation_result(request)
        return super().get(request, *args, **kwargs)

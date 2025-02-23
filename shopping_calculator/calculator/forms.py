from django import forms
from .models import ShoppingItem
from decimal import Decimal

class ShoppingItemForm(forms.ModelForm):
    class Meta:
        model = ShoppingItem
        fields = ['name', 'price']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '商品名を入力'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'placeholder': '価格を入力'
            })
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None:
            raise forms.ValidationError('価格を入力してください')
        
        if price < 0:
            raise forms.ValidationError('価格は0以上で入力してください')

        # 文字列に変換して小数点以下の桁数をチェック
        price_str = str(price)
        if '.' in price_str:
            decimal_places = len(price_str.split('.')[1])
            if decimal_places > 1:
                raise forms.ValidationError('価格は小数点以下1桁までしか入力できません')

        return price

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('商品名を入力してください')
        if len(name) > 100:
            raise forms.ValidationError('商品名は100文字以内で入力してください')
        return name
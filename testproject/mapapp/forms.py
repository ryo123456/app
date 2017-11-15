# -*- coding: utf-8 -*-

from django import forms


class MyForm(forms.Form):
    search = forms.CharField(max_length=100 ,label=u"宿泊施設検索")

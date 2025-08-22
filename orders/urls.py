from  . import views
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments')
]

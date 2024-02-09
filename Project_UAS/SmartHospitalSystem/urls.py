from django.urls import path
from . import views

app_name = 'SmartHospitalSystem'

urlpatterns = [
    path('', views.update_page, name='homepage'),
    path('info/',views.InfoPageView.as_view(),name='infopage'),
    path('log1/',views.Log1PageView.as_view(),name='log1_page'),
    path('log2/',views.Log2PageView.as_view(),name='log2_page'),
    path('log3/',views.Log3PageView.as_view(),name='log3_page')
]
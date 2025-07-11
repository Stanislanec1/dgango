from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('upload/', views.upload_document, name='upload'),
    path('order/', views.order_analysis, name='order'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/pay/<int:order_id>/', views.pay_order, name='pay_order'),
    path('upload-to-fastapi/<int:doc_id>/', views.upload_to_fastapi, name='upload_to_fastapi'),
    path('delete-document/<int:doc_id>/', views.delete_document, name='delete_document'),
    path('analyse-document/', views.analyse_document_view, name='analyse_document'),
    path('get-text/', views.get_text_view, name='get_text')



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""App_shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from shop.views import ProductAddView, ProductAllView, SearchProductView, ProductDetailsView, \
    UserView, AddUserView, MenuView, LogoutView, BasketView, delete_product, DeliveryPaymentView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('menu/addproduct', ProductAddView.as_view(), name='add product'),
    path('menu/product_list', ProductAllView.as_view(), name='product_list'),
    path('menu/search', SearchProductView.as_view(), name='search'),
    path('menu/product/<int:id>', ProductDetailsView.as_view(), name='product_details'),
    path('menu/login', UserView.as_view(), name="login"),
    path('menu/add_user', AddUserView.as_view(), name="add_user"),
    path('menu', MenuView.as_view(), name='menu'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('menu/basket', BasketView.as_view(), name='basket'),
    path('menu/basket/delete_product/<int:id>', delete_product, name = 'delete_product'),
    path('menu/basket/delivery',DeliveryPaymentView.as_view(), name = 'delivery')
]

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.views.generic import FormView, CreateView
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SearchProductForm, UserForm, UserCreateForm, DeliveryForm
from .models import Products, Category, Image, Basket, ProductBasket, Users,Delivery


# Create your views here.

# class ProductAddView(FormView):
#     template_name = 'webshop/add_product.html'
#     FormView = ProductAddForm
#     success_url = reverse_lazy('product_list')
#
#     def form_valid(self, form):
#         cd = form.cleaned_data
#         name = cd['name']
#         description = cd['description']
#         price = cd['price']
#         number_of_items = cd['number_of_items']
#         # category = cd['category']
#         Products.objects.create(name=name, price=price, description=description, number_of_items=number_of_items)
#         return super().form_valid(form)

class MenuView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'shop/main.html')


class ProductAddView(CreateView):
    template_name = 'shop/add_product.html'
    model = Products
    fields = ['name', 'price', 'description', 'number_of_items']
    success_url = reverse_lazy('add product')


class ProductAllView(View):

    def get(self, request, *args, **kwargs):
        products = Products.objects.all()
        arr = []
        for product in products:
            image = Image.objects.filter(product_id=product.pk)
            arr.append((product, image))
        context = {
            "arr": arr,
        }
        return render(request, 'shop/product_list.html', context)


class SearchProductView(LoginRequiredMixin, View):
    login_url = '/menu/login/'

    template_name = 'shop/search_product.html'
    form_class = SearchProductForm

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs, ):
        form = self.form_class(request.POST)
        if form.is_valid():
            name = form.cleaned_data['search_name']
            category = form.cleaned_data['category']
            categories = Category.objects.get(name=category)
            product_by_category = categories.products_set.all()
            products = Products.objects.filter(name__icontains=name)
            context = {
                "products": products,
                "form": form,
                "product_by_category": product_by_category,
            }
            return render(request, self.template_name, context)
        else:
            return render(request, self.template_name, {'form': form})


class ProductDetailsView(LoginRequiredMixin,View):

    def get(self, request, *args, **kwargs):
        choose_product = Products.objects.get(pk=kwargs['id'])
        images = Image.objects.filter(product_id=choose_product.pk)
        context = {
            "product": choose_product,
            "images": images,
        }
        return render(request, 'shop/product_details.html', context)

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            choose_user = Users.objects.filter(user=user).values()
            if len(choose_user) == 0:
                new_user = Users.objects.create(user=user)
                choose_user = Users.objects.filter(user=user).values()
            choose_product = Products.objects.get(pk=kwargs['id'])
            choose_basket = Basket.objects.filter(status=1,my_user_id=choose_user[0]['id']).values()
            delivery = Delivery.objects.get(pk=1)
            if len(choose_basket) == 0:
                new_basket = Basket.objects.create(status=1,my_user=Users.objects.get(pk=choose_user[0]['id']),delivery_method=delivery)
                product = ProductBasket.objects.create(product_id=choose_product.id, basket_id=new_basket.id)
            else:
                product = ProductBasket.objects.create(product_id=choose_product.id,basket_id=choose_basket[0]['id'])
            context = {
                'product': product,
                'choose_product': choose_product,
                }
            return render(request, 'shop/product_details.html', context)


class UserView(FormView):
    template_name = 'shop/login.html'
    form_class = UserForm
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        cd = form.cleaned_data
        user = authenticate(username=cd['username'], password=cd['password'])
        if user.is_authenticated:
            login(self.request, user)
            return super().form_valid(form)


class AddUserView(CreateView):
    model = User
    template_name = 'shop/add_user.html'
    success_url = reverse_lazy('login')
    form_class = UserCreateForm

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.set_password(form.cleaned_data['password1'])
        self.object.save()
        return response


class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('login')


class BasketView(View):
    template_name = 'shop/basket.html'
    form_class = DeliveryForm

    def get(self, request, *args, **kwargs):
        my_basket = Basket.objects.filter(status=1,my_user=Users.objects.get(user_id = request.user.id)).values()
        if len(my_basket) == 0:
            return HttpResponse("Nie masz jeszcze utworzonego koszyka. Dodaj produkt by utworzyć koszyk")
        basket_id = my_basket[0]['id']
        products = ProductBasket.objects.filter(basket_id=basket_id).values()
        arr=[]
        price = 0
        for product in products:
            arr.append(Products.objects.get(pk=product[0]['id']))
            price = Products.objects.get(pk=product[0]['id']).price + price
        form = self.form_class
        context = {
            'products': arr,
            "basket": my_basket,
            "form": form,
            "price": price,
        }
        return render(request, self.template_name, context)

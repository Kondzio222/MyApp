from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.views.generic import FormView, CreateView
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User,Permission
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SearchProductForm, UserForm, UserCreateForm, PaymentForm
from .models import Products, Category, Image, Basket, ProductBasket, Users, Delivery





class MenuView(View):
    """
     You can choose to register user or login into shop
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'shop/main.html')


class ProductAddView(CreateView):
    """
    Create new product into database
    """

    template_name = 'shop/add_product.html'
    model = Products
    fields = ['name', 'price', 'description', 'number_of_items']
    success_url = reverse_lazy('add product')


class ProductAllView(View):
    """
    Show all product which you can buy on webshop
    """
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
    """
    It's possible to search product by categories.
    Only for Users being log in.
    """

    def get_login_url(self):
        return 'login'

    template_name = 'shop/search_product.html'
    form_class = SearchProductForm

    """
    View which show SearchProductForm 
    """
    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.template_name, {"form": form})
    """
    Use Category to find Products
    """
    def post(self, request, *args, **kwargs, ):
        form = self.form_class(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            categories = Category.objects.get(name=category)
            product_by_category = categories.products_set.all()
            context = {
                "form": form,
                "product_by_category": product_by_category,
            }
            return render(request, self.template_name, context)
        else:
            return render(request, self.template_name, {'form': form})


class ProductDetailsView(LoginRequiredMixin, View):
    """
    Show Products details like price, description
    """
    def get_login_url(self):
        return 'login'

    def get(self, request, *args, **kwargs):
        choose_product = Products.objects.get(pk=kwargs['id'])
        images = Image.objects.filter(product_id=choose_product.pk)
        context = {
            "product": choose_product,
            "images": images,
        }
        return render(request, 'shop/product_details.html', context)

    """
    Give oportunity to create Basket by add first product.
    """
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            choose_user = Users.objects.filter(user=user).values()
            if len(choose_user) == 0:
                Users.objects.create(user=user)
                choose_user = Users.objects.filter(user=user).values()
            choose_product = Products.objects.get(pk=kwargs['id'])
            choose_basket = Basket.objects.filter(status=1, my_user_id=choose_user[0]['id']).values()
            delivery = Delivery.objects.create(address='Nie ma',payment_method=1)
            if len(choose_basket) == 0:
                new_basket = Basket.objects.create(status=1, my_user=Users.objects.get(pk=choose_user[0]['id']),
                                                   delivery_method=delivery)
                ProductBasket.objects.create(product_id=choose_product.id, basket_id=new_basket.id)
            else:
                ProductBasket.objects.create(product_id=choose_product.id, basket_id=choose_basket[0]['id'])
            return redirect('product_list')


class UserView(FormView):
    """
    Site where can log in by django.auth.
    """

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
    """
    Create User to django.auth User
    """
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
    """
    User can log out and don't had permission to see all views
    """
    def get(self, request):
        logout(request)
        return redirect('login')


class BasketView(LoginRequiredMixin, View):
    """
    Only for login Users. Show all products being in Users Basket which is not accepted by himself.
    """
    def get_login_url(self):
        return 'login'

    template_name = 'shop/basket.html'

    def get(self, request, *args, **kwargs):
        choose_user = Users.objects.filter(user=request.user).values()
        if len(choose_user) == 0:
            choose_user = Users.objects.create(user=request.user)
        my_basket = Basket.objects.filter(status=1, my_user=choose_user[0]['id']).values()
        if len(my_basket) == 0:
            return HttpResponse("Nie masz jeszcze utworzonego koszyka. Dodaj produkt by utworzyć koszyk")
        basket_id = my_basket[0]['id']
        products = ProductBasket.objects.filter(basket_id=basket_id).values()
        arr = list(products)
        price = 0
        arr_products = []
        for product in arr:
            prod = Products.objects.get(pk=product['product_id'])
            arr_products.append((prod, product['id']))
            price = prod.price + price
        context = {
            'products': arr_products,
            "basket": my_basket,
            "price": price,

        }
        return render(request, self.template_name, context)


class DeliveryPaymentView(LoginRequiredMixin, View):
    """
    Only for login User. Render PaymentForm
    """

    def get_login_url(self):
        return 'login'

    template_name = 'shop/delivery.html'
    form_class = PaymentForm

    def get(self, request, *args, **kwargs):
        my_basket = Basket.objects.filter(status=1, my_user=Users.objects.get(user_id=request.user.id)).values()
        basket_id = my_basket[0]['id']
        products = ProductBasket.objects.filter(basket_id=basket_id).values()
        price = 0
        for product in products:
            prod = Products.objects.get(pk=product['product_id'])
            price = prod.price + price
        form = self.form_class
        context = {
            "form": form,
            "price": price
        }
        return render(request, self.template_name, context)

    """
    Create and update delivery method and address
    """
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            address = cd['address']
            payment = cd['payment']
            basket = Basket.objects.filter(status=1, my_user=Users.objects.get(id=request.user.id)).values()
            delivery = Delivery.objects.create(address=address, payment_method=payment)
            basket.update(delivery_method_id=delivery.id, status=2)
            return HttpResponse('Twoje zamówienie zostało wykonane')

    """
    Let delete products from basket belongs to user 
    """
def delete_product(request, *args, **kwargs):
    basket = Basket.objects.filter(status=1, my_user=Users.objects.get(user_id=request.user.id)).values()
    product = ProductBasket.objects.filter(basket_id=basket[0]['id']).filter(id=kwargs['id'])
    product.delete()
    return redirect('basket')

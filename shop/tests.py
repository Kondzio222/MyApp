from django.test import TestCase
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

from django.db.utils import IntegrityError

from shop.models import Products, Users, Category, Delivery,Basket



# Create your tests here.

class ProductAddView(TestCase):
    def test_template(self):
        response = self.client.get('/menu/addproduct')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/add_product.html')

    def test_add_some_product(self):
        test_object = {
            'name': 'test_name',
            'price': 123,
            'description': 'test description',
            'number_of_items': 99
        }

        self.client.post('/menu/addproduct', test_object)
        created_object = Products.objects.last()

        self.assertEqual(created_object.name, test_object['name'])
        self.assertEqual(created_object.price, test_object['price'])
        self.assertEqual(created_object.description, test_object['description'])
        self.assertEqual(created_object.number_of_items, test_object['number_of_items'])

class ProductAllViewTest(TestCase):
    number_of_products = 5

    @classmethod
    def setUpTestData(cls):
        for i in range(0, cls.number_of_products):
            Products.objects.create(name=f"product_{i}", price=i, number_of_items=999)

    def test_list_products(self):
        response = self.client.get('/menu/product_list')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_list.html')


    def test_list_products_multiple_products(self):
        response = self.client.get('/menu/product_list')

        self.assertEqual(len(response.context[0]['arr']), self.number_of_products)
        for i in range(0, self.number_of_products):
            self.assertEqual(response.context[0]['arr'][i][0].name, f"product_{i}")

class SearchProductViewTest(TestCase):
    number_of_products = 5

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='test_user')
        user.set_password('test_pass')
        user.save()

        for i in range(0, cls.number_of_products):
            Products.objects.create(
                name=f"product_{i}",
                price=i,
                number_of_items=999,
            )

    def test_get_page_without_login(self):
        response = self.client.get('/menu/search')
        self.assertEqual(response.status_code, 302)

    def test_get_page_login(self):
        client = Client()
        logged_in = client.login(username='test_user', password='test_pass')
        self.assertTrue(logged_in)

        response = client.get('/menu/search')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/search_product.html')

    def test_post_search(self):
        client = Client()
        logged_in = client.login(username='test_user', password='test_pass')
        self.assertTrue(logged_in)

        response = client.post('/menu/search', {'search_name': 'product'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/search_product.html')

class ProductDetailsViewTest(TestCase):

    test_product = {
        'name': 'test_product',
        'price': 123,
        'number_of_items': 999
    }

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='test_user')
        user.set_password('test_pass')
        user.save()

        Products.objects.create(
            name=cls.test_product['name'],
            price=cls.test_product['price'],
            number_of_items=cls.test_product['number_of_items'],
        )

        Delivery.objects.create(
            address="Dluga 1",
            payment_method=2
        )

    def test_get_page_without_login(self):
        response = self.client.get('/menu/product/1')
        self.assertEqual(response.status_code, 302)

    def test_get_page_with_login(self):
        client = Client()
        logged_in = client.login(username='test_user', password='test_pass')
        self.assertTrue(logged_in)

        response = client.get('/menu/product/7')
        self.assertEqual(response.status_code, 200)

        product_details = response.context[0]['product']

        self.assertEqual(product_details.name, self.test_product['name'])
        self.assertEqual(product_details.price, self.test_product['price'])
        self.assertEqual(product_details.number_of_items, self.test_product['number_of_items'])

    def test_post_product(self):
        client = Client()
        logged_in = client.login(username='test_user', password='test_pass')
        self.assertTrue(logged_in)
        response = client.post('/menu/product/7')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/menu/product_list')


        created_product = Products.objects.last()

        self.assertEqual(created_product.name, self.test_product['name'])
        self.assertEqual(created_product.price, self.test_product['price'])
        self.assertEqual(created_product.number_of_items, self.test_product['number_of_items'])

class UserViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='test_user')
        user.set_password('test_pass')
        user.save()

    def test_get_page_without_login(self):
        response = self.client.get('/menu/login')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/login.html')

    def test_login_incorrect_pass(self):
        response = self.client.post(
            '/menu/login',
            {
                'username': 'test_user',
                'password': 'wrong_password'
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Podaj poprawne dane')

    def test_login_correct_pass(self):
        response = self.client.post(
            '/menu/login',
            {
                'username': 'test_user',
                'password': 'test_pass'
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/menu/product_list')

class CreateUserViewTest(TestCase):
    def test_template(self):
        response =self.client.get('/menu/add_user')

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'shop/add_user.html')

    def test_add_user(self):
        test_user = {
            'username': 'sume_test_user',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'first_name': 'Jan',
            'last_name': 'Kowalski'
        }

        response = self.client.post('/menu/add_user', test_user)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/menu/login')

        user = User.objects.last()
        self.assertEqual(user.username, 'sume_test_user')
        self.assertEqual(user.first_name, 'Jan')
        self.assertEqual(user.last_name, 'Kowalski')

class BasketViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='test_user')
        user.set_password('test_pass')
        user.save()


    def test_template(self):
        response = self.client.get('/menu/basket')

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/menu/login?next=/menu/basket')

    def test_get_page_with_login(self):
        client = Client()
        logged_in = client.login(username='test_user', password='test_pass')
        self.assertTrue(logged_in)
        Users.objects.create(user_id=User.objects.last().id)
        response = client.get('/menu/basket')
        self.assertEqual(response.status_code, 200)


class DeliveryViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='test_user')
        user.set_password('test_pass')
        user.save()

    def test_template(self):
        response = self.client.get('/menu/basket/delivery')

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/menu/login?next=/menu/basket/delivery')



from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError, EmailValidator
from django.contrib.auth import get_user_model, authenticate, password_validation

from .models import Category,PAYMENT

User = get_user_model()


class ProductAddForm(forms.Form):
    name = forms.CharField(max_length=64)
    price = forms.DecimalField(max_digits=6, decimal_places=2)
    description = forms.Textarea()
    number_of_items = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(300)])
    # category = forms.ModelMultipleChoiceField(queryset=Category.objects.all())


class SearchProductForm(forms.Form):
    search_name = forms.CharField(max_length=64, required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), to_field_name='id')


# class UserForm(forms.Form):
#     username = forms.CharField(max_length=64)
#     password = forms.CharField(max_length=64)
#     email = forms.EmailField(max_length=128, validators=[EmailValidator])


class UserForm(forms.Form):
    username = forms.CharField(max_length=128)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cd = super().clean()
        username = cd.get('username')
        password = cd.get('password')
        self.user = authenticate(username=username, password=password)
        if self.user is None:
            raise ValidationError('Podaj poprawne dane')


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')
        help_texts = (
            " "
        )

    def clean(self):
        cd = super().clean()
        pass1 = cd.get('password1')
        pass2 = cd.get('password2')
        password_validation.validate_password(pass1)
        if pass1 != pass2:
            raise ValidationError("Passwords must be the same!!!")


class DeliveryForm(forms.Form):
    address = forms.CharField()
    payment = forms.ChoiceField(choices=PAYMENT)

from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views import View

from django.utils.datastructures import MultiValueDictKeyError

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.models import User

from django.http import JsonResponse

from .encryptors import account_activation_token
from django.utils.encoding import force_text

from .forms import UserSignupForm
from .forms import UserSigninForm
from .forms import CommentForm
from .forms import DeleteForm
from .forms import LikeForm
from .forms import DislikeForm
from .forms import ProductInfoForm

from .models import Product
from .models import Comment
from .models import Like
import requests

from backend_server.models import BackendLike
from backend_server.models import BackendProduct

import requests
import os


@method_decorator(login_required, name='post')
class CreateProductView(View):
    model = Product

    def post(self, request, *args, **kwargs):
        user = self.request.user
        product_id = self.model.objects.create_product(user.id)
        return redirect('../changeproduct/{}'.format(product_id))


class RecommendationsView(ListView):
    template_name = 'frontend_server/index.html'
    context_object_name = 'products'
    model = Product
    PAGE_SIZE = 35

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            page = int(self.request.GET['page'])
        except MultiValueDictKeyError:
            page = 1

        if self.request.user.is_authenticated:
            context['products'] = self.model.objects.for_registered_user(self.request.user.id,
                                                                         page)
        else:
            context['products'] = self.model.objects.for_anonymous_user(page)

        context['next_page_number'] = page + 1
        context['next_page_exists'] = len(context['products']) > self.PAGE_SIZE
        context['products'] = context['products'][:self.PAGE_SIZE]
        context['user'] = self.request.user

        if self.request.user.is_authenticated:
            for product in context['products']:
                # for negative statistics
                Product.objects.visit(context['user'].id, product.id)

        return context

    def get_queryset(self):
        return []


@method_decorator(login_required, name='post')
class LikeView(View):
    model = Like

    def post(self, request):
        form = LikeForm(request.POST)

        product_id = int(form.data['product_id'])
        user_id = request.user.id

        print('like {} by {}'.format(product_id, user_id))

        self.model.objects.set_like(
            user_id,
            product_id
        )

        return JsonResponse("good", safe=False)


@method_decorator(login_required, name='post')
class DislikeView(View):
    model = Like

    def post(self, request):
        form = DislikeForm(request.POST)

        product_id = int(form.data['product_id'])
        user_id = request.user.id

        print('dislike {} by {}'.format(product_id, user_id))

        self.model.objects.set_dislike(
            user_id,
            product_id
        )

        return JsonResponse("good", safe=False)


@method_decorator(login_required, name='post')
@method_decorator(login_required, name='get')
class ChangeProductView(View):
    model = Product

    def get(self, request, *args, **kwargs):
        product = self.model.objects.product_info(self.kwargs['product_id'], 0)
        user = self.request.user

        product_data = {
            'name': product.name,
            'description': product.description,
            'product_id': product.id,
            'image_url': product.image_url
        }
        form = ProductInfoForm(data=product_data)

        context = {
            'form': form,
            'product': product,
            'user': user,
            'user_is_owner': product.owner == user
        }

        return render(request, 'frontend_server/change_product.html', context)

    def post(self, request, *args, **kwargs):
        form = ProductInfoForm(request.POST)
        product = self.model.objects.product_info(self.kwargs['product_id'], 0)
        user = self.request.user

        context = {
            'form': form,
            'product': product,
            'user': user,
            'user_is_owner': product.owner == user
        }

        if form.is_valid():
            description = form.data['description']
            product_id = int(form.data['product_id'])
            image_url = form.data['image_url']
            name = form.data['name']
            user_id = request.user.id

            myfile = requests.get(image_url) 
            file_name = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend_server', 'static', 'frontend_server', 'images', image_url[(image_url.rindex('/')+1):])
            #file_name = 'C:/wannait/frontend_server/static/frontend_server/images/' + image_url[(image_url.rindex('/')+1):]
            open(file_name, 'wb').write(myfile.content)
            #image_url = image_url[(image_url.rindex('/')+1):]
            #file:///C:/wannait/frontend_server/static/frontend_server/images/9O7gLzmreU0nGkIB6K3BsJbzvNv.jpg
            #image_url = 'file://localhost/C:/wannait/frontend_server/static/frontend_server/images/'+ image_url[(image_url.rindex('/')+1):]

            self.model.objects.change_product(
                user_id,
                product_id,
                image_url,
                name,
                description
            )
            return redirect('../info/{}'.format(product_id))
        else:
            return render(request, 'frontend_server/change_product.html',
                          context)


@method_decorator(login_required, name='post')
class CommentView(View):
    model = Comment

    def post(self, request):
        form = CommentForm(request.POST)

        text = form.data['text']
        product_id = int(form.data['product_id'])
        user_id = request.user.id

        self.model.objects.add_comment(product_id, user_id, text)

        return redirect('../info/{}'.format(product_id))


@method_decorator(login_required, name='post')
class DeleteProductView(View):
    model = Product

    def post(self, request):
        form = DeleteForm(request.POST)

        product_id = int(form.data['product_id'])
        user_id = request.user.id

        if self.model.objects.delete_product(user_id, product_id):
            return HttpResponseRedirect(
                reverse(
                    'frontend_server:owned'
                )
            )
        else:
            return redirect('../info/{}'.format(product_id))


@method_decorator(login_required, name='get')
class OwnedProductsView(ListView):
    template_name = 'frontend_server/owned.html'
    context_object_name = 'products'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user'] = self.request.user

        return context

    def get_queryset(self):
        owner_id = self.request.user.id

        return self.model.objects.for_owner(owner_id)


class ProductInfoView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'frontend_server/product_info.html'

    def get_context_data(self, **kwargs):
        product_id: int = self.kwargs['id']
        user = self.request.user
        user_id = user.id if user.is_authenticated else 0

        context = super().get_context_data(**kwargs)

        context['product'] = Product.objects.product_info(product_id, user_id)
        users_liked = [like.owner for like in BackendLike.objects.filter(product_id=product_id)]
        users_liked.reverse()
        context['users_liked'] = users_liked

        context['user'] = user
        context['user_is_owner'] = context['product'].owner.id == user_id
        context['like'] = context['product'].like
        context['comments'] = context['product'].comments
        context['comment_form'] = CommentForm()

        return context

    def get_object(self, queryset=None):
        product_id: int = self.kwargs['id']
        user = self.request.user
        user_id = user.id if user.is_authenticated else 0

        # for negative statistics
        if user.is_authenticated:
            Product.objects.visit(user_id, product_id)

        return Product.objects.product_info(product_id, user_id)


def login_view(request):
    next_page = request.GET.get('next')
    form = UserSigninForm(request.POST or None)
    context = {}

    if form.is_valid():
        username = form.cleaned_data.get('login')
        password = form.cleaned_data.get('password')

        user = authenticate(username=username, password=password)
        login(request, user)

        if next_page:
            return redirect(next_page)
        return redirect('/')
    else:
        try:
            context['form_error'] = "\n".join(form.errors['__all__'])
        except BaseException:
            pass

    context['form'] = form

    return render(request, "frontend_server/signin.html", context)


def register_view(request):
    next_page = request.GET.get('next')
    form = UserSignupForm(request.POST or None)
    context = {}

    if form.is_valid():
        username = form.cleaned_data.get('login')
        password = form.cleaned_data.get('password')
        email = form.cleaned_data.get('email1')

        user = User.objects.create_user(username, email, password)
        login(request, user)

        if next_page:
            return redirect(next_page)
        return redirect('/')
    else:
        try:
            context['form_error'] = "\n".join(form.errors['__all__'])
        except BaseException:
            pass

    context['form'] = form

    return render(request, "frontend_server/signup.html", context)


@login_required
def logout_view(request):
    logout(request)
    return redirect('/')


def recovery_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            mail_subject = 'Password recovery.'
            message = render_to_string('frontend_server/confirm_email.html', {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            EmailMessage(mail_subject, message, to=[user.email]).send()
            return render(request, "frontend_server/send_email.html")
        except BaseException:
            return render(request, "frontend_server/recovery.html")
    else:
        return render(request, "frontend_server/recovery.html")


def change_password_view(request, index, token):
    if request.method == 'POST':
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if (password1 == password2):
            uid = force_text(urlsafe_base64_decode(index))
            try:
                user = User.objects.get(pk=uid)
                user.set_password(password1)
                user.save()
                return render(
                    request, "frontend_server/change_password_confirm.html")
            except BaseException:
                pass
    else:
        return render(request, "frontend_server/change_password.html")


def profile_view(request, user_id):
    user = User.objects.get(pk=user_id)
    owned_products = Product.objects.for_owner(user_id)
    liked_products = [
        like.product for like in BackendLike.objects.filter(
            owner=user_id)]

    context = {'viewed_user': user,
               'owned_products': owned_products,
               'liked_products': liked_products
               }
    return render(request, "frontend_server/user_profile.html", context)

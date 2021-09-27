# from django import views
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from taggit.models import Tag
from .models import Post
from .forms import SigUpForm, SignInForm, FeedBackForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import BadHeaderError, send_mail
from django.conf import settings


class MainView(View):

    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()
        paginator = Paginator(posts, 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj': page_obj}
        path = 'blog_app/home.html'
        return render(request, path, context)


class PostDetailView(View):

    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, url=slug)
        common_tags = Post.tag.most_common()
        last_posts = Post.objects.all().order_by('-id')[:5]
        context = {
            'post': post,
            'common_tags': common_tags,
            'last_posts': last_posts,
        }
        path = 'blog_app/post_detail.html'
        return render(request, path, context)


class SignUpView(View):

    def get(self, request, *args, **kwargs):
        form = SigUpForm()
        path = 'blog_app/signup.html'
        context = {'form': form}
        return render(request, path, context)

    def post(self, request, *args, **kwargs):
        form = SigUpForm(request.POST)
        path = 'blog_app/signup.html'
        context = {'form': form}
        if form.is_valid():
            user = form.save()
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
        return render(request, path, context)


class SignInView(View):
    def get(self, request, *args, **kwargs):
        form = SignInForm()
        path = 'blog_app/signin.html'
        context = {'form': form}
        return render(request, path, context)

    def post(self, request, *args, **kwargs):
        form = SignInForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
        path = 'blog_app/signin.html'
        context = {'form': form, }
        return render(request, path, context)


class FeedBackView(View):
    def get(self, request, *args, **kwargs):
        form = FeedBackForm()
        path = 'blog_app/contact.html'
        context = {
            'form': form,
            'title': 'Написать мне'
        }
        return render(request, path, context)

    def post(self, request, *args, **kwargs):
        form = FeedBackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            collected_string = f'От {name} | {subject}'
            try:
                send_mail(collected_string, message, from_email,
                          settings.MAILS_FOR_FEEDBACK)
            except BadHeaderError:
                return HttpResponse('Невалидный заголовок')
            return HttpResponseRedirect('success')
        path = 'blog_app/contact.html'
        context = {'form': form}
        return render(request, path, context)


class SuccessView(View):
    def get(self, request, *args, **kwargs):
        path = 'blog_app/success.html'
        context = {'title': 'Спасибо'}
        return render(request, path, context)


class SearchResultsView(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('q')
        results = ''
        if query:
            results = Post.objects.filter(
                Q(h1__icontains=query) | Q(content__icontains=query)
            )
        paginator = Paginator(results, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        path = 'blog_app/search.html'
        context = {
            'title': 'Поиск',
            'page_obj': page_obj,
            'count': paginator.count
        }
        return render(request, path, context)


class TagView(View):
    def get(self, request, slug, *args, **kwargs):
        tag = get_object_or_404(Tag, slug=slug)
        posts = Post.objects.filter(tag=tag)
        common_tags = Post.tag.most_common()
        path = 'blog_app/tag.html'
        context = {
            'title': f'#ТЕГ {tag}',
            'page_obj': posts,
            'common_tags': common_tags
        }
        return render(request, path, context)

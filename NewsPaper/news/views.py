from datetime import timedelta, datetime

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, resolve, reverse
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.core.paginator import Paginator  # импортируем класс, позволяющий удобно осуществлять постраничный вывод
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin  # миксин, проверка наличия аутентификации пользователя
from .filters import PostFilter
from .forms import PostForm
from .models import Post, Author, Category


# DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


class News(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-timePost')
    paginate_by = 10

    def get_queryset(self) -> QuerySet(any):
        post_filter = PostFilter(self.request.GET, queryset=Post.objects.all())
        return post_filter.qs.order_by('-timePost')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = timezone.localtime(timezone.now())  # добавим переменную текущей даты time_now
        context['filter'] = PostFilter(self.request.GET,
                                       queryset=self.get_queryset())  # вписываем фильтр в контекст
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)  # создаём новую форму, забиваем в неё данные из POST-запроса
        if form.is_valid():
            form.save()
        return super().get(request, *args, **kwargs)


class PostList(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    queryset = Post.objects.all()


class Search(ListView):
    model = Post
    template_name = 'search.html'
    queryset = Post.objects.order_by('-timePost')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


class PostCreate(PermissionRequiredMixin, CreateView):
    template_name = 'post_create.html'
    form_class = PostForm
    permission_required = 'news.add_Post'
    context_object_name = 'news'

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)
        self.object = form.save()
        self.category_list = self.object.category.all()

        for category in self.category_list:

            for sub in category.subscribers.all():
                html_content = render_to_string(
                    'mail.html',
                    {
                        'user': sub,
                        'post': self.object,
                    }
                )

                msg = EmailMultiAlternatives(
                    subject=f'{self.object.title}',
                    body=self.object.textPost,
                    from_email='kuchinsk93@yandex.ru',
                    to=[f'{sub.email}'],
                )
                msg.attach_alternative(html_content, "text/html")  # добавляем html
                msg.send()  # отсылаем
                print(html_content)

        return HttpResponseRedirect(self.get_success_url())


    def form_valid(self, form):

        super().form_valid(form)
        author = Author.objects.get(authorUser_id=self.request.user.id)
        yesterday = datetime.now() - timedelta(days=1)
        post_day = Post.objects.filter(author=author, timePost__gt=yesterday).count()

        if post_day > 3:
            return redirect('news:post_list')



class PostEdit(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'post_edit.html'
    form_class = PostForm
    permission_required = 'news.change_Post'

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDelete(DeleteView):
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = reverse_lazy('news:post_list')


class AddProduct(PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_post'


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(id=self.kwargs['pk'])
        context['subscribers'] = category.subscribers.all()
        return context


def subscribe(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.add(request.user.id)
    return redirect('news:post_list')
    # return HttpResponseRedirect(reverse('category', args=[pk]))


def unsubscribe(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.remove(request.user.id)
    return redirect('news:post_list')
    # return HttpResponseRedirect(reverse('category', args=[pk]))





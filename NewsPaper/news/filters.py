import django_filters
from .models import Post


class PostFilter(django_filters.FilterSet):
    timePost = django_filters.DateFilter(
        field_name='timePost',
        label='Создан позднее чем:',
        input_formats=['%d-%m-%Y', '%d.%m.%Y'],
        lookup_expr='gt',
    )
    title = django_filters.CharFilter(
        field_name='title',
        label='Заголовок',
        lookup_expr='icontains'
    )
    author = django_filters.CharFilter(
        field_name='author__authorUser__username',
        label='Автор',
        lookup_expr='iregex'
    )

    class Meta:
        model = Post
        fields = ['timePost', 'title', 'author']

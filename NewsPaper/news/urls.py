from django.urls import path
from .views import News, PostList, Search, PostCreate, PostEdit, PostDelete, CategoryDetailView, subscribe, unsubscribe

app_name = 'news'
urlpatterns = [
    path('', News.as_view(), name='post_list'),
    path('<int:pk>/', PostList.as_view(), name='post'),
    path('search/', Search.as_view(), name='post_search'),
    path('add/', PostCreate.as_view(), name='post_add'),
    path('<int:pk>/edit/', PostEdit.as_view(), name='post_edit'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='category'),
    path('subscribe/<int:pk>', subscribe, name='subscribe'),
    path('unsubscribe/<int:pk>', unsubscribe, name='unsubscribe'),
]
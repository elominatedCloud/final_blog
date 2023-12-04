from django.urls import path
from . import views

app_name = 'mypage'

urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('write/', views.post_write, name='write'),
    path('about/', views.about, name="about"),
    # views.post_detail를 통해 가져온 post_id 정보를 바탕으로 url 구성
    # posts/1 -> post_id = 1 인 상세페이지로 이동
    path('posts/<int:post_id>/', views.post_detail, name="posts"),
    # 위와 동일
    path('category/<str:cate_name>/', views.category, name='category'),
    path('option/', views.category_option, name='category option'),
    path('option/delete/<int:category_id>', views.category_delete, name='category delete'),
    path('option/modify/<int:category_id>', views.category_modify, name='category modify'),
    path('modify/<int:post_id>/', views.modify, name="modify"),
    path('delete/<int:post_id>/', views.delete, name="delete"),
    path('comment/<int:comments_id>/', views.delete_comment, name="delete_comment"),
]
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

class User(AbstractUser):
    full_name = models.CharField(max_length=255, default="Unknown")
    email = models.EmailField(default = "anonymous@unknown_mails.com")
    # 기본적으로 password 필드가 이미 User 모델에 존재합니다. 따라서 추가적인 password 필드는 필요하지 않습니다.

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.user.username

class Category(models.Model):
    cate_name = models.CharField(max_length=50)

    def __str__(self):
        return self.cate_name

class Post(models.Model):
    cate = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    p_title = models.CharField(max_length=50)
    p_desc = models.CharField(max_length=100)
    p_contents = models.TextField()
    p_created = models.DateTimeField(auto_now_add=True, null=True)
    p_updated = models.DateTimeField(default=None, null=True)
    thumbnail = models.ImageField(upload_to="post", blank=True)

    def __str__(self):
        return self.p_title

class Comments(models.Model):
    p = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    c_user_id = models.CharField(max_length=20)
    c_user_pw = models.CharField(max_length=20)
    c_contents = models.TextField()
    c_created = models.DateTimeField(auto_now_add=True)
    c_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.c_contents
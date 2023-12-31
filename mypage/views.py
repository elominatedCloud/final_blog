from django.shortcuts import render, redirect

# https://velog.io/@may_soouu/%EC%9E%A5%EA%B3%A0-Annotate-Aggregate 
from django.db.models import Count, F
from django.db.models.functions import Lower

from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Category, Post, Comments, UserProfile, User
from .forms import UserForm

from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib import messages
import datetime


# index.html / 메인페이지
def main(request):
    # categorys에 post_count 변수명으로 post의 개수 정보 추가
    categorys = Category.objects.annotate(post_count=Count('post')).order_by('cate_name')
    # posts에 comments_count 변수명으로 comment의 개수 정보 추가 + 역순으로 출력시켜 최신순으로 보이도록 함
    # category_title에 외래키 정보인 category 테이블의 cate_name 정보를 category_title에 입력시켜 줌
    posts = Post.objects.annotate(comments_count=Count('comments'), category_title=F('cate__cate_name')).order_by('-id')
    # 현재 시간 반환
    current_time = timezone.now()

    # 전체 포스트의 개수를 세기 위한 all_post 변수
    all_post = 0
    for category in categorys:
        all_post += category.post_count
    
    context = {'categorys': categorys, 'posts' : posts, 'current_time': current_time, 'all_post' : all_post}
    return render(request, 'mypage/index.html', context)

# category.html / 카테고리 선택 페이지
def category(request, cate_name):
    # lower_name 변수에 Category 테이블의 cate_name 데이터를 모두 소문자화시켜 넣어줌
    categorys = Category.objects.annotate(post_count=Count('post'), lower_name=Lower('cate_name')).order_by('cate_name')

    # 카테고리를 눌렀을 때 해당 카테고리에 포함되어 있는 post만 출력시키는 기능을 위함
    for cate in categorys:
        # cate_name이 소문자로 되어있기 때문에 lower()함수를 사용해 소문자로 변경해줌
        if cate.cate_name.lower() == cate_name:
            category_id = cate.id
            
    posts = Post.objects.filter(cate_id=category_id).annotate(comments_count=Count('comments'), category_title=F('cate__cate_name')).order_by('-id')
    
    all_post = 0
    for category in categorys:
        all_post += category.post_count

    context = {'categorys' : categorys, 'posts' : posts, 'cate_name' : cate_name, 'all_post' : all_post}
    return render(request, 'mypage/category.html', context)

# login.html / 로그인 페이지
def login_view(request):
    
    if request.method == "POST":
        username = request.POST['u_id']
        password = request.POST['u_pw']

        # username과 password가 일치한지 확인
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect('/')
        else:
            print("login failed")

    return render(request, 'mypage/login.html')

# 로그아웃은 따로 페이지가 필요없음
def logout_view(request):

    logout(request)

    return redirect('/')

# 회원가입 구현
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)  # 사용자 인증
            login(request, user)  # 로그인
            return redirect('/')
    else:
        form = UserForm()
    return render(request, 'mypage/signup.html', {'form': form})

# detail.html / 포스트 상세 페이지
def post_detail(request, post_id):
    # 특정 post를 클릭했을 때 해당 Post의 상세 페이지로 이동시키기 위함
    post = Post.objects.annotate(category_title=F('cate__cate_name')).get(id=post_id)
    categorys = Category.objects.all()

    # 만약 POST method를 요청했을 때 수행되는 구문
    # 상세페이지를 들어갔을 때 DB에서 정보를 가져오기 위해 GET을 하게 되는데 해당 조건문을 달지않으면 상세페이지를 들어갈 때마다 POST를 수행하기 때문에 빈 값을 보내게 되어 오류 발생
    if request.method == "POST":
        # detail.html에 있는 input의 name값을 기반으로 value를 가져옴
        comment_content = request.POST["comment"]
        comment_user_id = 'None'
        # comment_id = request.POST["comment_id"]
        # comment_pw = request.POST["comment_pw"]

        if request.user.is_authenticated:
            # 로그인한 사용자의 경우 사용자 이름 사용
            comment_author = request.user
            anonymous_author = None
        else:
            # 비로그인 사용자의 경우 '익명'과 IP 주소의 첫 3자리 사용
            comment_author = None
            anonymous_author = '익명({})'.format(request.META.get('REMOTE_ADDR', '')[:3])


        Comments.objects.create(
            author=comment_author,  # 댓글 작성자를 저장
            anonymous_author=anonymous_author,
            p_id = post_id,
            c_contents = comment_content,
            # c_user_id = comment_id,
            # c_user_pw = comment_pw,
            c_created = timezone.now(),
            # c_updated = timezone.now()

        )
        
    context = {'post' : post, 'categorys' : categorys}
    return render(request, 'mypage/detail.html', context)

# write.html / 포스트 작성 페이지
def post_write(request):
    categorys = Category.objects.all()
    context = {'categorys' : categorys}

    # 위와 동일
    if request.method == "POST":
        cate = request.POST["categorys"]
        title = request.POST["title"]
        description = request.POST["description"]    
        content = request.POST["content"]

        # 썸네일 이미지 파일을 가져오기 위함
        # 예외구문을 사용하지 않고 썸네일을 넣지 않는 경우 오류 발생
        # 따라서 썸네일을 넣지 않는 경우에는 None을 입력
        try:
            thumbnail = request.FILES["thumbnail"]
        except:
            thumbnail = None

        post = Post.objects.create(
            cate_id = int(cate),
            p_title = title,
            p_desc = description,
            p_contents = content,
            p_created = datetime.datetime.now(),
            thumbnail = thumbnail,
            author=request.user  # 현재 로그인한 사용자를 작성자로 설정 # 추가된 부분
        )
        # redirect를 통해 게시글 작성을 완료하면 해당 post 상세페이지로 이동
        return redirect(f"/posts/{post.id}")
    
    return render(request, 'mypage/write.html', context)

# modify.html / 포스트 수정 페이지
def modify(request, post_id):
    post = Post.objects.get(id=post_id)
    categorys = Category.objects.all()
    
    # 위와 동일
    if request.method == "POST":
        post.cate_id = request.POST["categorys"]
        post.p_title = request.POST["title"]
        post.p_desc = request.POST["description"]    
        post.p_contents = request.POST["content"]
        post.p_updated = timezone.now()

        # 썸네일 이미지 파일을 가져오기 위함
        # 이때 썸네일을 수정하지 않는 경우 기존의 썸네일을 가져가도록 하기 위함
        try:
            post.thumbnail = request.FILES["thumbnail"]
        except:
            post.thumbnail = post.thumbnail
        # 포스트 내용 업데이트
        post.save()
        # redirect를 통해 게시글 작성을 완료하면 해당 post 상세페이지로 이동
        return redirect(f"/posts/{post.id}")

    context = {'post' : post, 'categorys' : categorys}
    return render(request, 'mypage/modify.html', context)

# 포스트 삭제
def delete(request, post_id):
    # 해당 포스트에 대한 정보만 가져오기 위함
    post = Post.objects.get(id=post_id)
    # 해당 포스트 삭제
    post.delete()
    # 포스트를 삭제한 뒤 메인페이지로 이동
    return redirect('/')

# 댓글 삭제
def delete_comment(request, comments_id):
    # 해당하는 댓글에 대한 정보만 가져오기 위함
    comment = Comments.objects.get(id=comments_id)
    
    # comment = get_object_or_404(Comments, id=comments_id)

    # 로그인한 사용자가 댓글 작성자이거나 스태프, 관리자인지 확인
    if request.user == comment.author or request.user.is_staff or request.user.is_superuser:
        # 댓글 삭제
        comment.delete()

        # 댓글을 삭제한 뒤, 댓글이 있었던 포스트로 이동
        return redirect(f"/posts/{comment.p_id}")
    else:
        # 권한이 없는 경우 예외 처리 또는 다른 처리
        return redirect('/')  # 다른 페이지로 리디렉션 또는 권한 없음 메시지 반환

    return render(request, 'mypage/comment_delete.html')

def category_option(request):
    categorys = Category.objects.all().order_by('cate_name')

    if request.method == "POST":
        category_name = request.POST['cate_name']

        Category.objects.create(
            cate_name = category_name
        )

    context = {'categorys' : categorys}
    return render(request, "mypage/category_option.html", context)

def category_delete(request, category_id):
    category = Category.objects.get(id=category_id)
    category.delete()
    return redirect('/option')

def category_modify(request, category_id):
    category = Category.objects.get(id=category_id)
    context = {'category' : category}

    if request.method == "POST":
        category.cate_name = request.POST['cate_name']

        category.save()
        return redirect('/option')
    
    return render(request, 'mypage/category_modify.html', context)

def about(request):

    return render(request, 'mypage/about.html')

# 마이페이지 뷰
@login_required
def my(request):
    if request.method == 'POST':
        user = request.user
        user_form = UserForm(request.POST, instance=user)
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if user_form.is_valid():
            user_form.save()

        if current_password and new_password and confirm_password:
            if check_password(current_password, user.password):
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, '비밀번호가 변경되었습니다.')
                    return redirect('/')  # 인덱스 페이지로 리디렉션
                else:
                    messages.error(request, '새 비밀번호와 확인 비밀번호가 일치하지 않습니다.')
            else:
                messages.error(request, '현재 비밀번호가 올바르지 않습니다.')
        
        return redirect('http://127.0.0.1:8000/my')  # 현재 페이지로 리디렉션
    else:
        user_form = UserForm(instance=request.user)

    context = {
        'user_form': user_form,
    }
    return render(request, 'mypage/my.html', context)




from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event,Guest
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger


# Create your views here.
def index(request):
    return render(request, "index.html")

# 登录动作
def login_action(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)       # 登录
            request.session['user'] = username      # 将session信息记录到浏览器
            response = HttpResponseRedirect('/event_manage/')
            return response
        else:
            return render(request, 'index.html', {'error':'username or password error!'})

# 发布会管理
@login_required
def event_manage(request):
    username = request.session.get('user', '')  # 读取浏览器session
    event_list = Event.objects.all()
    return render(request, "event_manage.html", {'user':username, 'events':event_list})

# 发布会名称搜索
@login_required
def search_name(request):
    username = request.session.get('user', '')
    search_name = request.GET.get('name', '')
    event_list = Event.objects.filter(name__contains=search_name)
    return render(request, "event_manage.html", {'user':username, 'events':event_list})

# 嘉宾管理
@login_required
def guest_manage(request):
    username = request.session.get('user', '')
    guest_list = Guest.objects.all()    # 查询Guest表的所有数据
    paginator = Paginator(guest_list, 2)    # 创建每页2条数据的分页器
    page = request.GET.get('page')      # 通过GET请求获取当前要显示第几页的数据
    try:
        contacts = paginator.page(page)     # 获取第page页的数据
    except PageNotAnInteger:                # 如果没有第page页，抛出PageNotAnInteger异常
        contacts = paginator.page(1)        # 显示第1页的数据
    except EmptyPage:                       # 如果超出页数范围，抛出Empty异常
        contacts = paginator.page(paginator.num_pages)      # 显示最后一页的数据
    return render(request, "guest_manage.html", {'user':username, 'guests':contacts})

# 嘉宾搜索
@login_required
def search_realname(request):
    username = request.session.get('user', '')
    search_realname = request.GET.get('realname', '')
    guest_list = Guest.objects.filter(realname__contains=search_realname)
    paginator = Paginator(guest_list, 2)  # 创建每页2条数据的分页器
    page = request.GET.get('page')  # 通过GET请求获取当前要显示第几页的数据
    try:
        contacts = paginator.page(page)  # 获取第page页的数据
    except PageNotAnInteger:  # 如果没有第page页，抛出PageNotAnInteger异常
        contacts = paginator.page(1)  # 显示第1页的数据
    except EmptyPage:  # 如果超出页数范围，抛出Empty异常
        contacts = paginator.page(paginator.num_pages)  # 显示最后一页的数据
    return render(request, "guest_manage.html", {'user': username, 'guests': contacts})
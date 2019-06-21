from django.db.models import Count
from django.shortcuts import render,get_object_or_404
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
    return render(request, "event_manage.html", {'user': username, 'events': event_list})

# 发布会名称搜索
@login_required
def search_name(request):
    username = request.session.get('user', '')
    search_name = request.GET.get('name', '')
    event_list = Event.objects.filter(name__contains=search_name)
    return render(request, "event_manage.html", {'user': username, 'events': event_list})

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
    return render(request, "guest_manage.html", {'user': username, 'guests': contacts})

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

# 签到页面
@login_required
def sign_index(request, eid):
    event = get_object_or_404(Event, id=eid)
    guest_num = Guest.objects.filter(event_id=eid).aggregate(guest_num =Count('phone'))   # 统计该event的手机guest数量
    signin_num = Guest.objects.filter(event_id=eid,sign=True).aggregate(signin_num=Count('phone'))   # 统计已签到数量
    return render(request, "sign_index.html", {'event': event, 'guest_num': guest_num['guest_num'],
                                               'signin_num': signin_num['signin_num']})

# 签到动作
@login_required
def sign_index_action(request, eid):
    event = get_object_or_404(Event, id=eid)
    phone = request.POST.get('phone', '')
    guest_num = Guest.objects.filter(event_id=eid).aggregate(guest_num=Count('phone'))  # 统计该event的手机guest数量
    signin_num = Guest.objects.filter(event_id=eid, sign=True).aggregate(signin_num=Count('phone'))  # 统计已签到数量
    result = Guest.objects.filter(phone=phone)  # 查询手机号是否在Guest中存在，不存在提示phone error
    if not result:
        return render(request, "sign_index.html", {'event': event, 'hint': 'phone error',
                                                   'guest_num': guest_num['guest_num'],
                                                   'signin_num': signin_num['signin_num']})
    result = Guest.objects.filter(phone=phone, event_id=eid)    # 查询phone与event是否匹配，不存在提示phone与event不匹配
    if not result:
        return render(request, "sign_index.html", {'event': event, 'hint': 'phone and event not match',
                                                   'guest_num': guest_num['guest_num'],
                                                   'signin_num': signin_num['signin_num']})
    result = Guest.objects.get(phone=phone, event_id=eid)   # 获取phone和eid的嘉宾对象，判断其是否签到
    if result.sign:     # 已签到提示已签到
        return render(request, 'sign_index.html', {'event': event, 'hint': 'user has sign in',
                                                   'guest_num': guest_num['guest_num'],
                                                   'signin_num': signin_num['signin_num']})
    else:               # 未签到，将状态修改为已签到，并提示签到成功
        Guest.objects.filter(phone=phone, event_id=eid).update(sign='1')
        return render(request, 'sign_index.html', {'event': event, 'hint': 'sign in success', 'guest': result,
                                                   'guest_num': guest_num['guest_num'],
                                                   'signin_num': signin_num['signin_num'] + 1})


# 退出系统
@login_required
def logout(request):
    auth.logout(request)
    response = HttpResponseRedirect('/index/')
    return response

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sign.models import Event, Guest
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError
import time


# 添加发布会接口
@csrf_exempt    # django 的POST接口需要CSRF验证，添加此装饰器豁免验证
def add_event(request):
    eid = request.POST.get('eid', '')                           # 发布会id
    name = request.POST.get('name', '')                         # 发布会名称
    limit = request.POST.get('limit', '')                       # 限制人数
    status = request.POST.get('status', '')                     # 状态
    address = request.POST.get('address', '')                   # 地址
    start_time = request.POST.get('start_time', '')             # 开始时间

    # 若参数为空，则返回状态码100021，错误信息parameter error
    if eid == '' or name == '' or limit == '' or address == '' or start_time == '':
        return JsonResponse({'status': 100021, 'message': 'parameter error'})
    # 判断发布会id和名称是否存在，若存在返回状态码和提示
    result = Event.objects.filter(id=eid)
    if result:
        return JsonResponse({'status': 100022, 'message': 'Event id already exists'})
    result = Event.objects.filter(name=name)
    if result:
        return JsonResponse({'status': 100023, 'message': 'Event name already exists'})
    # 若发布会status为空，置默认值1
    if status == '':
        status = 1
    # 插入数据，若日期格式错误，返回状态码和提示
    try:
        Event.objects.create(id=eid, name=name, limit=limit, status=int(status), address=address,
                             start_time=start_time)
    except ValidationError:
        error = 'start_time format error. It must be in YYYY-MM-DD HH:MM:SS format.'
        return JsonResponse({'status': 100024, 'message': error})
    return JsonResponse({'status': 200, 'message': 'add event success'})


# 查询发布会接口
def get_event_list(request):
    eid = request.GET.get('eid', '')                            # 发布会id
    name = request.GET.get('name', '')                           # 发布会名称

    # 若id和name都为空，返回状态码和提示
    if eid == '' and name == '':
        return JsonResponse({'status': 100021, 'message': 'parameter error'})
    # 若id不为空，根据id查询结果，结果为空，返回结果为空，不为空，返回结果
    if eid != '':
        event = {}
        try:
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 100022, 'message': 'query result is empty'})
        else:
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time
            return JsonResponse({'status': 200, 'message': 'success', 'data': event})
    if name != '':
        datas = []
        results = Event.objects.filter(name__contains=name)
        if results:
            for r in results:
                event = dict()
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                datas.append(event)
            return JsonResponse({'status': 200, 'message': 'success', 'data': datas})
        else:
            return JsonResponse({'status': 100022, 'message': 'query result is empty'})


# 添加嘉宾接口
@csrf_exempt
def add_guest(request):
    eid = request.POST.get('eid', '')
    realname = request.POST.get('realname', '')
    phone = request.POST.get('phone', '')
    email = request.POST.get('email', '')

    # 若eid，realname，phone为空，则提示参数错误
    if eid == '' or realname == '' or phone == '':
        return JsonResponse({'status': 100021, 'message': 'parameter error'})
    # 判断发布会是否存在,不存在返回发布会id不存在
    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status': 100022, 'message': 'event id null'})
    # 判断发布会状态是否为True，不为True，说明发布会为关闭状态
    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status': 100023, 'message': 'event status is not available'})
    # 判断发布会嘉宾数量是否已达到上限
    event_limit = Event.objects.get(id=eid).limit               # 发布会人数上限
    guest_num = len(Guest.objects.filter(event_id=eid))         # 发布会已添加的人数
    if guest_num >= event_limit:
        return JsonResponse({'status': 100024, 'message': 'event limit is full'})
    # 判断发布会是否已开始
    event_time = Event.objects.get(id=eid).start_time           # 发布会时间
    etime = str(event_time).split(".")[0]
    timearray = time.strptime(etime, "%Y-%M-%D %H:%M:%S")
    e_time = int(time.mktime(timearray))

    now_time = str(time.time())                                 # 当前时间
    ntime = now_time.split(".")[0]
    n_time = int(ntime)

    if n_time >= e_time:
        return JsonResponse({'status': 100025, 'message': 'event has started'})
    # 插入嘉宾数据，若phone存在，则抛出IntegrityError异常，并返回状态码和信息，插入成功返回状态码200
    try:
        Guest.objects.create(realname=realname, phone=phone, email=email, sign=0, event_id=eid)
    except IntegrityError:
        return JsonResponse({'status': 100026, 'message': 'the event guest phone number repeat'})
    return JsonResponse({'status': 200, 'message': 'add guest success'})


# 查询嘉宾接口
def get_guest_list(request):
    eid = request.GET.get('id', '')
    phone = request.GET.get('phone', '')

    # 若eid为空，返回状态码和错误提示
    if eid == '':
        return JsonResponse({'status': 100021, 'message': 'eid can not empty'})
    # 若eid不为空，phone为空，返回所有guest信息
    if eid != '' and phone == '':
        datas = []
        results = Guest.objects.filter(event_id=eid)
        if results:
            for g in results:
                guest = dict()
                guest['realname'] = g.realname
                guest['phone'] = g.phone
                guest['email'] = g.email
                guest['sign'] = g.sign
                datas.append(guest)
            return JsonResponse({'status': 200, 'message': 'success', 'data': datas})
        else:
            return JsonResponse({'status': 100022, 'message': 'query result is empty'})
    # 若eid不为空且phone不为空，返回guest信息
    if eid != '' and phone != '':
        guest = {}
        try:
            result = Guest.objects.get(event_id=eid, phone=phone)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 100022, 'message': 'query result is empty'})
        else:
            guest['realname'] = result.realname
            guest['phone'] = result.phone
            guest['email'] = result.email
            guest['sign'] = result.sign
            return JsonResponse({'status': 200, 'message': 'success', 'data': guest})


# 发布会签到接口
@csrf_exempt
def user_sign(request):
    eid = request.POST.get('eid', '')                   # 发布会id
    phone = request.POST.get('phone', '')               # 嘉宾手机号
    # 判断两个参数均不能为空
    if eid == '' or phone == '':
        return JsonResponse({'status': 100021, 'message': 'parameter error'})
    # 判断发布会是否存在,不存在返回发布会id不存在
    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status': 100022, 'message': 'event id null'})
    # 判断发布会状态是否为True，不为True，说明发布会为关闭状态
    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status': 100023, 'message': 'event status is not available'})
    # 判断发布会是否已开始
    event_time = Event.objects.get(id=eid).start_time           # 发布会时间
    etime = str(event_time).split(".")[0]
    timearray = time.strptime(etime, "%Y-%M-%D %H:%M:%S")
    e_time = int(time.mktime(timearray))

    now_time = str(time.time())                                 # 当前时间
    ntime = now_time.split(".")[0]
    n_time = int(ntime)

    if n_time >= e_time:
        return JsonResponse({'status': 100024, 'message': 'event has started'})
    # 判断嘉宾手机号是否存在
    result = Guest.objects.filter(phone=phone)
    if not result:
        return JsonResponse({'status': 100025, 'message': 'user phone null'})
    # 判断嘉宾手机号与发布会id是否对应
    result = Guest.objects.filter(event_id=eid, phone=phone)
    if not result:
        return JsonResponse({'status': 100026, 'message': 'user did not paticipate in the conference'})
    # 判断嘉宾是否已签到
    result = Guest.objects.get(event_id=eid, phone=phone).sign
    if result:
        return JsonResponse({'status': 100027, 'message': 'guest has sign in'})
    else:
        Guest.objects.filter(event_id=eid, phone=phone).update(sign='1')
        return JsonResponse({'status': 100028, 'message': 'sign success'})

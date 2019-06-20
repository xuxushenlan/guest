from django.http import JsonResponse
from sign.models import Event, Guest
from django.core.exceptions import ValidationError, ObjectDoesNotExist


# 添加发布会接口
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
    except ValidationError as e:
        error = 'start_time format error. It must be in YYYY-MM-DD HH:MM:SS format.'
        return JsonResponse({'status': 100024, 'message': error})
    return JsonResponse({'status': 200, 'message': 'add event success'})

# 查询发布会接口
def get_event_list(request):
    eid = request.GET.get('eid', '')                            # 发布会id
    name = request.GET.get('eid', '')                           # 发布会名称

    # 若id和name都为空，返回状态码和提示
    if eid == '' and name == '':
        return JsonResponse({'status': 100021, 'message': 'parameter error'})
    # 若id不为空，根据id查询结果，结果为空，返回结果为空，不为空，返回结果
    if eid != '':
        event = {}
        try:
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist as e:
            return JsonResponse({'status': 100022, 'message': 'query result is empty'})
        else:
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time
            return JsonResponse({'status': 200, 'message': 'success', 'data':event})
    if name != '':
        datas = []
        results = Event.objects.filter(name__contains=name)
        if results:
            for r in results:
                event = {}
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                datas.append(event)
            return JsonResponse({'status': 200, 'message': 'success', 'data':datas})
        else:
            return JsonResponse({'status': 100022, 'message': 'query result is empty'})
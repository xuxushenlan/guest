from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sign.models import Event, Guest
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError
import time,hashlib,base64
from django.contrib import auth as django_auth


# 用户认证
def user_auth(request):
    # request.META是一个Python字典，包含了本次HTTP请求的Header信息，例如用户认证、IP地址和user - Agent等。
    # HTTP_AUTHORIZATION用于获取HTTP认证数据，如Basic YWRtaW46YWRtaW4xMjMNTY=
    get_http_auth = request.META.get('HTTP_AUTHORIZATION', b'')
    # 通过split()方法将其拆分成list，拆分后：['Basic','YWRtaW46YWRtaW4xMjMNTY']
    auth = get_http_auth.split()
    try:
        # 取出list中的加密串，通过base64对加密字符进行解码。通过decode()方法以UTF-8编码对字符串进行解码。
        # partition()方法以冒号":"为分隔符对字符串进行分隔，得到数据('admin',':','admin123456')
        auth_parts = base64.b64decode(auth[1]).decode('utf-8').partition(':')
    except IndexError: # 获取不到Auth数据，抛出异常
        return "null"
    # 取出auth_parts元组中对应的username和password
    username, password = auth_parts[0], auth_parts[1]
    # 调用Django的认证模块，认证成功则返回"success",失败返回"fail"
    user = django_auth.authenticate(username=username, password=password)
    if user is not None:
        django_auth.login(request, user)
        return "success"
    else:
        return "fail"

# 查询发布会接口--增加用户认证
def sec_get_event_list(request):
    auth_result = user_auth(request)    # 调用认证函数
    if auth_result == 'null':
        return JsonResponse({'status': 10011, 'message': 'user auth null'})
    if auth_result == 'fail':
        return JsonResponse({'status': 10012, 'message': 'user auth fail'})

    eid = request.GET.get('eid', '')                            # 发布会id
    name = request.GET.get('name', '')                           # 发布会名称

    # 若id和name都为空，返回状态码和提示
    if eid == '' and name == '':
        return JsonResponse({'status': 10021, 'message': 'parameter error'})
    # 若id不为空，根据id查询结果，结果为空，返回结果为空，不为空，返回结果
    if eid != '':
        event = {}
        try:
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 10022, 'message': 'query result is empty'})
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
            return JsonResponse({'status': 10022, 'message': 'query result is empty'})

# 用户签名+时间戳
def sign_time(request):
    # 判断客户端请求是否为POST，是则获取客户端时间戳和签名，否则返回'error'
    if request.method == 'POST':
        client_time = request.POST.get('time', '')  # 客户端时间戳
        client_sign = request.POST.get('sign', '')  # 客户端签名
    else:
        return 'error'
    # 判断客户端时间戳和签名不能为空，为空则返回'sign null'
    if client_sign == '' or client_time == '':
        return 'sign null'

    # 服务器时间
    now_time = time.time()
    server_time = str(now_time).split('.')[0]
    # 获取时间差
    time_difference = int(server_time) - int(client_time)

    # 若服务器时间戳-客户端时间戳大于等于60秒，则返回'timeout'
    if time_difference >= 60:
        return 'timeout'

    # 签名检查，将api_key和客户端发送的时间戳喝到一起，通过MD5生成新的加密字符串作为服务器端的sign参数，即server_sign
    md5 = hashlib.md5()
    sign_str = client_time + '&Guest-Bugmaster'     # api_key密钥字符串为'&Guest-Bugmaster'
    sign_bytes_utf8 = sign_str.encode(encoding='utf-8')
    md5.update(sign_bytes_utf8)
    server_sign = md5.hexdigest()

    # 若服务器签名与客户端签名一致，则返回'sign success',否则返回'sign fail'
    if server_sign != client_sign:
        return 'sign fail'
    else:
        return 'sign success'

# 添加发布会接口--增加签名+时间戳
@csrf_exempt    # django 的POST接口需要CSRF验证，添加此装饰器豁免验证
def sec_add_event(request):
    sign_result = sign_time(request)
    if sign_result == 'error':
        return JsonResponse({'status': 10011, 'message': 'request error'})
    if sign_result == 'sign null':
        return JsonResponse({'status': 10012, 'message': 'client sign null'})
    if sign_result == 'timeout':
        return JsonResponse({'status': 10013, 'message': 'client sign timeout'})
    if sign_result == 'sign fail':
        return JsonResponse({'status': 10014, 'message': 'client sign error'})

    eid = request.POST.get('eid', '')                           # 发布会id
    name = request.POST.get('name', '')                         # 发布会名称
    limit = request.POST.get('limit', '')                       # 限制人数
    status = request.POST.get('status', '')                     # 状态
    address = request.POST.get('address', '')                   # 地址
    start_time = request.POST.get('start_time', '')             # 开始时间

    # 若参数为空，则返回状态码100021，错误信息parameter error
    if eid == '' or name == '' or limit == '' or address == '' or start_time == '':
        return JsonResponse({'status': 10021, 'message': 'parameter error'})
    # 判断发布会id和名称是否存在，若存在返回状态码和提示
    result = Event.objects.filter(id=eid)
    if result:
        return JsonResponse({'status': 10022, 'message': 'Event id already exists'})
    result = Event.objects.filter(name=name)
    if result:
        return JsonResponse({'status': 10023, 'message': 'Event name already exists'})
    # 若发布会status为空，置默认值1
    if status == '':
        status = 1
    # 插入数据，若日期格式错误，返回状态码和提示
    try:
        Event.objects.create(id=eid, name=name, limit=limit, status=int(status), address=address,
                             start_time=start_time)
    except ValidationError:
        error = 'start_time format error. It must be in YYYY-MM-DD HH:MM:SS format.'
        return JsonResponse({'status': 10024, 'message': error})
    return JsonResponse({'status': 200, 'message': 'add event success'})

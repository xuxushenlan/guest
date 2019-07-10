from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sign.models import Event, Guest
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError
import time
from django.contrib import auth as django_auth
import base64


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


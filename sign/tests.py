from django.test import TestCase
from django.contrib.auth.models import User
from sign.models import Event,Guest


# Create your tests here.
class ModelTest(TestCase):
    '''测试model类'''
    def setUp(self):
        Event.objects.create(id=1, name='Cherry 3 Plus event', status=True, limit=2000, address='shenzhen',
                             start_time='2019-08-12 09:00:00')
        Guest.objects.create(id=1, event_id=1, realname='alan', phone='13521217758', sign=False, email='alan@email.com')

    def test_event_models(self):
        result = Event.objects.get(name='Cherry 3 Plus event')
        self.assertEqual(result.address, 'shenzhen')
        self.assertTrue(result.status)

    def test_guest_models(self):
        result = Guest.objects.get(realname='alan')
        self.assertEqual(result.phone, '13521217758')
        self.assertFalse(result.sign)


class IndexPageTest(TestCase):
    '''测试index登录页面'''
    def test_index_page_render_index_template(self):
        '''测试index视图'''
        response = self.client.get('/index/')               # client.get()方法请求'/index/'路径
        self.assertEqual(response.status_code, 200)         # status_code获取HTTP返回的状态码
        self.assertTemplateUsed(response, 'index.html')     # 断言服务器是否用给定的index.html模板响应


class LoginActionTest(TestCase):
    '''测试登录动作'''

    def setUp(self):
        User.objects.create_user('admin', 'admin@email.com', 'admin123456')

    def test_add_user(self):
        '''测试增加用户'''
        user = User.objects.get(username='admin')
        self.assertEqual(user.username, 'admin')
        self.assertEqual(user.email, 'admin@email.com')

    def test_login_action_username_password_null(self):
        '''用户名密码为空'''
        test_data = {'username':'', 'password':''}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username or password error!', response.content)

    def test_login_action_username_password_error(self):
        '''用户名密码错误'''
        test_data = {'username':'aaa', 'password':'123'}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username or password error!', response.content)

    def test_login_action_success(self):
        '''登录成功'''
        test_data = {'username':'admin', 'password':'admin123456'}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 302)
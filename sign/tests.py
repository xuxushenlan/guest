from django.test import TestCase
from django.contrib.auth.models import User
from sign.models import Event, Guest


# Create your tests here.
class ModelTest(TestCase):
    """测试model类"""
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
    """测试index登录页面"""
    def test_index_page_render_index_template(self):
        """测试index视图"""
        response = self.client.get('/index/')               # client.get()方法请求'/index/'路径
        self.assertEqual(response.status_code, 200)         # status_code获取HTTP返回的状态码
        self.assertTemplateUsed(response, 'index.html')     # 断言服务器是否用给定的index.html模板响应


class LoginActionTest(TestCase):
    """测试登录动作"""

    def setUp(self):
        User.objects.create_user('admin', 'admin@email.com', 'admin123456')

    def test_add_user(self):
        """测试增加用户"""
        user = User.objects.get(username='admin')
        self.assertEqual(user.username, 'admin')
        self.assertEqual(user.email, 'admin@email.com')

    def test_login_action_username_password_null(self):
        """用户名密码为空"""
        test_data = {'username': '', 'password': ''}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username or password error!', response.content)

    def test_login_action_username_password_error(self):
        """用户名密码错误"""
        test_data = {'username': 'aaa', 'password': '123'}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username or password error!', response.content)

    def test_login_action_success(self):
        """登录成功"""
        test_data = {'username': 'admin', 'password': 'admin123456'}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 302)


class EventManageTest(TestCase):
    """发布会管理测试"""

    def setUp(self):
        User.objects.create_user('admin', 'admin@email.com', 'admin123456')
        Event.objects.create(name='xiaomi5', limit=2000, address='beijing', status=True,
                             start_time='2019-09-01 09:00:00')
        Event.objects.create(name='pingguo5', limit=1000, address='shanghai', status=True,
                             start_time='2019-10-01 09:00:00')
        self.login_user = {'username': 'admin', 'password': 'admin123456'}

    def test_event_manage_success(self):
        """测试发布会管理视图"""
        self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/event_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'xiaomi5', response.content)
        self.assertIn(b'beijing', response.content)

    def test_event_manage_search_success(self):
        """测试发布会名称搜索"""
        self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/event_manage/', {'name': 'pingguo5'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'pingguo5', response.content)
        self.assertIn(b'shanghai', response.content)


class GuestManageTest(TestCase):
    """"嘉宾管理测试"""

    def setUp(self):
        User.objects.create_user('admin', 'admin@email.com', 'admin123456')
        Event.objects.create(name='xiaomi5', limit=2000, address='beijing', status=True,
                             start_time='2019-09-01 09:00:00')
        Guest.objects.create(realname='zhangsan', phone='13512345678', email='zhangsan@email.com', sign=False,
                             event_id=1)
        self.login_user = {'username': 'admin', 'password': 'admin123456'}

    def test_guest_manage_success(self):
        """测试嘉宾信息：zhangsan"""
        self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/guest_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'zhangsan', response.content)
        self.assertIn(b'13512345678', response.content)

    def test_guest_manage_search_success(self):
        """测试嘉宾搜索"""
        self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/search_realname/', {'realname': 'zhangsan'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'zhangsan', response.content)
        self.assertIn(b'13512345678', response.content)


class SignIndexActionTest(TestCase):
    """嘉宾签到测试"""

    def setUp(self):
        User.objects.create_user('admin', 'admin@email.com', 'admin123456')
        Event.objects.create(id=1, name='xiaomi5', limit=2000, address='beijing', status=True,
                             start_time='2019-09-01 09:00:00')
        Event.objects.create(id=2, name='pingguo5', limit=2000, address='beijing', status=True,
                             start_time='2019-09-01 09:00:00')
        Guest.objects.create(realname='zhangsan', phone='13512345678', email='zhangsan@email.com', sign=False,
                             event_id=1)
        Guest.objects.create(realname='lisi', phone='13412345678', email='lisi@email.com', sign=True,
                             event_id=2)
        self.login_user = {'username': 'admin', 'password': 'admin123456'}

    def test_sign_index_action_phone_null(self):
        """手机号为空"""
        self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/1/', {'phone': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'phone error', response.content)

    def test_sign_index_action_phone_event_not_match(self):
        """手机号与发布会不匹配"""
        self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/2/', {'phone': '13512345678'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'phone and event not match', response.content)

    def test_sign_index_action_guest_has_sign(self):
        """嘉宾已签到"""
        self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/2/', {'phone': '13412345678'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'user has sign in', response.content)

    def test_sign_index_action_success(self):
        """签到成功"""
        self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/1/', {'phone': '13512345678'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'sign in success', response.content)
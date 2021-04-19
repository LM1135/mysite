from django.apps import AppConfig


class LoginConfig(AppConfig):
    name = 'login'
    # login app 在后台的展示 若未使用verbose_name，则展示LOGIN
    verbose_name = '注册用户'

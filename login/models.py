from django.db import models


# Create your models here.
class User(models.Model):
    gender = ((0, '男'), (1, '女'))
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    sex = models.SmallIntegerField(choices=gender, default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    has_confirmed = models.BooleanField(default=False)

    class Meta:
        # User模型类，在admin中的展示名称
        verbose_name = verbose_name_plural = '用户'
        # 排序
        ordering = ['-create_time']


# 邮件确认的模型
class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ":" + self.code

    class Meta:
        ordering = ["-create_time"]
        verbose_name = verbose_name_plural = "确认码"

from django.urls import path,include

from login import views

urlpatterns = [
    path('index/', views.index_handler, name='user_inder'),
    path('login/', views.login_handler, name='user_login'),
    path('register/', views.register_handler, name='user_register'),
    path('logout/', views.logout_hanger, name='user_logout'),
    path('confirm/', views.confirm_hander, name='user_confirm'),
]

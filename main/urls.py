from django.urls import path
from .views import callback, logout, reset, main_page, server_choose, sync, success

urlpatterns = [
    path('', main_page, name="main_page"),
    path('server_choose', server_choose, name="server_choose"),
    path('fhir-app/', callback, name="callback"),
    path('sync/', sync, name="sync"),
    path('logout', logout, name="logout"),
    path('reset', reset, name="reset"),
    path('success', success, name="success")

]
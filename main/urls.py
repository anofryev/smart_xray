from django.urls import path
from .views import index, callback, logout, reset, main_page, server_choose, synchronizing

urlpatterns = [
    path('', main_page, name="main_page"),
    path('server_choose', server_choose, name="server_choose"),
    path('fhir-app', callback, name="callback"),
    path('synchronizing', synchronizing, name="synchronizing"),
    path('logout', logout, name="logout"),
    path('reset', reset, name="reset")
]
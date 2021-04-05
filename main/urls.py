from django.urls import path
from .views import callback, logout, reset, main_page, server_choose, sync, success, test_nn_predict, StudiesView

urlpatterns = [
    path('', main_page, name="main_page"),
    path('server_choose', server_choose, name="server_choose"),
    path('fhir-app/', callback, name="callback"),
    path('sync/', sync, name="sync"),
    path('studies_list', StudiesView.as_view(), name = "studies_list"), # Выводит список исследований
    path('logout', logout, name="logout"),
    path('reset', reset, name="reset"),
    path('success', success, name="success"),
    path('test_nn_predict', test_nn_predict, name="test_nn_predict")

]
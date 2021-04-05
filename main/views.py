from django.shortcuts import render, redirect
from .session_class import Session
from .fhir_sync import synchronizing
from django.views.generic import ListView
from .models import Series, ImagingStudy
from .neural_network import nn_predict

# Create your views here.
smart_session = None

class StudiesView(ListView):

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ImagingStudy.objects.filter(user=self.request.user)
    model = ImagingStudy
    template_name = 'studies_list.html'
    context_object_name = 'imaging_studies'



# Онсовная страница
def main_page(request):
    context = {'test_info' : request.user}
    return render(request, 'main_page.html', context)

def server_choose(request):
    if request.user.is_authenticated:
        global smart_session
        try:
            smart_session = Session(request)
            auth_url = smart_session.smart.authorize_url
            context = {'auth_url': auth_url}
            return render(request, 'server_choose.html', context)
        except Exception as e:
            return render(request, 'callback_error.html', context)
    else:
        print('ошибка , не авторизован')
        context ={'error': 'Ошибка. Требуется авторизация'}
        return render(request, 'callback_error.html', context)

# Возвращение от сервера авторизации
def callback(request):
    """ OAuth2 callback interception."""
    try:
        smart_session.smart.handle_callback(request.build_absolute_uri())
    except Exception as e:

        context = {'error': e}
        print("an error ocured:", e)
        return render(request, 'callback_error.html', context)
    return redirect('/sync')

def sync(request):
    print('во view sync')
    if smart_session:
        if request.user.is_authenticated:
            synchronizing(smart=smart_session.smart, request=request)
        else:
            context = {'error': 'ошибка! пользователь не авторизован!'}
            return render(request, 'callback_error.html', context)
    else:
        context = {'error': 'error while synchronizing, no smart session'}
        return render(request, 'callback_error.html', context)
    nn_predict()
    return redirect('/success')

def logout(request):
    smart_session.logout()
    return redirect('/')


def reset(request):
    if 'state' in request.session:
        del request.session['state']
        print('State deleted from session')
    return redirect('/')


def success(request):
    return render(request, 'success.html')

def test_nn_predict(request):
    nn_predict()
    return render(request, "success.html")

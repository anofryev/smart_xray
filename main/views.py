from django.shortcuts import render, redirect
from .session_class import Session
# Create your views here.


# Онсовная страница
def main_page(request):
    context = None
    return render(request, 'main_page.html', context)

def server_choose(request):
    smart_session = Session(request)
    auth_url = smart_session.smart.authorize_url
    context = {'auth_url': auth_url}
    return render(request, 'server_choose.html', context)

def index(request):

    """ The app's main page."""
    smart_session = Session(request)
    smart = smart_session.smart
    pres = None
    name = None
    prescriptions = None
    is_smart_ready = smart.ready
    auth_url = smart.authorize_url
    if is_smart_ready and smart.patient is not None: # "ready" may be true but the access token may have expired, making smart.patient = None
        name = smart.human_name(
            smart.patient.name[0] if smart.patient.name and len(smart.patient.name) > 0 else 'Unknown')

        pres = smart_session.get_prescriptions()
        if pres is not None:
            prescriptions = [smart_session.get_med_name(p) for p in pres]
    else:
        auth_url = smart.authorize_url
    context = {'prescriptions': prescriptions,
               'is_smart_ready': is_smart_ready,
               'name': name,
               'auth_url': auth_url,
               'auth_state': request.session.get('state')
               }
    return render(request, 'index.html', context)


# Возвращение от сервера авторизации
def callback(request):
    """ OAuth2 callback interception."""
    smart_session = Session(request)
    try:
        smart_session.smart.handle_callback(request.build_absolute_uri())
    except Exception as e:
        context = {'error': e}
        print("an error ocured:", e)
        return render(request, 'callback_error.html', context)
    return redirect('/')


def logout(request):
    smart_session = Session(request)
    smart_session.logout()
    return redirect('/')


def reset(request):
    if 'state' in request.session:
        del request.session['state']
        print('State deleted from session')
    return redirect('/')

def index(request):

    """ The app's main page."""
    global smart_session
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
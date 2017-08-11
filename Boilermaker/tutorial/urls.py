from django.conf.urls import url 
from tutorial import views 

urlpatterns = [ 
  # The home view ('/tutorial/') 
  url(r'^$', views.home, name='home'), 
  # Explicit home ('/tutorial/home/') 
  url(r'^home/$', views.home, name='home'), 
  # Redirect to get token ('/tutorial/gettoken/')
  url(r'^gettoken/$', views.gettoken, name='gettoken'),
  # Mail view ('/tutorial/mail/')
  url(r'^mail/$', views.mail, name='mail'),
  # Events view ('/tutorial/events/')
  url(r'^my_events/$', views.my_events, name='my_events'),
  url(r'^bunker_events/$', views.bunker_events, name='bunker_events'),
  url(r'^boilermaker_events/$', views.boilermaker_events, name='boilermaker_events'),
  url(r'^strategy_events/$', views.strategy_events, name='strategy_events'),
  url(r'^all_events/$', views.all_events, name='all_events'),
]

# howdy/urls.py
from django.conf.urls import url
from django.contrib import admin
from polly import views as core_views
from django.contrib.auth.views import login
from django.contrib.auth import views as auth_views
from django.conf.urls import include


urlpatterns = [
    url(r'^$', core_views.HomePageView.as_view()),
    #url(r'^index/$', core_views.index, name='index'),
    #url(r'^login/$', core_views.index),
    url(r'^about/$', core_views.AboutPageView.as_view()),
    url(r'contact/$', core_views.contact, name='contact_me'),
    #url(r'^admin/', admin.site.urls),
    url(r'^logout/$', auth_views.logout, {'next_page': '/AnonymousUser/library/all/all/'}, name='logout'),
    #url(r'^login/', auth_views.LoginView.as_view(redirect_authenticated_user=False), name='login'),
    url(r'^ajax/login/$', core_views.my_login, name='login_button'),
    url(r'^ajax/signup/$', core_views.signup, name='signup'),
    url(r'^password_reset/$', core_views.my_password_reset, name='password_reset'),
    url(r'^password_reset_done/$', core_views.my_password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        core_views.my_password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', core_views.my_password_reset_complete, name='password_reset_complete'),
    url(r'^(?P<user_name>[\w.@+-]+)/library/(?P<language_native>[\w-]+)/(?P<language_foreign>[\w-]+)/$', core_views.text_library, name='text_library'),
    url(r'^(?P<user_name>[\w.@+-]+)/collection/(?P<book_name>.*)/(?P<language_native>[\w-]+)/(?P<language_foreign>[\w-]+)/$', core_views.col_library, name='col_library'),
    url(r'^(?P<user_name>[\w.@+-]+)/test/(?P<language_native>[\w-]+)/(?P<language_foreign>[\w-]+)/(?P<book_name>.*)/$', core_views.language_form, name='language_form'),
    url(r'^(?P<user_name>[\w-]+)/(?P<language_native>[\w-]+)/(?P<language_foreign>[\w-]+)/(?P<book_name>.*)/(?P<section>\d+)/reader/$', core_views.reader, name='reader'),
    url(r'^ajax/typing/$', core_views.renderWord, name='renderWord'),
    url(r'^ajax/addbook/$', core_views.addBook, name='addbook'),
    url(r'^ajax/highlight/$', core_views.highlight, name='highlight'),
    url(r'^ajax/removebook/$', core_views.removeBook, name='removebook'),
]

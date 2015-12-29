from django.conf.urls import url
from django.views.generic import TemplateView
from courses import views
from courses import apis

urlpatterns = [
    url(r'^$', views.Main.as_view(), name='main'),
    url(r'^course/list/$', apis.CourseListApi.as_view(), name='course_list'),
    url(r'^course/(?P<id>[a-zA-Z0-9-_]+)/$', TemplateView.as_view(template_name="courses/coursedetail.html"), name='course_detail'),
    url(r'^course/(?P<id>[a-zA-Z0-9-_]+)/api/$', apis.CourseDetailApi.as_view(), name='api_course_detail'),

]

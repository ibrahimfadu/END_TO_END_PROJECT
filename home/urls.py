from django.urls import path
from . import views 

urlpatterns=[
    path("",views.home,name="home"),
    path("graph/",views.graph,name="graph"),
    path('graph_result/', views.graph_result, name='graph_result'),

]
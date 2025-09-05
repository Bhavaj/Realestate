from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('agent-login/', views.agent_login, name='agent_login'),
    path('agent-dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('agent-logout/', LogoutView.as_view(next_page='agent_login'), name='agent_logout'),

    # Admin routes
    path('admin-login/', views.admin_login, name='admin-login'),
    path('admin-logout/', views.admin_logout, name='admin-logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('add-customer/', views.add_customer, name='add_customer'),
    path('add-agent/', views.add_agent, name='add_agent'),
    path('add-payment/', views.add_payment, name='add_payment'),
    path('add-project/', views.add_project, name='add_project'),
    path('delete-agent/<int:agent_id>/', views.delete_agent, name='delete_agent'),
    path('delete-customer/<int:customer_id>/', views.delete_customer, name='delete_customer'),
    path('delete-project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('update-gift-status/<int:gift_id>/', views.update_gift_status, name='update_gift_status'),

    # Customer routes
    path('customer-login/', views.customer_login, name='customer_login'),
    path('customer-dashboard/<int:customer_id>/', views.customer_dashboard, name='customer_dashboard'),
]

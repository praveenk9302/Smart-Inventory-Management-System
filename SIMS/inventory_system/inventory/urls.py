from django.urls import path
from . import views
from .views import sales_view

urlpatterns = [
    path("admin/", views.login_view, name="admin_login"),  # Optional app-level route
    path("login/", views.login_view, name="login"),
    path("", views.login_view, name="home"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("products/", views.products, name="products"),
    path("scan-barcode/", views.scan_barcode, name="scan_barcode"),
    path("logout/", views.logout_view, name="logout"),
    path("sales/", sales_view, name="sales"),
    path("alerts/", views.alert_view, name="alerts"),
]
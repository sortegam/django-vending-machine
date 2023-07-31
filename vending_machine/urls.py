"""vending_machine URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from apps.health.views import healthcheck 
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
import apps.vending.views as vending_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthcheck/", healthcheck),
    path("login/", vending_views.UserLoginView.as_view()),
    path("balance/add/", vending_views.BalanceViewSet.as_view({'post': 'add'})),
    path("balance/refund/", vending_views.BalanceViewSet.as_view({'post': 'refund'})),
    path("buy/", vending_views.BuyView.as_view()),
    path("slots/", include([
      #  path("<uuid:id>", vending_views.MyDetailViewToBeDone.as_view()),
        path("", vending_views.VendingMachineSlotView.as_view()),
    ])),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.urls import path
import apps.vending.views as vending_views

urlpatterns = [
    path("login/", vending_views.UserLoginView.as_view()),
    path("balance/add/", vending_views.BalanceViewSet.as_view({'post': 'add'})),
    path("balance/refund/", vending_views.BalanceViewSet.as_view({'post': 'refund'})),
    path("buy/", vending_views.BuyView.as_view()),
    path("slots/", vending_views.VendingMachineSlotView.as_view()),
]

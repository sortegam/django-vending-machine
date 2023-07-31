from django.contrib import admin
from apps.vending.models import Product, VendingMachineSlot, User


class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "created_at", "updated_at"]
    ordering = ["-created_at"]


class VendingMachineSlotAdmin(admin.ModelAdmin):
    pass


class UserAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(VendingMachineSlot, VendingMachineSlotAdmin)
admin.site.register(User, UserAdmin)

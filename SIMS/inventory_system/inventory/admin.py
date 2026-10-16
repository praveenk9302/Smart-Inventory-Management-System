from django.contrib import admin
from .models import Product, Category, Sale, SalesHistory


# Site branding
admin.site.site_header = "📦 Inventory Control"
admin.site.site_title = "Inventory Admin"
admin.site.index_title = "Welcome to your inventory dashboard"


class StockStatusFilter(admin.SimpleListFilter):
    title = "stock status"
    parameter_name = "stock_status"

    def lookups(self, request, model_admin):
        return [
            ("in", "In stock"),
            ("low", "Low stock (5 or less)"),
            ("out", "Out of stock"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "in":
            return queryset.filter(stock__gt=5)
        if self.value() == "low":
            return queryset.filter(stock__gt=0, stock__lte=5)
        if self.value() == "out":
            return queryset.filter(stock=0)
        return queryset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "product_id", "barcode", "price", "stock", "stock_status")
    list_editable = ("price", "stock")
    list_filter = (StockStatusFilter,)
    search_fields = ("name", "product_id", "barcode")
    ordering = ("name",)
    list_per_page = 25

    @admin.display(description="Status", ordering="stock")
    def stock_status(self, obj):
        if obj.stock == 0:
            return "🔴 Out of stock"
        if obj.stock <= 5:
            return "🟡 Low stock"
        return "🟢 In stock"


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity", "total_price", "date_sold")
    list_filter = ("date_sold",)
    search_fields = ("product__name",)
    date_hierarchy = "date_sold"
    ordering = ("-date_sold",)
    list_per_page = 25


@admin.register(SalesHistory)
class SalesHistoryAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity_sold", "date")
    list_filter = ("date",)
    search_fields = ("product__name",)
    date_hierarchy = "date"
    ordering = ("-date",)
    list_per_page = 25


    # ================= ADMIN HOME PAGE: show products first =================
_original_admin_index = admin.site.index

def admin_index_with_products(request, extra_context=None):
    extra_context = extra_context or {}
    extra_context["products"] = Product.objects.order_by("name")[:10]
    return _original_admin_index(request, extra_context)

admin.site.index = admin_index_with_products
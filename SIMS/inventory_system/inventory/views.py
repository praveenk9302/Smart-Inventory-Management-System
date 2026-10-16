import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .ai_prediction import predict_demand
from .models import Product, SalesHistory

LOW_STOCK_LIMIT = 5


# ---------------- DASHBOARD ----------------

def dashboard(request):
    # Annotate every product with its total sold quantity from SalesHistory
    products_with_sales = Product.objects.annotate(
        sold_count=Coalesce(Sum('saleshistory__quantity_sold'), 0)
    )

    total_products = Product.objects.count()
    top_selling_products = products_with_sales.order_by('-sold_count', 'name')
    top_seller = top_selling_products.first()
    low_stock_count = Product.objects.filter(stock__lte=LOW_STOCK_LIMIT).count()

    # Sales analytics data for chart
    chart_data = [
        {"name": p.name, "sold": p.sold_count}
        for p in top_selling_products
    ]

    context = {
        "total_products": total_products,
        "top_seller": top_seller,
        "low_stock_count": low_stock_count,
        "top_selling_products": top_selling_products,
        "chart_data": json.dumps(chart_data),
    }

    return render(request, "inventory/dashboard.html", context)


# ---------------- PRODUCTS ----------------

@login_required
def products(request):
    return render(request, "inventory/products.html", {
        "products": Product.objects.all()
    })


# ---------------- BARCODE SCAN ----------------

@csrf_exempt
def scan_barcode(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})

    try:
        data = json.loads(request.body)
        barcode = data.get("barcode")

        product = Product.objects.get(barcode=barcode)

        if product.stock <= 0:
            return JsonResponse({
                "success": False,
                "message": "Out of stock"
            })

        product.stock -= 1
        product.save()

        # Record the sale so the dashboard counts it
        SalesHistory.objects.create(
            product=product,
            quantity_sold=1
        )

        sold_total = (
            SalesHistory.objects
            .filter(product=product)
            .aggregate(total=Sum('quantity_sold'))['total'] or 0
        )

        return JsonResponse({
            "success": True,
            "name": product.name,
            "stock": product.stock,
            "sold": sold_total
        })

    except Product.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Product not found"
        })


# ---------------- LOGOUT ----------------

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# ---------------- LOGIN ----------------

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")

        return render(request, "inventory/login.html", {
            "error": "Invalid username or password"
        })

    return render(request, "inventory/login.html")


# ---------------- SALES ----------------

def sales_view(request):
    products = Product.objects.all()

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 0))

        product = get_object_or_404(Product, id=product_id)

        if quantity <= 0:
            messages.error(request, "Quantity must be at least 1.")
        elif quantity <= product.stock:
            product.stock -= quantity
            product.save()

            SalesHistory.objects.create(
                product=product,
                quantity_sold=quantity
            )

            messages.success(request, "Sale recorded successfully!")
        else:
            messages.error(request, "Not enough stock!")

        return redirect("sales")

    # AI prediction data
    predictions = []
    for product in products:
        predictions.append({
            "product": product.name,
            "stock": product.stock,
            "prediction": predict_demand(product)
        })

    return render(request, "inventory/sales.html", {
        "products": products,
        "predictions": predictions
    })


def sell_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        sell_qty = int(request.POST.get("sell_qty", 0))

        if sell_qty > 0 and product.stock >= sell_qty:
            product.stock -= sell_qty
            product.save()

            SalesHistory.objects.create(
                product=product,
                quantity_sold=sell_qty
            )

    return redirect("sales")


# ---------------- ALERTS / OTHER VIEWS (unchanged logic) ----------------

def dashboard_view(request):
    products = Product.objects.all()
    alert_count = 0

    for p in products:
        predicted = predict_demand(p.id)
        p.predicted_demand = predicted

        if isinstance(predicted, int) and p.stock < predicted:
            alert_count += 1

    return render(request, "inventory/dashboard.html", {
        "products": products,
        "alert_count": alert_count,
    })


def alert_view(request):
    products = Product.objects.all()
    alert_products = []

    for p in products:
        predicted = predict_demand(p.id)

        # AI-based alert
        if isinstance(predicted, int):
            if p.stock < predicted:
                p.predicted_demand = predicted
                alert_products.append(p)

                def predictions_view(request):
    products = Product.objects.all()

    predictions = []
    for product in products:
        predictions.append({
            "product": product.name,
            "stock": product.stock,
            "prediction": predict_demand(product),
        })

    return render(request, "inventory/predictions.html", {
        "predictions": predictions,
    })

        # Fallback alert (no AI data yet)
        else:
            if p.stock <= LOW_STOCK_LIMIT:
                p.predicted_demand = "Insufficient data"
                alert_products.append(p)

    return render(request, "inventory/alerts.html", {
        "alert_products": alert_products
    })
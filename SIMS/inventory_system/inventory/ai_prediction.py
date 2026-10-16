from .models import SalesHistory
from django.db.models import Sum

def predict_demand(product):
    sales = SalesHistory.objects.filter(product=product)

    if sales.count() < 2:
        return "Low demand"

    total_sold = sales.aggregate(total=Sum("quantity_sold"))["total"]
    avg_demand = total_sold // sales.count()

    if avg_demand >= 5:
        return "High Demand"
    elif avg_demand >= 3:
        return "Medium Demand"
    else:
        return "Low Demand"

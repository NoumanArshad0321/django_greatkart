from django.http import HttpResponse
from django.shortcuts import render

from carts.models import CartItem
from orders.models import Order
from .forms import OrderForm

# Create your views here.
def place_order(request):
    current_user = request.user
    

    # If cart count is less than 1 or equal to 0 ,then redirect to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return render(request, 'store/shop.html')
    

    if request.method == "POST":
        # Process the order
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside the Order Table
           data = Order()
           data.first_name = form.cleaned_data('first_name')
           data.last_name = form.cleaned_data('last_name')
           data.phone = form.cleaned_data('phone')
           data.email = form.cleaned_data('email')
           data.address_line_1 = form.cleaned_data('address_line_1')
           data.address_line_2 = form.cleaned_data('address_line_2')
           data.country = form.cleaned_data('country')
           data.state = form.cleaned_data('state')
           data.city = form.cleaned_data('city')
           data.order_note = form.cleaned_data('order_note')
           data.save()
        return HttpResponse("Order Placed Successfully")
    else:
        return render(request, 'orders/place_order.html')
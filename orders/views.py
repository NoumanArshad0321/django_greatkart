import datetime
from django.http import HttpResponse
from django.shortcuts import redirect, render
import stripe
from django.utils import timezone

from carts.models import CartItem
from greatkart import settings
from orders.models import Order
from .forms import OrderForm

# Create your views here.
def payments(request):
    return render(request, 'orders/payments.html')


def place_order(request,total=0, quantity=0):
    current_user = request.user
    

    # If cart count is less than 1 or equal to 0 ,then redirect to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store') 
    
    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax
    

    if request.method == "POST":
        # Process the order
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside the Order Table
            data = Order()
            data.user           = current_user
            data.first_name     = form.cleaned_data['first_name']
            data.last_name      = form.cleaned_data['last_name']
            data.phone          = form.cleaned_data['phone']
            data.email          = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country        = form.cleaned_data['country']
            data.state          = form.cleaned_data['state']
            data.city           = form.cleaned_data['city']
            data.order_note     = form.cleaned_data['order_note']
            data.order_total    = grand_total
            data.tax            = tax
            data.ip             = request.META.get('REMOTE_ADDR')
            data.save()

        #     Generate Order id or number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d  = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'grand_total': grand_total,
                'tax': tax,
            }
            return render(request,'orders/payments.html', context)

    else:
        return redirect('checkout')

    #     return HttpResponse("Order Placed Successfully")
    # else:
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderProduct, Payment



stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_checkout_session(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, is_ordered=False)
    YOUR_DOMAIN = "http://127.0.0.1:8000"

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': f'Order {order.order_number}'},
                'unit_amount': int(order.order_total * 100),  # cents
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=YOUR_DOMAIN + f'/orders/payment_success/?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}',
        cancel_url=YOUR_DOMAIN + '/orders/payment_cancel/',
    )

    return redirect(checkout_session.url, code=303)

from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Order, Payment, OrderProduct
from carts.models import CartItem

@login_required
def payment_success(request):
    session_id = request.GET.get("session_id")
    order_id = request.GET.get("order_id")
    
    # Get the order (remove is_ordered=False to allow page reload)
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Save payment record
    payment = Payment.objects.create(
        user=request.user,
        payment_id=session_id,
        payment_method="Stripe",
        amount_paid=order.order_total,
        status="Completed",
    )
    
    # Update order
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    # Get all ordered products
    ordered_products = OrderProduct.objects.filter(order=order)
    
    # Mark products as ordered
    for item in ordered_products:
        item.ordered = True
        item.save()
    
    # Clear the cart
    CartItem.objects.filter(user=request.user).delete()
    
    # Calculate totals
    total = sum([item.product_price * item.quantity for item in ordered_products])
    tax = order.tax
    grand_total = order.order_total
    
    # Estimated delivery date (3 days from now)
    estimated_delivery = (timezone.now() + timedelta(days=3)).strftime("%d %b, %Y")
    
    # Context for template
    context = {
        "order": order,
        "ordered_products": ordered_products,
        "total": total,
        "tax": tax,
        "grand_total": grand_total,
        "estimated_delivery": estimated_delivery,
    }
    
    return render(request, "orders/payment_success.html", context)


@login_required
def payment_cancel(request):
    return render(request, "orders/payment_cancel.html")

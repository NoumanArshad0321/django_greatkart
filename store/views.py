
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category
from store.models import Product
from django.core.paginator import EmptyPage,PageNotAnInteger, Paginator
from django.db.models import Q

# Create your views here.
def store(request, category_slug=None):
     categories=None
     products=None

     if category_slug != None:
          categories = get_object_or_404(Category, slug=category_slug)
          products = Product.objects.filter(category=categories, is_available=True)
          paginator= Paginator(products, 3)
          page= request.GET.get('page')
          paged_products = paginator.get_page(page)
          product_count= products.count()
     else:
            products = Product.objects.all().filter(is_available=True).order_by('id')
            paginator= Paginator(products, 3)
            page= request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count= products.count()
     context = {
        'products': paged_products,
        'product_count': product_count
     }
     return render(request, 'store/store.html',context)
def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

        # New: fetch variations for this product
        from store.models import Variation
        color_variations = Variation.objects.filter(product=single_product, variation_category='color', is_active=True)
        size_variations = Variation.objects.filter(product=single_product, variation_category='size', is_active=True)

    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        # New: send variations to template
        'color_variations': color_variations,
        'size_variations': size_variations,
    }

    return render(request, 'store/product_detail.html', context)

def search(request):
     if 'keyword' in request.GET:
          keyword = request.GET['keyword']
          if keyword:
               products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword)| Q(product_name__icontains=keyword))
               product_count= products.count()
          context ={
               'products':products,
               'product_count': product_count,
          }     
     return render(request,'store/store.html',context)
from django.contrib import admin
import admin_thumbnails


from .models import Product, Variation, ReviewRating

# Register your models here.
@admin_thumbnails.thumbnail('image')
class VariationInline(admin.TabularInline):
    model = Variation
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','price' ,'stock','category','created_date','modified_date','is_available')
    prepopulated_fields = {'slug':('product_name',)}
    inlines =[VariationInline]

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product','variation_category' ,'variation_value','is_active', 'image')
    list_editable = ('is_active',)
    list_filter = ('product','variation_category' ,'variation_value')
admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating)
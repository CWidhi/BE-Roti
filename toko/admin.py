from django.contrib import admin
from .models import Jalur, Toko


class TokoInline(admin.TabularInline): 
    model = Toko
    extra = 1 
    fields = ('nama', 'alamat', 'koordinat', 'telepon', 'is_pasar', 'is_delete') 
    show_change_link = True  

@admin.register(Jalur)
class JalurAdmin(admin.ModelAdmin):
    list_display = ('id', 'nama', 'created_at', 'updated_at')
    search_fields = ('nama',)
    list_filter = ('created_at',)
    inlines = [TokoInline] 
    filter_horizontal = ('users',)

@admin.register(Toko)
class TokoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nama', 'alamat', 'telepon', 'is_pasar', 'jalur', 'created_at')
    search_fields = ('nama', 'alamat', 'telepon')
    list_filter = ('is_pasar', 'jalur')
    list_editable = ('is_pasar',) 
 
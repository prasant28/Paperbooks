from django.contrib import admin

# Register your models here.
from .models import book, post, Order, orderbook, Comment, Review, Subscribe, Customer


@admin.register(book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_nm', 'publisher_nm', 'branch',
                    'book_price', 'stock', 'visit')
    list_filter = ('publisher_nm', 'branch', 'featured')
    search_fields = ('book_nm', 'author_nm', 'edition')


@admin.register(post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'post_title', 'post_category',
                    'post_date', 'post_tag', 'visit')
    list_filter = ('post_category', 'post_auth', 'post_date')
    search_fields = ('post_title', 'post_category',
                     'post_date', 'post_tag')


@admin.register(orderbook)
class OrderBookAdmin(admin.ModelAdmin):
    list_display = ('user', 'pk', 'ordered')
    list_filter = ('ordered',)
    search_fields = ('user', 'book')


@admin.register(Order)
class OrderBookAdmin(admin.ModelAdmin):
    list_display = ('user', 'pk', 'ordered', 'ordered_date')
    list_filter = ('ordered', 'ordered_date')
    search_fields = ('user', 'book')


admin.site.register(Review)
admin.site.register(Customer)
admin.site.register(Subscribe)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'content', 'post', 'timestamp', 'active')
    list_filter = ('post', 'timestamp', 'active')
    search_fields = ('name', 'email', 'content')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)

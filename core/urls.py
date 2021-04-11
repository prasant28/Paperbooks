from django.urls import path
from .views import home, contact, blog, bookshelf, myaccount, BookDetailView, checkout, register, orders, address, account_details, PostDetailView, CartView, logoutCust, home_search, add_to_cart, remove_from_cart, remove_single_item_from_cart, buy_now, privacy_policy, LikeView, footer, AMIGOS, change_password

app_name = 'core'

urlpatterns = [
    path('', home, name='home'),
    path('contact-us/', contact, name='contact'),
    path('footer/', footer, name='footer'),
    path('blog/', blog, name='blog'),
    path('post/<slug>/', PostDetailView.as_view(), name='post'),
    path('bookshelf/', bookshelf, name='bookshelf'),
    path('search/', home_search, name='search'),
    path('MyAccount/', myaccount, name='myaccount'),
    path('privacy-policy/', privacy_policy, name='privacy-policy'),
    path('Orders/', orders, name='orders'),
    path('Address/', address, name='address'),
    path('AccountDetails/', change_password, name='change_password'),
    path('AccountDetails/', account_details, name='accountdetails'),
    path('checkout/', checkout, name='checkout'),
    path('cart/', CartView.as_view(), name='cart'),
    path('bookshelf/<slug>/', BookDetailView.as_view(), name='book'),
    path('register/', register, name='register'),
    path('logout/', logoutCust, name='logout'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('buy-now/<slug>/', buy_now, name='buy-now'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('like/<int:pk>', LikeView, name='like_post'),
    path('AMIGOS/', AMIGOS, name='AMIGOS'),

]

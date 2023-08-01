from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("<int:auction_id>", views.auctions, name="auctions"),
    path('auctions/<int:auction_id>/add_comment', views.add_comment, name='add_comment'),
    path('watchlist', views.watchlist, name='watchlist'),
    path('watchlist/add/<int:auction_id>', views.add_watchlist, name='add_watchlist'),
    path('watchlist/remove/<int:auction_id>', views.remove_watchlist, name='remove_watchlist'),
    path('auctions/<int:auction_id>/change_active_status/', views.change_active_status, name='change_active_status'),
    path('categories', views.categories, name='categories'),
    path("categories/<int:category_id>", views.category_detail, name="category_detail"),
    
]

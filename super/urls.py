from django.urls import path,include
from super.views import *
# ajax
from app.views import SellerViewId 

urlpatterns = [
    path('', superView,name='super_view'),
    path('super_keys', superkeys,name='super_keys'),
    path('super_seller', super_Seller,name='super_seller'),
    path('super_transaction', superTrns,name='super_transaction'),
    path('super_proxy', superProxy,name='super_proxy'),
    path('super_history', superHistory,name='super_history'),

    path('super_renew_id/<str:id>', superRenewId , name='super_renew_id'),
    path('delete_super_ip/<int:id>', DeleteSuperIp , name='delete_super_ip'),
    path('delete_super_seller/<int:id>', DeleteSeller , name='delete_super_seller'),
    path('update_super_seller/<int:id>', UpdateSeller , name='update_super_seller'),
    path('update_super_seller_password/<int:id>', UpdateSellerPassword , name='update_super_seller_password'),


    # ajax methods
    path('super_view_id/', superViewId , name='super_view_id'),






]

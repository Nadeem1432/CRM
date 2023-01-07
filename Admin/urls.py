from django.urls import path,include
from Admin.views import *

# ajax
from app.views import SellerViewId , DeleteIp


urlpatterns = [
    # path('', Home,name='home'),
    # path('test', Test,name='test'),
    path('', adminView,name='admin_view'),
    path('admin_keys', adminkeys,name='admin_keys'),
    path('admin_transaction', adminTrns,name='admin_transaction'),
    path('admin_proxy', adminProxy,name='admin_proxy'),
    path('admin_history', adminHistory,name='admin_history'),

    path('admin_renew_id/<str:id>', adminRenewId , name='admin_renew_id'),
    path('delete_ip/<int:id>', DeleteAdminIp , name='delete_ip'),
    
    # seller urls 
    path('admin_seller', admin_Seller,name='admin_seller'),
    path('delete_seller/<int:id>', DeleteSeller , name='delete_seller'),
    path('update_seller/<int:id>', UpdateSeller , name='update_seller'),
    path('update_seller_password/<int:id>', UpdateSellerPassword , name='update_seller_password'),

    # super urls 
    path('admin_super', admin_Super,name='admin_super'),
    path('delete_super/<int:id>', DeleteSuper , name='delete_super'),
    path('update_super/<int:id>', UpdateSuper , name='update_super'),
    path('update_super_password/<int:id>', UpdateSuperPassword , name='update_super_password'),



    # ajax methods
    path('admin_view_id/', adminViewId , name='admin_view_id'),






]

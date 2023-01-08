from django.urls import path,include
from .views import SellerView, Home ,Sellerkeys,SellerTrns , SellerProxy , SellerHistory,Logout , SellerRenewId  , test
# ajax
from .views import SellerViewId , DeleteIp
# api
from .views import ChangePasswordView , VerifyKey , TransactionAPI , change_self_password , configuration

urlpatterns = [
    path('', Home,name='home'),
    path('test', test,name='test'),

    path('seller_view', SellerView,name='seller_view'),
    path('seller_keys', Sellerkeys,name='seller_keys'),
    path('seller_transaction', SellerTrns,name='seller_transaction'),
    path('seller_proxy', SellerProxy,name='seller_proxy'),
    path('seller_history', SellerHistory,name='seller_history'),

    path('seller_renew_id/<str:id>', SellerRenewId , name='seller_renew_id'),
    path('logout', Logout,name='logout'),
    path('delete_seller_ip/<int:id>', DeleteIp , name='delete_seller_ip'),

# ajax methods
    path('seller_view_id/', SellerViewId , name='seller_view_id'),

# api 
    path('api/v1/update_password/', ChangePasswordView.as_view() , name='update_password'),
    path('api/v1/verify/', VerifyKey.as_view() , name='verify_key'),
    path('api/v1/transactions/', TransactionAPI.as_view() , name='transaction_api'),
 
#  common urls 
    path('change_self_password/', change_self_password , name='change_self_password'),
    path('configuration/', configuration , name='configuration'),

]

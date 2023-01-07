from django.http import JsonResponse
from django.shortcuts import redirect, render , HttpResponse
from django.contrib.auth import authenticate

from app.models import  Key, History, Trns, User , Configuration
from django.contrib.auth import login , logout
from django.db.models import Q
from django.utils import timezone
from datetime import date, timedelta
from django.db import IntegrityError
import os, sys, socket
from app.helper_functions import all_under_user

from .serializer import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ipaddr import client_ip
# test

def test(request):
    if not request.user.is_authenticated:
        return redirect('home')
    
    return render(request, 'app/test.html')

#today date to expirey date
def SellerView(request):
    if not request.user.is_authenticated:
        return redirect('home')

    users = all_under_user(request.user.username)
    include_logged_users=[]
    include_logged_users += users
    include_logged_users.append(request.user.username)

    total_id      = Key.objects.filter(created_by__username__in =include_logged_users).count()
    active_id     = Key.objects.filter(Q(expired_at__gt=timezone.now()) | Q(expired_at=None) , created_by__username__in =include_logged_users).count()
    inactive_id   = Key.objects.filter(created_by__username__in =include_logged_users).exclude(Q(expired_at__gt=timezone.now()) | Q(expired_at=None)).count()
    today_sold_id = Key.objects.filter( created_at__date=date.today() , created_by__username__in =include_logged_users).count()

    context =  {
        'credit'       :request.user.credit,
        'username'     :request.user.username,
        'total_id'     :total_id,
        'active_id'    :active_id,
        'inactive_id'  :inactive_id,
        'today_sold_id':today_sold_id
        }

    return render(request,'app/seller/seller_view.html', context)




def SellerTrns(request):
    
    if not request.user.is_authenticated:
        return redirect('home')
    
    users = all_under_user(request.user.username)
    include_logged_users=[]
    include_logged_users += users
    include_logged_users.append(request.user.username)
    
    data =  Trns.objects.filter(created_by__username__in = include_logged_users ).order_by('-created_at')

    return render(request,'app/seller/seller_transaction.html',{'username':request.user.username,'data':data})




def SellerProxy(request):
    if not request.user.is_authenticated:
        return redirect('home')

    users = all_under_user(request.user.username)
    include_logged_users=[]
    include_logged_users += users
    include_logged_users.append(request.user.username)

    keys = Key.objects.filter(created_by__username__in = include_logged_users).order_by('-created_at')
    ips = keys.exclude(ip="None").order_by('-created_at')

    # ''' TODO : form submit action '''
    if request.method=='POST':

        # ''' NOTE : getting creds from form  '''
        userid   = request.POST['userid']
        ip       = request.POST['ip']

        # ''' TODO : add ip to userid '''
        userid_obj = Key.objects.get(user_id = userid )
        userid_obj.ip = ip.strip()
        userid_obj.save()

        keys = Key.objects.filter(created_by__username__in = include_logged_users).order_by('-created_at')
        ips = keys.exclude(ip="None").order_by('-created_at')
        
        context = {
                'username':request.user.username ,
                'keys':keys ,
                'ips':ips,
                'ip_add':True,
                'ip':ip,
                'userid':userid
                }

        return render(request,'app/seller/seller_proxy.html',context)


    context = {
        'username':request.user.username ,
         'keys':keys ,
          'ips':ips
          }

    return render(request,'app/seller/seller_proxy.html',context)


# renew id
def SellerRenewId(request,id):
    if not request.user.is_authenticated:
        return redirect('home')

    users = all_under_user(request.user.username)
    include_logged_users=[]
    include_logged_users += users
    include_logged_users.append(request.user.username)

    if int(request.user.credit) <= 0:
        username      = request.user.username
        data =  Key.objects.filter(created_by__username__in = include_logged_users).order_by('-created_at')
        return render(request,'app/super/super_keys.html',{'key_renwed_failed':True ,'data':data ,'username':username})

    data          = Key.objects.filter(created_by__username__in =include_logged_users).order_by('-created_at')
    key           = Key.objects.get(user_id=id)
    key.expired_at= timezone.now() + timedelta(days=30)
    key.save()
    
    # Decrease credit on renew
    seller_data = User.objects.create(pk=request.user.id)
    seller_data.credit -=1
    seller_data.save()

    return render(request,'app/seller/seller_keys.html',{'key_renwed':True,'key':key ,'data':data ,'username':username})





def SellerHistory(request):
    if not request.user.is_authenticated:
        return redirect('home')

    users = all_under_user(request.user.username)
    include_logged_users=[]
    include_logged_users += users
    include_logged_users.append(request.user.username)

    data =  History.objects.filter(creater_name__username__in = include_logged_users).order_by('-created_at')
    
    return render(request,'app/seller/seller_history.html',{'username':request.user.username,'data':data})





def Sellerkeys(request):
    if not request.user.is_authenticated:
        return redirect('home')
    
    users = all_under_user(request.user.username)
    include_logged_users=[]
    include_logged_users += users
    include_logged_users.append(request.user.username)

    data          = Key.objects.filter(created_by__username__in =include_logged_users).order_by('-created_at')
    
    # ''' TODO : form submit action '''
    if request.method=='POST':

        # ''' NOTE : getting creds from form  '''
        customer_name = request.POST['client_name']
        user_id       = request.POST['client_id']
        version       = request.POST['client_version']
        username      = request.user.username

        if int(request.user.credit) <= 0:
            return render(request,'app/seller/seller_keys.html',{'key_added_failed':True ,'data':data ,'username':request.user.username})

        try:
            key_obj =  Key.objects.create(customer_name = customer_name , user_id=user_id , version = version ,created_by = request.user)
        except IntegrityError:
            return render(request,'app/seller/seller_keys.html',{'key_already_exists':True,'key':user_id ,'data':data ,'username':username})
        except Exception as e :
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return HttpResponse(f"<p  style='color:red;'>{exc_type} : `{e}` Error at line `{exc_tb.tb_lineno}` in `{fname}` .</p>")

        # ''' update user for decrease credit '''
        user_obj = User.objects.get(pk=request.user.id)
        user_obj.credit -=1
        user_obj.save()

        # ''' NOTE : create history object'''
        history_obj = History.objects.create(  name = customer_name , user_id=user_id , mode = "DEDUCT" ,creater_name = request.user )
        data        = Key.objects.filter(created_by__username__in =include_logged_users).order_by('-created_at')
        
        return render(request,'app/seller/seller_keys.html',{'key_added':True,'key':user_id ,'data':data ,'username':username})


    return render(request,'app/seller/seller_keys.html',{'data':data ,'username':request.user.username})




def Home(request):
    if  request.user.is_authenticated:
        username  = request.user.username
        usern     = User.objects.get(username=username)
        is_seller =  usern.is_seller
        is_super  =  usern.is_super
        is_admin  =  usern.is_admin
        if is_seller:
            return redirect('seller_view')

        elif is_super:
            return redirect('super_view')

        elif is_admin:
            return redirect('admin_view')

        else:
            redirect('home')

    if request.method=='POST':

        # ''' NOTE : getting creds from form  '''
        username = request.POST['username']
        password = request.POST['password']
        usertype = request.POST['usertype']

        # ''' TODO : authenticating  '''
        user =  authenticate(username= username , password=password)

        # ''' NOTE : if creds are valid   '''
        if user:
            users = all_under_user(user.username)
            include_logged_users=[]
            include_logged_users += users
            include_logged_users.append(username)

            # ''' NOTE : check usertype admin is correct for creds    '''
            if usertype=='admin':
                is_admin = User.objects.filter(username = user.username , is_admin=True)
                
                # ''' TODO : show a warning popup and return to login again '''
                if not is_admin:
                    return render(request,'app/index.html',{ 'not_admin' :True})
                login(request,user)             #''' TODO : redirect to view page for super    '''
                
                # ''' NOTE Get total id , activate and deactivated Ids to show on homepage '''
                total_id      = Key.objects.all().count()
                total_seller  = User.objects.filter(is_seller= True).count()
                total_super   = User.objects.filter(is_super= True).count()
                active_id     = Key.objects.filter(Q(expired_at__gt=timezone.now()) | Q(expired_at=None) ).count()
                inactive_id   = Key.objects.all().exclude(Q(expired_at__gt=timezone.now()) | Q(expired_at=None) ).count()
                today_sold_id = Key.objects.filter( created_at__date=date.today() ).count()

                context =  {
                    'username'     :username,
                    'total_id'     :total_id,
                    'active_id'    :active_id,
                    'inactive_id'  :inactive_id,
                    'today_sold_id':today_sold_id,
                    'total_seller' :total_seller,
                    'total_super'  :total_super,
                    'admin_login'  :True
                    }


                # ''' TODO : redirect to view page for admin    '''

                return render(request,'app/admin/admin_view.html',context)


            elif usertype=='super':
                # ''' NOTE : check usertype super is correct for creds    '''
                is_super = User.objects.filter(username = user.username , is_super=True)
                
                # ''' TODO : show a warning popup and return to login again '''
                if not is_super:
                    return render(request,'app/index.html',{ 'not_super' :True})
                login(request,user)         #''' TODO : redirect to view page for super    '''

                # ''' NOTE Get total id , activate and deactivated Ids to show on homepage'''
                total_seller  = User.objects.filter(username__in  = users).count()
                total_id      = Key.objects.filter(created_by__username__in = include_logged_users ).count()
                active_id     = Key.objects.filter(Q(expired_at__gt=timezone.now()) | Q(expired_at=None) , created_by__username__in = include_logged_users).count()
                inactive_id   = Key.objects.filter(created_by__username__in = include_logged_users).exclude(Q(expired_at__gt=timezone.now()) | Q(expired_at=None) ).count()
                today_sold_id = Key.objects.filter( created_at__date=date.today() ,created_by__username__in = include_logged_users).count()

                context =  {
                    'credit':request.user.credit,
                    'username':username,
                    'super_login':True,
                    'total_id':total_id,
                    'active_id':active_id,
                    'total_seller':total_seller,
                    'inactive_id':inactive_id,
                    'today_sold_id':today_sold_id
                    }

                # ''' TODO : redirect to view page for seller    '''
                return render(request,'app/super/super_view.html',context)


            elif usertype=='seller':
                # ''' NOTE : check usertype seller is correct for creds    '''
                is_seller = User.objects.filter(username = user.username , is_seller=True)

                # ''' TODO : show a warning popup and return to login again '''
                if not is_seller:
                    return render(request,'app/index.html',{ 'not_seller' :True})

                login(request,user)

                # ''' NOTE Get total id , activate and deactivated Ids to show on homepage'''
                total_id = Key.objects.filter(created_by__username__in = include_logged_users).count()
                active_id = Key.objects.filter(Q(expired_at__gt=timezone.now()) | Q(expired_at=None) ,created_by__username__in = include_logged_users).count()
                inactive_id = Key.objects.filter( created_by__username__in = include_logged_users).exclude(Q(expired_at__gt=timezone.now()) | Q(expired_at=None)).count()
                today_sold_id = Key.objects.filter( created_at__date=date.today() ,created_by__username__in = include_logged_users).count()

                context =  {
                    'credit':request.user.credit,
                    'username':username,
                    'seller_login':True,
                    'total_id':total_id,
                    'active_id':active_id,
                    'inactive_id':inactive_id,
                    'today_sold_id':today_sold_id
                    }

                # ''' TODO : redirect to view page for seller    '''
                return render(request,'app/seller/seller_view.html',context)


            return render(request,'app/index.html',{ 'usernone' :True})

        return render(request,'app/index.html',{'error':'given creds are invalid!', 'invalid_creds' :True})

    return render(request,'app/index.html')



def Logout(request):
    logout(request)
    return redirect('home')


def SellerViewId(request):
    data = {}
    if request.method == 'GET':
            user_id = request.GET['user_id']
            key_queryset = Key.objects.filter(user_id=user_id).values('user_id','created_by','customer_name','expired_at','version') #getting
            data['Key']  = list(key_queryset)

            return JsonResponse(data , safe=False) # Sending an success response
    else:
            return HttpResponse("Request method is not a GET")



# delete ip
def DeleteIp(request,id):
    if not request.user.is_authenticated:
        return redirect('home')

    key = Key.objects.get(id=id)
    key.ip = "None"
    key.save()

    username      = request.user.username
    users = all_under_user(username)
    include_logged_users=[]
    include_logged_users += users
    include_logged_users.append(username)

    keys =  Key.objects.filter(created_by__username__in = include_logged_users).order_by('-created_at')
    ips = keys.exclude(ip="None").order_by('-created_at')

    context = {
                'username':username ,
                'keys':keys ,
                'ips':ips,
                'ip_delete':True,
                }

    return render(request,'app/seller/seller_proxy.html',context)




class TransactionAPI(APIView):

    serializer_class = Transactionializer

    def post(self, request, *args, **kwargs):
        serializer = Transactionializer(data=request.data)

        if serializer.is_valid():
            request_data = serializer.data
            # request parameters
            key         = request_data.get('key', 'key not found!!!')
            destination = request_data.get('destination', 'destination not found!!!')
            train_no    = request_data.get('train_no', 'train_no not found!!!')
            trn_status  = request_data.get('trn_status', 'trn_status not found!!!')
            pnr_time    = request_data.get('pnr_time', 'pnr_time not found!!!')
            payment_type= request_data.get('payment_type', 'payment_type not found!!!')

            getkeyinfo =  Key.objects.get(Q(expired_at__gt=timezone.now()) | Q(expired_at=None),user_id = key )
            key_creator=  getkeyinfo.created_by.username

            getuser    =  User.objects.get(username = key_creator )

            # ''' TODO : save transaction '''

            trn_obj   = Trns(designation =  destination , train_no = train_no , gateway = payment_type , pnr_time = pnr_time , status = trn_status , created_by =getuser )
            trn_obj.save()

            return Response({"Details": "transaction saved successfully..."}, status=status.HTTP_200_OK)


        else:
            # return Response({"Key": ["failed."]}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)






# ''' NOTE : verify key Api-  code '''
class VerifyKey(APIView):

    serializer_class = VerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = VerifySerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
          
        request_data = serializer.data
        key = request_data.get('key', 'key not found!!!') # request parameters
        
        ipaddr = client_ip(request)
        print('********** ipaddr : ' , ipaddr)#TODO : send ip in message by bot on tg 
        
        obj  = Configuration.objects.last()
    
        if not obj:
            app_version = ""
            dll_version = ""
            message = ""
            short_message = ""
            news = ""
        else:
            app_version = obj.app_version
            dll_version = obj.dll_version
            message = obj.message
            short_message = obj.short_message
            news = obj.news

        
        manager = Key.objects.filter(user_id = key)
        
        if  not manager.exists():
            return Response({"Details": "Invalid Key!"}, status=status.HTTP_400_BAD_REQUEST)
            
        if  not manager.filter(  Q( expired_at__gte=timezone.now() )  ).exists():
            return Response({
                                "success":False,
                                "message":"this key has been expired please contact to your owner.",
                                "token":"",
                                "app_version":app_version,
                                "news":news,
                                "KeyType":"monthly",
                                "PaidStatus":"Unpaid",
                                "DllVersion":dll_version,
                                "ChromeDriver":"2222",
                                "ChromeVersion":"4444",
                                }, status=status.HTTP_400_BAD_REQUEST)
        
        
        if  not manager.filter(is_login = False).exists():
            return Response({
                                "success":False,
                                "message":"Already login with this key, Please contact to your owner.",
                                "token":"",
                                "app_version":app_version,
                                "news":news,
                                "KeyType":"monthly",
                                "PaidStatus":"Unpaid",
                                "DllVersion":dll_version,
                                "ChromeDriver":"2222",
                                "ChromeVersion":"4444",
                                }, status=status.HTTP_400_BAD_REQUEST) #update reponse
        
        if  not manager.filter(pay_status = True).exists():
            return Response({
                                "success":False,
                                "message":"This key is unpaid , Please contact to your owner.",
                                "token":"",
                                "app_version":app_version,
                                "news":news,
                                "KeyType":"monthly",
                                "PaidStatus":"Unpaid",
                                "DllVersion":dll_version,
                                "ChromeDriver":"2222",
                                "ChromeVersion":"4444",
                                }, status=status.HTTP_400_BAD_REQUEST) #update reponse
        
        manager = Key.objects.get(user_id = key)
        manager.is_login = True
        manager.save()
        
        success_context = {
            "success":True,
            "message":message,
            "left_days":manager.validity(),
            "token":"",
            "app_version":app_version,
            "ip_list":[manager.ip],
            "short_message":short_message,
            "news":news,
            "KeyType":"monthly",
            "PaidStatus":"Paid"  if  manager.pay_status else "Unpaid",
            "DllVersion":dll_version,
            "ChromeDriver":"2222",
            "ChromeVersion":"4444",
            "SaltKey":manager.user_id
            }
        
        return Response(success_context, status=status.HTTP_200_OK)
        

        
        


# ''' NOTE : update password Api  code '''
class ChangePasswordView(UpdateAPIView):
        # """
        # An endpoint for changing password.
        # """
        serializer_class = ChangePasswordSerializer
        model = User
        permission_classes = (IsAuthenticated,)

        def get_object(self, queryset=None):
            obj = self.request.user
            return obj

        def update(self, request, *args, **kwargs):
            self.object = self.get_object()
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                # Check old password
                if not self.object.check_password(serializer.data.get("old_password")):
                    return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
                # set_password also hashes the password that the user will get
                self.object.set_password(serializer.data.get("new_password"))
                self.object.save()
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Password updated successfully',
                    'data': []
                }

                return Response(response)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def change_self_password(request):
    if not request.user.is_authenticated:
        return redirect('home')
    
    
    if request.method=='POST':
        # ''' NOTE : getting passwords and username from form  '''
        old_password   = request.POST['old_password']
        new_password   = request.POST['new_password']
        username_param   = request.POST['username']
        
        # NOTE : user exists or not 
        is_exists =  User.objects.filter(pk = request.user.id )
        if not is_exists:
            return render(request,'app/change_self_password.html' ,{'error':f'User not found by this username `{username_param}` !!!'})
        
        # NOTE : old password is valid or not for logged user
        user_obj =  User.objects.get(pk = request.user.id )
        if not user_obj.check_password(old_password):
            return render(request,'app/change_self_password.html' ,{'error':f'Please enter valid old password !!! '})
        
        # TODO : update new passeord
        user_obj.set_password(new_password)
        user_obj.save()
        
        # TODO : return according to role 
        # if user_obj.is_admin:
        #     return render(request,'app/admin/admin_view.html', {'password_changed': True})
        # elif user_obj.is_super:
        #     return render(request,'app/super/super_view.html', {'password_changed': True})
        # elif user_obj.is_seller:
        #     return render(request,'app/seller/seller_view.html',{'password_changed': True})
        # else:
        #     return redirect('home')

        return render(request,'app/index.html', {'password_changed': True})
        
        
    return render(request,'app/change_self_password.html')




def configuration(request):
    if not request.user.is_authenticated:
        return redirect('home')
    
    
    if request.method=='POST':
        # ''' NOTE : getting config data from form  '''

        app_version   = request.POST['app_version']
        dll_version   = request.POST['dll_version']
        message       = request.POST['message']
        short_message = request.POST['short_message']
        news          = request.POST['news']

        create_obj = Configuration.objects.create(app_version= app_version ,
                                                  dll_version =dll_version , 
                                                  message = message ,
                                                  short_message = short_message ,
                                                  news = news  )
        
        if request.user.is_admin:
            return render(request,'app/admin/admin_view.html', {'conf_saved': True})
        elif request.user.is_super:
            return render(request,'app/super/super_view.html', {'conf_saved': True})
        else:
            return redirect('home')
        
    
    obj  = Configuration.objects.last()
    
    if not obj:
        app_version = ""
        dll_version = ""
        message = ""
        short_message = ""
        news = ""
    else:
        app_version = obj.app_version
        dll_version = obj.dll_version
        message = obj.message
        short_message = obj.short_message
        news = obj.news

    context = {
        
        'app_version': app_version,
        'dll_version': dll_version,
        'message': message,
        'short_message': short_message,
        'news': news,
        }


    return render(request,'app/config.html' , context)

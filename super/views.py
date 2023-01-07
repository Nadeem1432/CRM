from django.forms import PasswordInput
from django.http import JsonResponse
from django.shortcuts import redirect, render , HttpResponse
from django.contrib.auth import authenticate

from app.models import  Key, History, Trns, User
from django.contrib.auth import login , logout
from django.db.models import Q
from django.utils import timezone
from datetime import date, timedelta
from django.db import IntegrityError
import os ,sys
from app.helper_functions import all_under_user

#today date to expirey date
def superView(request):
    if not request.user.is_authenticated:
        return redirect('home')
    
    users = all_under_user(request.user.username)
    include_logged_users=[]
    include_logged_users += users
    include_logged_users.append(request.user.username)
    
    
    total_id      = Key.objects.filter(created_by__username__in = include_logged_users).count()
    total_seller  = User.objects.filter(username__in = users ).count()
    active_id     = Key.objects.filter(Q(expired_at__gt=timezone.now()) | Q(expired_at=None) , created_by__username__in = include_logged_users).count()
    inactive_id   = Key.objects.filter( created_by__username__in = users).exclude(Q(expired_at__gt=timezone.now()) | Q(expired_at=None) ).count()
    today_sold_id = Key.objects.filter( created_at__date=date.today() , created_by__username__in = include_logged_users).count()

    
    context =  {
        'credit':request.user.credit,
        'username':request.user.username,
        'total_id':total_id,
        'active_id':active_id,
        'inactive_id':inactive_id,
        'today_sold_id':today_sold_id,
        'total_seller':total_seller
        }

    return render(request,'app/super/super_view.html', context)





def superTrns(request):
    if not request.user.is_authenticated:
        return redirect('home')

    users = all_under_user(request.user.username)
    include_logged_users=[]
    include_logged_users += users
    include_logged_users.append(request.user.username)

    data =  Trns.objects.filter(created_by__username__in = include_logged_users ).order_by('-created_at')
    
    return render(request,'app/super/super_transaction.html',{'username':request.user.username,'data':data})




def superProxy(request):
    if not request.user.is_authenticated:
        return redirect('home')

    users = all_under_user(request.user.username)
    include_logged_users=[]
    include_logged_users += users
    include_logged_users.append(request.user.username)

    # ''' Get User '''
    keys = Key.objects.filter(created_by__username__in = include_logged_users ).order_by('-created_at')
    ips  = keys.exclude(ip = "None").order_by('-created_at')
    
    # ''' TODO : form submit action '''
    if request.method=='POST':

        # ''' NOTE : getting creds from form  '''
        userid   = request.POST['userid']
        ip       = request.POST['ip']
        
        # ''' TODO : add ip to userid '''
        userid_obj = Key.objects.get(user_id = userid ) 
        userid_obj.ip = ip.strip()
        userid_obj.save()
        
        keys =  Key.objects.filter(created_by__username__in = include_logged_users ).order_by('-created_at')
        ips = keys.exclude(ip="None")

        context = {
                'username':request.user.username ,
                'keys':keys ,
                'ips':ips,
                'ip':ip,
                'userid':userid,
                'ip_add':True
                }

        return render(request,'app/super/super_proxy.html',context)

    context = {
        'username':request.user.username ,
         'keys':keys ,
          'ips':ips
          }

    return render(request,'app/super/super_proxy.html',context)


# renew id
def superRenewId(request,id):
    if not request.user.is_authenticated:
        return redirect('home')
    
    users = all_under_user(request.user.username)
    include_logged_users=[]
    include_logged_users += users
    include_logged_users.append(request.user.username)

    if int(request.user.credit) <= 0:
        data =  Key.objects.filter(created_by__username__in = include_logged_users).order_by('-created_at')
        return render(request,'app/super/super_keys.html',{'key_renwed_failed':True ,'data':data ,'username':request.user.username})

    data =  Key.objects.filter(created_by__username__in = include_logged_users).order_by('-created_at')
    
    ''' increase more 29 days from today'''
    key = Key.objects.get(user_id=id)
    key.expired_at = timezone.now() + timedelta(days=30)
    key.save()
    
    # Decrease credit on renew
    user =  User.objects.get(pk=request.user.id)
    user.credit -=1
    user.save()

    return render(request,'app/super/super_keys.html',{'key_renwed':True,'key':key ,'data':data ,'username':request.user.username})
    










def superHistory(request):
    if not request.user.is_authenticated:
        return redirect('home')

    users = all_under_user(request.user.username)
    include_logged_users=[]
    include_logged_users += users
    include_logged_users.append(request.user.username)

    data =  History.objects.filter(creater_name__username__in = include_logged_users).order_by('-created_at')

    username      = request.user.username
    return render(request,'app/super/super_history.html',{'username':username,'data':data})




def superkeys(request):
    if not request.user.is_authenticated:
        return redirect('home')

    username      = request.user.username
    users = all_under_user(request.user.username)
    include_logged_users=[]
    include_logged_users += users
    include_logged_users.append(request.user.username)

    data =  Key.objects.filter(created_by__username__in = include_logged_users).order_by('-created_at')
    
    # ''' TODO : form submit action '''
    if request.method=='POST':

        # ''' NOTE : getting creds from form  '''
        customer_name = request.POST['client_name']
        user_id       = request.POST['client_id']
        version       = request.POST['client_version']
        username      = request.user.username

        if int(request.user.credit) <= 0:

            keys =  Key.objects.filter(created_by__username__in = include_logged_users).order_by('-created_at')
            ips = keys.exclude(ip="None").order_by('-created_at')
            return render(request,'app/super/super_keys.html',{'username':request.user.username ,'keys':keys ,'ips':ips,'key_added_failed':True})
        
        try:
            key_obj =  Key.objects.create(customer_name = customer_name , user_id=user_id , version = version ,created_by = request.user)
        except IntegrityError:
            return render(request,'app/super/super_keys.html',{'key_already_exists':True,'key':user_id ,'data':data ,'username':username})
        except Exception as e :
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return HttpResponse(f"<p   style='color:red;'>{exc_type}  `{e}` Error at line `{exc_tb.tb_lineno}` in `{fname}` .</p>")

        # ''' update user for decrease credit '''
        user_obj = User.objects.get(pk=request.user.id)
        user_obj.credit -=1
        user_obj.save()

        # ''' NOTE : create history object'''
        history_obj = History.objects.create(  name = customer_name , user_id=user_id , mode = "DEDUCT" ,creater_name = request.user )

        return render(request,'app/super/super_keys.html',{'key_added':True,'key':user_id ,'data':data ,'username':username})

    
    return render(request,'app/super/super_keys.html',{'data':data ,'username':username})



def superViewId(request):
    data = {}
    if request.method == 'GET':
            user_id = request.GET['user_id']
            key_queryset = Key.objects.filter(user_id=user_id).values('user_id','created_by','customer_name','expired_at','version') #getting 
            data['Key']  = list(key_queryset)
            return JsonResponse(data , safe=False) # Sending an success response
    else:
            return HttpResponse("Request method is not a GET")



# delete ip
def DeleteSuperIp(request,id):
    if not request.user.is_authenticated:
        return redirect('home')
    
    key    = Key.objects.get(id=id)
    key.ip = "None"
    key.save()
    
    users = all_under_user(request.user.username)
    include_logged_users=[]
    include_logged_users += users
    include_logged_users.append(request.user.username)

    keys = Key.objects.filter(created_by__username__in = include_logged_users).order_by('-created_at')
    ips = keys.exclude(ip="None").order_by('-created_at')

    context = {
                'username':request.user.username ,
                'keys':keys ,
                'ips':ips,
                'ip_delete':True,
                }
    return render(request,'app/super/super_proxy.html',context)


# delete seller
def DeleteSeller(request,id):
    if not request.user.is_authenticated:
        return redirect('home')
    
    User.objects.filter(id=id).delete()

    users = all_under_user(request.user.username)
    include_logged_users=[]
    include_logged_users += users
    include_logged_users.append(request.user.username)

    sellers =  User.objects.filter(username__in=users)
    
    context = {
                'username':request.user.username,
                'sellers':sellers,
                'seller_delete':True,
                }
    return render(request,'app/super/super_seller.html',context)



# update seller
def UpdateSeller(request,id):
    if not request.user.is_authenticated:
        return redirect('home')
    
    
    if request.method=='POST':
        # ''' NOTE : getting creds from form  '''
        seller_credit   = request.POST['seller_credit']
        
        users = all_under_user(request.user.username)
        include_logged_users=[]
        include_logged_users += users
        include_logged_users.append(request.user.username)

        if int(request.user.credit) <= 0:
            sellers =  User.objects.filter(username__in=users)
            return render(request,'app/super/super_seller.html',{'send_credit_failed':True , 'sellers':sellers , 'username':request.user.username})
        
        creator_obj = User.objects.get(pk=request.user.id)

        # ''' NOTE : Decrease credit of super '''
        creator_obj.credit -=int(seller_credit)
        creator_obj.save()

        # ''' NOTE : increase seller's credit '''
        seller = User.objects.get(id=id)   
        seller.credit += int(seller_credit)
        seller.save()

        # ''' NOTE : create history object'''
        seller_history_obj = History.objects.create(  name = seller.username , mode = "DEDUCT"   ,credit = int(seller_credit) , creater_name = request.user)

        # ''' TODO : successfullly added and render data to templates '''
        sellers =  User.objects.filter(username__in=users)
        return render(request,'app/super/super_seller.html',{'username':request.user.username,'sellers':sellers,'credit_sent':True , 'reciever':seller.username , 'credits':seller_credit})

        
    seller = User.objects.filter(id=id)   
    context = {
            'seller':seller
                }
    return render(request,'app/super/seller_update.html',context)




def super_Seller(request):
    if not request.user.is_authenticated:
        return redirect('home')

    users = all_under_user(request.user.username)

    username      = request.user.username
    sellers =  User.objects.filter(username__in = users)

    if request.method=='POST':

        # ''' NOTE : getting creds from form  '''
        seller_username = request.POST['seller_username']
        seller_password = request.POST['seller_password']
        seller_credit   = request.POST['seller_credit']

        if not seller_credit:
            seller_credit = 0

        # ''' NOTE : Check super has credit or not '''
        if int(request.user.credit) <= 0:
            sellers       =  User.objects.filter(username__in=users )
            return render(request,'app/super/super_seller.html',{'seller_added_failed':True , 'sellers':sellers , 'username':request.user.username})

        # ''' NOTE : Decrease credit of super '''
        creator_obj = User.objects.get(pk = request.user.id)
        creator_obj.credit -= int(seller_credit)
        creator_obj.save()


        # '''NOTE: check seller is already exists or not'''        
        is_already = User.objects.filter(username=seller_username).exists()
        if is_already:
                return render(request,'app/super/super_seller.html',{'username':username,'sellers':sellers,'user_already_exists':True})
        
        # '''TODO: create seller '''
        seller_obj = User.objects.create_user(username=seller_username , password = seller_password ,seller_pass=seller_password , credit = seller_credit , is_seller = True , created_by = username) 

        # ''' NOTE : create history object'''
        seller_history_obj = History.objects.create( name = seller_username , mode = "DEDUCT" ,credit = int(seller_credit) , creater_name = creator_obj)

        # ''' TODO : successfullly added and render data to templates '''
        username      = request.user.username
        users = all_under_user(request.user.username)
        sellers =  User.objects.filter(username__in=users )
        return render(request,'app/super/super_seller.html',{'username':username,'sellers':sellers,'seller_created':True})
        

    return render(request,'app/super/super_seller.html',{'username':username,'sellers':sellers})





# update seller
def UpdateSellerPassword(request,id):
    if not request.user.is_authenticated:
        return redirect('home')
    
    
    if request.method=='POST':

        # ''' NOTE : getting password from form  '''
        seller_password   = request.POST['seller_password']

        # ''' TODO : update password here '''
        seller = User.objects.get(id=id)   
        seller.set_password(seller_password)
        seller.seller_pass = seller_password
        seller.save()

        # ''' TODO : successfullly added and render data to templates '''
        users = all_under_user(request.user.username)
        include_logged_users=[]
        include_logged_users += users
        include_logged_users.append(request.user.username)

        sellers =  User.objects.filter(username__in =users )
        
        return render(request,'app/super/super_seller.html',{'username':request.user.username,'sellers':sellers,'password_changed':True , 'victim':seller.username , 'password':seller_password})

    return redirect('home')
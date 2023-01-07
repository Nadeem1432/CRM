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

import os , sys

#today date to expirey date
def adminView(request):
    if not request.user.is_authenticated:
        return redirect('home')

    username      = request.user.username
    total_id      = Key.objects.all().count()
    total_seller  = User.objects.filter(is_seller = True).count()
    total_super   = User.objects.filter(is_super = True).count()
    active_id     = Key.objects.filter(Q(expired_at__gt=timezone.now()) | Q(expired_at=None) ).count()
    inactive_id   = Key.objects.all().exclude(Q(expired_at__gt=timezone.now()) | Q(expired_at=None) ).count()
    today_sold_id = Key.objects.filter( created_at__date=date.today()).count()

    
    context =  {
        # 'credit':credits,
        'username':username,
        'total_id':total_id,
        'active_id':active_id,
        'inactive_id':inactive_id,
        'today_sold_id':today_sold_id,
        'total_seller':total_seller,
        'total_super':total_super
        }

    return render(request,'app/admin/admin_view.html', context)





def adminTrns(request):
    if not request.user.is_authenticated:
        return redirect('home')

    data =  Trns.objects.all().order_by('-created_at')

    username      = request.user.username
    return render(request,'app/admin/admin_transaction.html',{'username':username,'data':data})




def adminProxy(request):
    if not request.user.is_authenticated:
        return redirect('home')

    # ''' Get User '''
    keys =  Key.objects.all().order_by('-created_at')
    ips = keys.exclude(ip="None")
    username      = request.user.username

    # ''' TODO : form submit action '''
    if request.method=='POST':

        # ''' NOTE : getting creds from form  '''
        userid   = request.POST['userid']
        ip       = request.POST['ip']
        
        # ''' TODO : add ip to userid '''
        userid_obj = Key.objects.get(user_id = userid ) 
        userid_obj.ip = ip.strip()
        userid_obj.pay_status = True
        userid_obj.save()

        keys =  Key.objects.all().order_by('-created_at')
        ips = keys.exclude(ip="None")

        context = {
                'username':username ,
                'keys':keys ,
                'ips':ips,
                'ip_add':True,
                'ip':ip,
                'userid':userid
                }

        return render(request,'app/admin/admin_proxy.html',context)


    context = {
        'username':username ,
         'keys':keys ,
          'ips':ips
          }

    return render(request,'app/admin/admin_proxy.html',context)


# renew id
def adminRenewId(request,id):
    if not request.user.is_authenticated:
        return redirect('home')
    
    # ''' Get User '''
    data =  Key.objects.all().order_by('-created_at')
    
    # '''NOTE: increase more 29 days from today'''
    if Key.objects.filter(user_id=id).exists():
        key = Key.objects.get(user_id=id)
        key.expired_at = timezone.now() + timedelta(days=30)
        key.save()

    return render(request,'app/admin/admin_keys.html',{'key_renwed':True,'key':key.user_id ,'data':data ,'username':request.user.username})
    

def adminHistory(request):
    if not request.user.is_authenticated:
        return redirect('home')

    data =  History.objects.all().order_by('-created_at')
    username      = request.user.username
    return render(request,'app/admin/admin_history.html',{'username':username,'data':data})





def adminkeys(request):
    if not request.user.is_authenticated:
        return redirect('home')

    username      = request.user.username
    ''' Get User '''
    user = User.objects.get(username=username)
    data =  Key.objects.all().order_by('-created_at')
    ''' TODO : form submit action '''
    if request.method=='POST':
        ''' NOTE : getting creds from form  '''
        customer_name = request.POST['client_name']
        user_id       = request.POST['client_id']
        version       = request.POST['client_version']
        username      = request.user.username


        data =  Key.objects.all().order_by('-created_at')

        try:
            key_obj =  Key.objects.create(customer_name = customer_name , user_id=user_id , version = version ,created_by = request.user)
        except IntegrityError:
            return render(request,'app/admin/admin_keys.html',{'key_already_exists':True,'key':user_id ,'data':data ,'username':username})
        except Exception as e :
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return HttpResponse(f"<p  style='color:red;'>{exc_type} : `{e}` Error at line `{exc_tb.tb_lineno}` in `{fname}` .</p>")

        # ''' NOTE : create history object'''
        history_obj = History.objects.create(  name = customer_name , user_id=user_id , mode = "DEDUCT" ,creater_name = request.user )

        return render(request,'app/admin/admin_keys.html',{'key_added':True,'key':user_id ,'data':data ,'username':username})

    
    return render(request,'app/admin/admin_keys.html',{'data':data ,'username':username})



def adminViewId(request):
    data = {}
    if request.method == 'GET':
            user_id = request.GET['user_id']
            key_queryset = Key.objects.filter(user_id=user_id).values('user_id','created_by','customer_name','expired_at','version') #getting 
            data['Key']  = list(key_queryset)
            return JsonResponse(data , safe=False) # Sending an success response
    else:
            return HttpResponse("Request method is not a GET")



# delete ip
def DeleteAdminIp(request,id):
    if not request.user.is_authenticated:
        return redirect('home')
    
    key = Key.objects.get(id=id)
    key.ip = "None"
    key.pay_status = False
    key.save()

    keys = Key.objects.all()
    ips = Key.objects.all().exclude(ip="None")
    username      = request.user.username
    
    context = {
                'username':username ,
                'keys':keys ,
                'ips':ips,
                'ip_delete':True,
                }
    return render(request,'app/admin/admin_proxy.html',context)


# delete seller
def DeleteSeller(request,id):
    if not request.user.is_authenticated:
        return redirect('home')
    
    seller = User.objects.filter(id=id).delete()
    sellers =  User.objects.filter(is_seller = True)
    
    context = {
                'username':request.user.username,
                'sellers':sellers,
                'seller_delete':True,
                }

    return render(request,'app/admin/admin_seller.html',context)


   

# update seller
def UpdateSeller(request,id):
    if not request.user.is_authenticated:
        return redirect('home')
    
    if request.method=='POST':
        username      = request.user.username
        # ''' NOTE : getting creds from form  '''
        seller_credit   = request.POST['seller_credit']

        # ''' NOTE : Check admin has credit or not '''
        creator_obj = User.objects.get(username = username)

        # ''' NOTE : increase seller's credit '''
        seller = User.objects.get(id=id)   
        seller.credit += int(seller_credit)
        seller.save()

        # ''' NOTE : create history object'''
        seller_history_obj = History.objects.create(  name = seller.username , mode = "DEDUCT"   ,credit = int(seller_credit) , creater_name = request.user)

        # ''' TODO : successfullly added and render data to templates '''
        sellers =  User.objects.filter(is_seller = True)

        return render(request,'app/admin/admin_seller.html',{'username':username,'sellers':sellers,'credit_sent':True , 'reciever':seller.username , 'credits':seller_credit})

        
        

        
    seller = User.objects.filter(id=id)   
    seller_detail = User.objects.get(id=id)   
    context = {
            'seller':seller,
            'victim':seller_detail.username
                }
    return render(request,'app/admin/seller_update.html',context)



# update seller
def UpdateSellerPassword(request,id):
    if not request.user.is_authenticated:
        return redirect('home')
    
    if request.method=='POST':
        username      = request.user.username
        # ''' NOTE : getting password from form  '''
        seller_password   = request.POST['seller_password']

        # ''' TODO : update password here '''
        seller = User.objects.get(id=id)   
        seller.set_password(seller_password)
        seller.seller_pass = seller_password
        seller.save()

        # ''' TODO : successfullly added and render data to templates '''
        sellers =  User.objects.filter(is_seller=True)
        return render(request,'app/admin/admin_seller.html',{'username':username,'sellers':sellers,'password_changed':True , 'victim':seller.username , 'password':seller_password})

    return redirect('home')




def admin_Seller(request):
    if not request.user.is_authenticated:
        return redirect('home')

    username      = request.user.username
    sellers       =  User.objects.filter(is_seller = True)

    if request.method=='POST':

        # ''' NOTE : getting creds from form  '''
        seller_username = request.POST['seller_username']
        seller_password = request.POST['seller_password']
        seller_credit   = request.POST['seller_credit']

        if not seller_credit:
            seller_credit = 0

        # ''' NOTE : create history object'''
        seller_history_obj = History.objects.create(  name = seller_username , mode = "DEDUCT"   ,credit = int(seller_credit) , creater_name = request.user)

        # '''NOTE: check seller is already exists or not'''        
        is_already = User.objects.filter(username=seller_username).exists()
        if is_already:
                return render(request,'app/admin/admin_seller.html',{'username':username,'sellers':sellers,'user_already_exists':True})
        
        # '''TODO: create seller '''
        seller_obj = User.objects.create_user(username=seller_username , password = seller_password ,seller_pass=seller_password , credit = seller_credit , is_seller = True , created_by = username) 

        # ''' TODO : successfullly added and render data to templates '''
        sellers =  User.objects.filter(is_seller = True)

        return render(request,'app/admin/admin_seller.html',{'username':username,'sellers':sellers,'seller_created':True})


    return render(request,'app/admin/admin_seller.html',{'username':username,'sellers':sellers})







# '''  Super's code ''' 
def admin_Super(request):
    if not request.user.is_authenticated:
        return redirect('home')

    username      = request.user.username
    supers       =  User.objects.filter(is_super = True)

    if request.method=='POST':

        # ''' NOTE : getting creds from form  '''
        super_username = request.POST['super_username']
        super_password = request.POST['super_password']
        super_credit   = request.POST['super_credit']
        
        if not super_credit:
            super_credit = 0
            


        # ''' TODO : successfullly added and render data to templates '''
        username      = request.user.username
        supers =  User.objects.filter(is_super = True)
        
        # '''NOTE: check seller is already exists or not'''        
        is_already = User.objects.filter(username=super_username).exists()
        if is_already:
                return render(request,'app/admin/admin_super.html',{'username':username,'supers':supers,'user_already_exists':True})

        # '''TODO: create super '''
        super_obj = User.objects.create_user(username=super_username , password = super_password ,super_pass=super_password , credit = super_credit , is_super = True , created_by = username) 

        # ''' NOTE : create history object'''
        super_history_obj = History.objects.create(  name = super_username , mode = "DEDUCT"   ,credit = int(super_credit) , creater_name = request.user)
        
        return render(request,'app/admin/admin_super.html',{'username':username,'supers':supers,'super_created':True})

        
    return render(request,'app/admin/admin_super.html',{'username':username,'supers':supers})






# delete super
def DeleteSuper(request,id):
    if not request.user.is_authenticated:
        return redirect('home')
    
    
    super = User.objects.filter(id=id).delete()

    username      = request.user.username
    supers =  User.objects.filter(is_super = True)
    
    context = {
                'username':username,
                'supers':supers,
                'super_delete':True,
                }

    return render(request,'app/admin/admin_super.html',context)


   

# update super's credit
def UpdateSuper(request,id):
    if not request.user.is_authenticated:
        return redirect('home')
    
    
    if request.method=='POST':
        username      = request.user.username
        # ''' NOTE : getting creds from form  '''
        super_credit   = request.POST['super_credit']

        # ''' NOTE : increase super's credit '''
        superseller  = User.objects.get(id=id)   
        superseller.credit += int(super_credit)
        superseller.save()

        # ''' NOTE : create history object'''
        super_history_obj = History.objects.create(  name = superseller.username , mode = "DEDUCT"   ,credit = int(super_credit) , creater_name = request.user)

        # ''' TODO : successfullly added and render data to templates '''
        supers =  User.objects.filter(is_super = True)
        
        return render(request,'app/admin/admin_super.html',{'username':username,'supers':supers,'credit_sent':True , 'reciever':superseller.username , 'credits':super_credit})

        
    superseller  = User.objects.filter(id=id)   
    super_detail = User.objects.get(id=id)   
    context = {
            'super':superseller,
            'victim':super_detail.username,
                }
    return render(request,'app/admin/super_update.html',context)


# update super's password
def UpdateSuperPassword(request,id):
    if not request.user.is_authenticated:
        return redirect('home')
    
    
    if request.method=='POST':
        username      = request.user.username
        # ''' NOTE : getting password from form  '''
        super_password   = request.POST['super_password']

        # ''' TODO : update password here '''
        superseller = User.objects.get(id=id)   
        superseller.set_password(super_password)
        superseller.super_pass = super_password
        superseller.save()

        # ''' TODO : successfullly added and render data to templates '''
        supers =  User.objects.filter(is_super = True)

        return render(request,'app/admin/admin_super.html',{'username':username,'supers':supers,'password_changed':True , 'victim':superseller.username , 'password':super_password})

    return redirect('home')
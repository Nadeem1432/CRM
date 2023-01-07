
from django.db import models
from datetime import datetime, timedelta , date , timezone
from django.contrib.auth.models import AbstractUser


class User(AbstractUser): #inherite here
    # ''' create here user types like seller , super and admin '''
    is_admin    =  models.BooleanField(default=False) #high
    is_super    =  models.BooleanField(default=False) #mid
    is_seller   =  models.BooleanField(default=False) #low
    credit      =  models.PositiveIntegerField(default=0)
    created_by  =  models.CharField( max_length=150 , null=True, blank=True )
    creator     =  models.ForeignKey('self', on_delete=models.CASCADE , null=True, blank=True)
    seller_pass =  models.CharField( max_length=150 , null=True, blank=True )
    super_pass  =  models.CharField( max_length=150 , null=True, blank=True )
    # created_at    = models.DateTimeField(auto_now_add=True)
    # updated_at    = models.DateTimeField(auto_now=True)
    

class Key(models.Model):
    customer_name = models.CharField(max_length=70)
    user_id       = models.CharField(max_length=70 , unique=True)
    version       = models.CharField(max_length=50)
    created_by    = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at    = models.DateTimeField(auto_now_add=True)
    expired_at    = models.DateTimeField(default=datetime.now()+timedelta(days=30))
    updated_at    = models.DateTimeField(auto_now=True)
    ip            = models.CharField(max_length=150 , default="None")
    pay_status    = models.BooleanField(default=False)
    is_login      = models.BooleanField(default=False)
    
    def validity(self):
        current_date  = datetime.now(timezone.utc)
        expiry_date   = self.expired_at
        calculation   = expiry_date -  current_date
        validity      = calculation.days
        return int(validity)
        

class History(models.Model):
    name         = models.CharField(max_length=70)
    user_id      = models.CharField(max_length=70 , null=True , blank=True)
    credit       = models.PositiveIntegerField(default=1)
    mode         = models.CharField(max_length=70 , default="DEDUCT")
    creater_name = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)


class Trns(models.Model):
    designation   = models.CharField(max_length=70)
    train_no      = models.PositiveIntegerField()
    gateway       = models.CharField(max_length=50)
    pnr_time      = models.DateTimeField(default=datetime.now()+timedelta(days=30))
    status        = models.BooleanField(default=True)
    created_by    = models.ForeignKey(User, on_delete=models.CASCADE, null=True , blank=True)

    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)




class Configuration(models.Model):
    message       = models.TextField()
    short_message = models.CharField(max_length=1024)
    news          = models.CharField(max_length=1024)
    app_version   = models.CharField(max_length=255)
    dll_version   = models.CharField(max_length=255)
    created_by    = models.ForeignKey(User, on_delete=models.CASCADE, null=True , blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)







# class Ip(models.Model):
#     user_id     = models.ForeignKey(Key, on_delete=models.CASCADE)
#     created_at  = models.DateTimeField(auto_now_add=True)
#     updated_at  = models.DateTimeField(auto_now=True)


    # def username(self):
    #     expiry_date   = self.expired_at
    #     calculation   = expiry_date -  current_date
    #     validity      = calculation.days
    #     return int(validity)

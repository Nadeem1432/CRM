from rest_framework import serializers
from app.models import User

class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class VerifySerializer(serializers.Serializer):
    key =  serializers.CharField(max_length = 50)
    # password =  serializers.CharField(max_length = 50)

    class Meta:
        fields = ['key']
        # fields = ['username' , 'password']


    


class Transactionializer(serializers.Serializer):
    key          =  serializers.CharField(max_length = 50)
    train_no     =  serializers.CharField(max_length = 100)
    destination  =  serializers.CharField(max_length = 150)
    payment_type =  serializers.CharField(max_length = 50)
    pnr_time     =  serializers.CharField(max_length = 100)
    trn_status   =  serializers.CharField(max_length = 50)
    
    # password =  serializers.CharField(max_length = 50)

    class Meta:
        fields = ['key' , 'train_no','destination' , 'payment_type' , 'pnr_time' , 'trn_status']

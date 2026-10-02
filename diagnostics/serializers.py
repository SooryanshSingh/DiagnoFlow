from rest_framework import serializers
from django.contrib.auth.models import User
from .models import DiagnosticCentre, DiagnosticTest, Booking, Payment

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user
class DiagnosticTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticTest
        fields = ('id', 'centre', 'name', 'description', 'price')
class DiagnosticCentreSerializer(serializers.ModelSerializer):
    tests = DiagnosticTestSerializer(many=True, read_only=True)

    class Meta:
        model = DiagnosticCentre
        fields = ('id', 'name', 'location', 'tests')

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('id', 'user', 'test', 'centre', 'appointment_datetime', 'amount', 'status', 'created_at')
        read_only_fields = ('id', 'user', 'amount', 'status', 'created_at')

    def create(self, validated_data):
        request = self.context.get('request')
        test = validated_data.get('test')
        
        validated_data['user'] = request.user
        validated_data['amount'] = test.price
        validated_data['status'] = 'PENDING'
        return super().create(validated_data)

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'booking', 'transaction_id', 'status', 'amount', 'created_at')
        read_only_fields = ('id', 'transaction_id', 'status', 'amount', 'created_at')
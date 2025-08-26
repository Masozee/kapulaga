from rest_framework import serializers
from .models import Guest, GuestDocument


class GuestDocumentSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    is_expired_status = serializers.SerializerMethodField()
    
    class Meta:
        model = GuestDocument
        fields = [
            'id', 'document_type', 'document_type_display', 'document_number',
            'issuing_country', 'issue_date', 'expiry_date', 'is_verified',
            'notes', 'created_at', 'updated_at', 'is_expired_status'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_is_expired_status(self, obj):
        """Get document expiration status"""
        return obj.is_expired()


class GuestSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    documents = GuestDocumentSerializer(many=True, read_only=True)
    loyalty_level = serializers.SerializerMethodField()
    total_stays = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    
    class Meta:
        model = Guest
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'date_of_birth', 'age', 'gender', 'gender_display', 'nationality',
            'address', 'postal_code', 'city', 'country', 'loyalty_points',
            'preferences', 'notes', 'is_vip', 'is_active', 'created_at',
            'updated_at', 'documents', 'loyalty_level', 'total_stays', 'total_spent'
        ]
        read_only_fields = ['created_at', 'updated_at', 'full_name', 'age']

    def get_loyalty_level(self, obj):
        """Get loyalty level based on points"""
        points = obj.loyalty_points
        if points >= 1000:
            return {"level": "Platinum", "color": "purple"}
        elif points >= 500:
            return {"level": "Gold", "color": "gold"}
        elif points >= 100:
            return {"level": "Silver", "color": "silver"}
        else:
            return {"level": "Bronze", "color": "brown"}

    def get_total_stays(self, obj):
        """Get total number of stays"""
        return obj.reservations.filter(status='CHECKED_OUT').count()

    def get_total_spent(self, obj):
        """Get total amount spent"""
        from django.db.models import Sum
        total = obj.reservations.filter(
            status='CHECKED_OUT',
            bill__status='PAID'
        ).aggregate(
            total=Sum('bill__total_amount')
        )['total']
        return float(total) if total else 0.0


class GuestListSerializer(serializers.ModelSerializer):
    """Simplified serializer for guest listings"""
    full_name = serializers.CharField(read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    loyalty_level = serializers.SerializerMethodField()
    
    class Meta:
        model = Guest
        fields = [
            'id', 'full_name', 'email', 'phone', 'nationality',
            'loyalty_points', 'is_vip', 'is_active', 'gender_display',
            'loyalty_level'
        ]

    def get_loyalty_level(self, obj):
        """Get loyalty level based on points"""
        points = obj.loyalty_points
        if points >= 1000:
            return "Platinum"
        elif points >= 500:
            return "Gold"
        elif points >= 100:
            return "Silver"
        else:
            return "Bronze"


class GuestCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating guests with documents"""
    documents = GuestDocumentSerializer(many=True, required=False)
    
    class Meta:
        model = Guest
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'date_of_birth',
            'gender', 'nationality', 'address', 'postal_code', 'city',
            'country', 'loyalty_points', 'preferences', 'notes', 'is_vip',
            'documents'
        ]

    def create(self, validated_data):
        documents_data = validated_data.pop('documents', [])
        guest = Guest.objects.create(**validated_data)
        
        for doc_data in documents_data:
            GuestDocument.objects.create(guest=guest, **doc_data)
        
        return guest

    def update(self, instance, validated_data):
        documents_data = validated_data.pop('documents', None)
        
        # Update guest fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update documents if provided
        if documents_data is not None:
            # Clear existing documents and create new ones
            instance.documents.all().delete()
            for doc_data in documents_data:
                GuestDocument.objects.create(guest=instance, **doc_data)
        
        return instance


class LoyaltyPointsSerializer(serializers.Serializer):
    """Serializer for loyalty points operations"""
    points = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(max_length=200, required=False, default="Manual adjustment")
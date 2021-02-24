from rest_framework import serializers
from .models import Family


class FamilySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Family
        fields = [
            "id",
            "email",
            "phone_number",
            "address",
            "preferred_comms",
        ]

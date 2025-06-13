from rest_framework import serializers
from .models import PatientExtraNote 

class PatientExtraNoteSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = PatientExtraNote

        fields = ['id', 'author', 'note_text', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']
from rest_framework import serializers
from .models import TextoRecebido

class TextoRecebidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextoRecebido
        fields = ['id', 'patient_id', 'conteudo', 'data_recebimento']
        read_only_fields = ['data_recebimento'] 
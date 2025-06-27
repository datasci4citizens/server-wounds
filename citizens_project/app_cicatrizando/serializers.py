from rest_framework import serializers
from .models import TextoRecebido, AtencaoImediataRegistro

class TextoRecebidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextoRecebido
        fields = ['id', 'patient_id', 'conteudo', 'data_recebimento']
        read_only_fields = ['data_recebimento'] 

class AtencaoImediataRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtencaoImediataRegistro
        fields = '__all__' # Inclui todos os campos do modelo
        read_only_fields = ['data_registro'] 
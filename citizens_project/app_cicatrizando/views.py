from rest_framework import viewsets
from .models import TextoRecebido, AtencaoImediataRegistro
from .serializers import TextoRecebidoSerializer, AtencaoImediataRegistroSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

@extend_schema(
    description="API para gerenciar textos recebidos, com limite de 2000 caracteres.",
    request=TextoRecebidoSerializer,
    responses={200: TextoRecebidoSerializer, 400: {"description": "Erro de validação"}},
    tags=['Textos'] # Agrupa na documentação
)
class TextoRecebidoViewSet(viewsets.ModelViewSet):
    queryset = TextoRecebido.objects.all()
    serializer_class = TextoRecebidoSerializer

    @extend_schema(
        summary="Lista todos os textos recebidos",
        description="Retorna uma lista paginada de todos os textos registrados.",
        parameters=[
            OpenApiParameter(name='search', type=str, description='Filtrar por conteúdo do texto', required=False)
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Cria um novo texto",
        examples=[
            OpenApiExample(
                'Exemplo de Criação',
                value={'conteudo': 'Este é um exemplo de texto que será salvo.'},
                request_only=True,
                media_type='application/json'
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
@extend_schema(
    description="API para registrar informações da tela de atenção imediata de feridas.",
    request=AtencaoImediataRegistroSerializer,
    responses={200: AtencaoImediataRegistroSerializer, 400: {"description": "Erro de validação"}},
    tags=['Atenção Imediata - Ferida'] # Agrupa na documentação
)
class AtencaoImediataRegistroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para listar, criar, recuperar, atualizar e deletar registros de Atenção Imediata.
    """
    queryset = AtencaoImediataRegistro.objects.all()
    serializer_class = AtencaoImediataRegistroSerializer

    @extend_schema(
        summary="Lista todos os registros de atenção imediata",
        description="Retorna uma lista de todos os registros de atenção imediata."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Cria um novo registro de atenção imediata",
        examples=[
            OpenApiExample(
                'Exemplo de Criação de Registro',
                value={
                    'patient_id': 1,
                    'wound_id': 101,
                    'aumento_tamanho': True,
                    'vermelha_inchada': False,
                    'saindo_pus_secrecao': True,
                    'doendo_mais': True,
                    'pele_quente': False,
                    'com_febre_mal': True,
                    'tempo_mudanca': '2-3_DIAS'
                },
                request_only=True,
                media_type='application/json'
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
from rest_framework import viewsets
from .models import TextoRecebido
from .serializers import TextoRecebidoSerializer
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
# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse

from .models import Images, Patients, Specialists, TrackingRecords, Wound, Comorbidities
from .serializers import (
    ImagesSerializer, PatientsSerializer, SpecialistsSerializer,
    TrackingRecordsSerializer, WoundSerializer, ComorbiditiesSerializer
)

# ====== IMAGES ======

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Images.objects.all()
    serializer_class = ImagesSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # GET /images
        return super().list(request)

    def create(self, request):
        # POST /images
        return super().create(request)

    def update(self, request, *args, **kwargs):
        # PUT /images
        return super().update(request, *args, **kwargs)

# ====== PATIENTS ======

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patients.objects.all()
    serializer_class = PatientsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['specialist_id']  # para GET /patients?specialist_id=...

    def list(self, request, *args, **kwargs):
        # GET /patients?specialist_id=...
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        # GET /patients/{id}
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        # PATCH /patients/{id}
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # DELETE /patients/{patient_id}
        return super().destroy(request, *args, **kwargs)

# ====== SPECIALISTS ======

class SpecialistViewSet(viewsets.ModelViewSet):
    queryset = Specialists.objects.all()
    serializer_class = SpecialistsSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        # GET /specialists/{id}
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # POST /specialists
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        # PATCH /specialists/{id}
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        # DELETE 
        return super().destroy(request, *args, **kwargs)


# ====== TRACKING RECORDS ======

class TrackingRecordViewSet(viewsets.ModelViewSet):
    queryset = TrackingRecords.objects.all()
    serializer_class = TrackingRecordsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['specialist_id', 'wounds_id']

    def list(self, request, *args, **kwargs):
        # GET /tracking-records?specialist_id=...&wounds_id=...
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        # GET /tracking-records/{id}
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['put'], url_path='archive')
    def archive(self, request, pk=None):
        # PUT /tracking-records/{id}/archive GET /wounds/excel

    # filtros/query params: patient_id

        #PATCH /wounds/{id} 
        tracking_record = self.get_object()
        tracking_record.is_active = False
        tracking_record.save()
        serializer = self.get_serializer(tracking_record)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # POST /tracking-records, incluindo upload de imagem embutido
        # Exemplo simples, você pode precisar ajustar para receber o arquivo de imagem junto
        return super().create(request, *args, **kwargs)

# ====== WOUNDS ======

class WoundViewSet(viewsets.ModelViewSet):
    queryset = Wound.objects.all()
    serializer_class = WoundSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['patient_id']

    def list(self, request, *args, **kwargs):
        # GET /wounds?patient_id=...
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        # GET /wounds/{id}
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        # PATCH /wounds/{id}
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['put'], url_path='archive')
    def archive(self, request, pk=None):
        # PUT /wounds/{id}/archive
        wound = self.get_object()
        wound.is_active = False
        wound.save()
        serializer = self.get_serializer(wound)
        return Response(serializer.data)

class WoundExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # GET /wounds/excel?patient_id=...
        patient_id = request.query_params.get('patient_id')
        # TODO: gerar o Excel dos ferimentos do paciente (lógica para exportar Excel)
        # Aqui só um stub exemplo:
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="wounds_patient_{patient_id}.xlsx"'
        # Gerar o conteúdo do excel e escrever na resposta
        # ...
        return response

class ComorbidityViewSet(viewsets.ModelViewSet):
    queryset = Comorbidities.objects.all()
    serializer_class = ComorbiditiesSerializer
    serialize_class = [IsAuthenticated]


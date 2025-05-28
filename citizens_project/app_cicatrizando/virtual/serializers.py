import traceback
from rest_framework import serializers
from rest_framework.utils.field_mapping import ClassLookupDict
from django.db import transaction

from .models import VirtualModel

field_mapping = ClassLookupDict(serializers.ModelSerializer.serializer_field_mapping)
class VirtualSerializerMetaclass(serializers.SerializerMetaclass):
    def __new__(cls, name, bases, attrs):
        if attrs.get("Meta", None) == None:
            return super().__new__(cls, name, bases, attrs)
        sm : VirtualModel = attrs["Meta"].super_model
        desc  = sm.descriptor()
        for virtual_field, field_bind in desc.fields.items():
            
            model  = field_bind.db_table_model(desc)
            model_field = model._meta.get_field(field_bind.db_field_name())
            field, kwargs = serializers.ModelSerializer() \
                .build_standard_field(field_bind.db_field_name(), model_field)
            if(issubclass(field, serializers.ModelField)):
                field = serializers.IntegerField
                kwargs = {
                    "read_only": kwargs.get("read_only"),
                    "allow_null": kwargs.get("allow_null")
                }
            if kwargs.get("validators", None):
                del kwargs["validators"]
            attrs[virtual_field] = field(**kwargs)
        return super().__new__(cls, name, bases, attrs)
    
class VirtualModelSerializer(serializers.Serializer, metaclass=VirtualSerializerMetaclass):

    @transaction.atomic()
    def create(self, validated_data):
        ModelClass : VirtualModel = self.Meta.super_model
        validated_data = ModelClass.create(validated_data)
        return validated_data

    def update(self, instance, validated_data):
        ModelClass : VirtualModel = self.Meta.super_model
        validated_data = ModelClass.update(validated_data)
        return ModelClass.get(**validated_data)
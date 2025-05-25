import traceback
from rest_framework import serializers
from rest_framework.utils.field_mapping import ClassLookupDict

from .models import VirtualModel

field_mapping = ClassLookupDict(serializers.ModelSerializer.serializer_field_mapping)
class VirtualSerializerMetaclass(serializers.SerializerMetaclass):
    def __new__(cls, name, bases, attrs):
        if attrs.get("Meta", None) == None:
            return super().__new__(cls, name, bases, attrs)
        sm = attrs["Meta"].super_model
        for super_field, inner_field in sm.source_fields().items():
            model_field = getattr(sm, inner_field[0]).table._meta.get_field(inner_field[1])
            field, kwargs = serializers.ModelSerializer().build_standard_field(inner_field[1], model_field)
            if(issubclass(field, serializers.ModelField)):
                field = serializers.IntegerField
                kwargs = {
                    "read_only": kwargs.get("read_only"),
                    "allow_null": kwargs.get("allow_null")
                }
            if kwargs.get("validators", None):
                del kwargs["validators"]
            print(field, kwargs)
            attrs[super_field] = field(**kwargs)
        return super().__new__(cls, name, bases, attrs)
    
class VirtualModelSerializer(serializers.Serializer, metaclass=VirtualSerializerMetaclass):
    def create(self, validated_data):
        ModelClass : VirtualModel = self.Meta.super_model
        
        for subtables in ModelClass.get_subtables():
            
            subtables.table._default_manager.create(
                **subtables.model_from_data(**validated_data)
            )
        return validated_data

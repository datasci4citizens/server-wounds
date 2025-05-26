# views.py
from django.db.models import OuterRef, Subquery
import django.db.models  as django_models
from django.db.models import QuerySet
from dataclasses import dataclass
from typing import Iterable, Optional, Union


def all_attr_ofclass(cls, classes : Union[tuple[type], type]):
	return {
		attr: getattr(cls, attr)
		for attr in dir(cls)
		if isinstance(getattr(cls, attr), classes)
	}
def add_annotate(last : QuerySet, table : django_models, target : str, filters : dict[str, object], source : str):
	return last.annotate(**{
		target: Subquery(table.objects.all().filter(**filters).values(source)[:1])
	})
@dataclass
class FieldBind:
	value : object
	const : bool = False
	key : bool = False



CID_HEIGHT = 1
CID_CENTIMETER = 2
CID_WEIGHT = 3
CID_KILOGRAM = 4
CID_SMOKE_FREQUENCY = 5
CID_SMOKE_FREQUENCY = 6
CID_DRINK_FREQUENCY = 7
CID_DRINK_FREQUENCY = 8

@dataclass
class FieldPath:
	table : str
	name : str
@dataclass
class VirtualFieldDescriptor:
	name : str 
	db_field_path : FieldPath
	def db_field_name(self):
		return self.db_field_path.name
	def db_table_name(self):
		return self.db_field_path.table
	def db_table_model(self, desc : "VirtualModelDescriptor"):
		return desc.bindings[self.db_field_path.table].table

@dataclass
class VirtualModelDescriptor:
	fields : dict[str, VirtualFieldDescriptor]
	main_row_name : str
	bindings : dict[str, "TableBinding"]
	source : "VirtualModel"
	def get_fieldbind(self, fieldpath : FieldPath):
		return self.bindings[fieldpath.table].fields[fieldpath.name]

	def debug_str(self, name):
		string = f"virtual {name}:\n" 
		max_len = max(map(lambda a: len(a), self.fields.keys()))
		for k, v in self.fields.items():
			path = f"{v.db_field_path.table}.{v.db_field_path.name}"
			string += "    " + f"{v.name:<{max_len}} <-- {path}" +"\n"
		for binding_name, binding in self.bindings.items():
			string += f"    bind {name}:\n" 
			max_len = max(map(lambda a: len(a), binding.fields.keys()))
			for k, v in binding.fields.items():
				connector = ""
				if(v.const):
					connector = "==="
				else:
					db_source_path = self.fields[v.value].db_field_path
					if(db_source_path.table == binding_name and db_source_path.name == k):
						connector = "<->"
					else:
						connector = "<--"
				begin = "  "
				if(v.key):
					begin = "* "
				string +=  "        "+ begin + f"{k:<{max_len}} {connector} {v.value}" +"\n"
			string += "\n"
		return string
@dataclass
class VirtualField:
	source : Optional[tuple[str, str]] = None

class TableBinding:
	table : django_models.Model
	fields : dict[str, FieldBind]
	def __init__(self, **kwargs : dict[str, FieldBind]):
		self.fields = kwargs
	def model_from_data(self , **kwargs):
		result = {}
		for concrete_field, field_bind in self.fields.items():
			if field_bind.const:
				result[concrete_field] = field_bind.value
				continue
			result[concrete_field] = kwargs.get(field_bind.value, None)
		return result
	
	def keys(self):
		return { k: v for k,v in self.fields.items() if v.key}
	
class VirtualModel:
	@classmethod
	def descriptor(cls) -> VirtualModelDescriptor:
		return VirtualModelDescriptor(
			main_row_name =  cls.main_row,
			bindings = cls._get_tablesbindings(),
			fields = cls.virtual_fields_descriptor(),
			source = cls 
		);
	@classmethod
	def _get_tablesbindings(cls) -> dict[str, TableBinding]:
		return { a : v 
		  for a, v in cls.__dict__.items()
		  if isinstance(v, TableBinding)
		}
	
	@classmethod
	def virtual_fields_descriptor(cls):
		bindings =  cls._get_tablesbindings()
		source_fields_tuples = [(av.value, FieldPath(row_name, a))
			for row_name, binding in bindings.items() 
			for a, av  in binding.fields.items()
			if not av.const
		]
		source_fields = {}
		for k, v in source_fields_tuples:
			if not source_fields.get(k, None):
				source_fields[k] = v
		virtual_fields = all_attr_ofclass(cls, VirtualField)
		for k, v in virtual_fields.items():
			source_fields[k] = FieldPath(v.source[0], v.source[1])
		return {
			name: VirtualFieldDescriptor(
				name = name, 
				db_field_path = field, 
			)
			for name, field in source_fields.items()
		}
	@staticmethod
	def annotate_field(last,  desc : "VirtualModelDescriptor",  virtual_field : VirtualFieldDescriptor):
		keys = desc.bindings[virtual_field.db_field_path.table].keys()
		field = desc.get_fieldbind(virtual_field.db_field_path)
		target = virtual_field.name
		filters = { 
			key_name: 
				bind.value if bind.const else OuterRef(key_name) 
			for key_name, bind in keys.items()
		}
		source = virtual_field.db_field_path.name
		return add_annotate(last, virtual_field.db_table_model(desc), target, filters, source)
	@classmethod
	def get_queryset(cls):
		desc = cls.descriptor()
		main_row = desc.bindings[desc.main_row_name]

		queryset = main_row.table.objects.all() 
		
		for virtual_field in desc.fields.values():
			queryset = cls.annotate_field(queryset, desc, virtual_field)
		queryset = queryset.values(*cls.virtual_fields_descriptor().keys())
		return queryset
		
	@classmethod
	def objects(self):
		return self.get_queryset()
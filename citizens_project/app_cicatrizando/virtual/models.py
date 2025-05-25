# views.py
from ..omop_models import Measurement, Observation, Person, Provider; 
from django.db.models import OuterRef, Subquery
from dataclasses import dataclass
from typing import Iterable, Optional


def attr_isinstaceof(cls, name, test_cls ):
	return isinstance(getattr(cls, name), test_cls)
def all_attr_ofclass(cls, classes):
	return {
		attr: getattr(cls, attr)
		for attr in dir(cls)
		if any([
			attr_isinstaceof(cls, attr, c)
			for c in classes 
		])
	}
def add_annotate(last, table, target, filters, source):
	return last.annotate(**{
		target: Subquery(table.objects.all().filter(**filters).values(source)[:1])
	})
@dataclass
class FieldBind:
	v : object
	const : bool = False
	key : bool = False

	def annotate(self, last, row, name, source):
		fields = all_attr_ofclass(row, [FieldBind])
		keys = { k: v for k,v in fields.items() if v.key}
		target = getattr(row, name).v
		filters = {n: v.v if v.const else OuterRef(source[v.v][1]) for n, v in keys.items()}
		source = name
		return add_annotate(last, row.table, target, filters, source)
	
	def __str__(self):
		s = "" 
		if self.key:
			s += "*"
		else:
			s += " "
		if self.const:
			s += "Const("
		else:
			s += "Bind("
		return s + self.v.__str__() +  ")"
class TableBinding:
	fields = {}
	def __init__(self, *args, **kwargs):
		fields = kwargs
	def __init__(self, **kwargs):
		for k, v in kwargs.items():
			setattr(self, k, v)
	def model_from_data(self, **kwargs):

		result = {}
		for concrete_field, field_bind in self.get_fields().items():
			if field_bind.const:
				result[concrete_field] = field_bind.v
				continue
			result[concrete_field] = kwargs.get(field_bind.v, None)
		return result
	def get_fields(self):
		return all_attr_ofclass(self, [FieldBind])
	
TableCreationOrder = [
	Provider, 
	Person,
	Measurement,
	Observation
]
class TableBindings:
	class Observation(TableBinding):
		table = Observation
	class Measurement(TableBinding):
		table = Measurement
	class Person(TableBinding):
		table = Person
	class Provider(TableBinding):
		table = Provider
CID_HEIGHT = 1
CID_CENTIMETER = 2
CID_WEIGHT = 3
CID_KILOGRAM = 4
CID_SMOKE_FREQUENCY = 5
CID_SMOKE_FREQUENCY = 6
CID_DRINK_FREQUENCY = 7
CID_DRINK_FREQUENCY = 8
@dataclass
class VirtualField:
	source : Optional[tuple[str, str]] = None


class VirtualModel:
	@classmethod
	def descriptor(cls):
		return {c:
			all_attr_ofclass(getattr(cls, c), [FieldBind])
			for c in cls.subtables_attr()
		};
	@classmethod
	def subtables_attr(cls):
		return filter(lambda a: isinstance(getattr(cls, a), TableBinding), dir(cls));
	@classmethod
	def get_subtables(cls) -> Iterable[TableBinding]:
		return map(lambda a : getattr(cls, a), cls.subtables_attr())
	
	@classmethod
	def source_fields(cls):
		api_descriptor = cls.descriptor()
		# print(*[str_attrs(c, getattr(Model, c), v) for c, v in api_descriptor.items()], sep = "\n")
		source_fields_tuples = [(av.v, (c, a))
			for c,v in api_descriptor.items() 
			for a, av  in v.items()
			if not av.const
		]
		source_fields = {}
		for k, v in source_fields_tuples:
			if not source_fields.get(k, None):
				source_fields[k] = v
		api_fields = all_attr_ofclass(cls, [VirtualField])
		for k, v in api_fields.items():
			source_fields[k] = v.source
		return source_fields
	@classmethod
	def get_queryset(cls):
		main_row = getattr(cls, cls.main_row)
		queryset = main_row.table.objects.all() 
		for k, v in cls.source_fields().items():
			field = getattr(getattr(cls, v[0]), v[1])
			queryset = field.annotate(queryset, getattr(cls, v[0]), v[1], cls.source_fields())
		queryset = queryset.values(*cls.source_fields().keys())
		return queryset
		
	@classmethod
	def objects(self):
		return self.get_queryset()
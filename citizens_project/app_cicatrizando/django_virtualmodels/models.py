"""Esse modulo define modelos virtuais, que são modelos que servem como interface para linhas em outros modelos 
Esse modulo possui 4 conceitos principais:
- Modelo virtual
- Campo virtual
- linha/Binding de tabela
- Binding de Campo fisico 

Os modelos virtuais basicamente gerenciam Leitura, Criação e Modificação de dados em outros modelos 

Os campos virtuais são os campos visiveis na interface publica dos modelos virtuais, onde o usuario do modelo virtual ira passar as informações e receber lendo os campos virtuais

As linhas ou bindings com tabela, definem linhas em outros modelos que estão conectados ao modelo virtual, onde a cada vez que é adicionado ao modelo virtual, para cada uma das bindings é criado também uma linha nas respectivas tabelas, e quando é feito leitura, os dados são obtidos a partir dos bindings 

Os bindings de campos fisicos são como o campo fisico devem ser tratados na manipulação das linhas, alguns são constantes então sempre para a respectiva binding é preenchida com mesmo valor, e outros conectam com campos virtuais.

A conexão entre campo fisico e campo virtual pode ser bidirecional: escreve do campo virtual para o fisico, e o virtual é lido do a partir do fisico, quanto unidirecional: apenas é escrito do campo virtual para o fisico, nunca lido. Forma unidirecional se dá principalmente em chaves, que aparecem em mutiplas tabelas, mas só é nescessario ler de uma unica. 
"""
# views.py
from django.db.models import OuterRef, Subquery
import django.db.models  as django_models
from django.db.models import QuerySet
from dataclasses import dataclass
from typing import Iterable, Optional, TypeVar, Union
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Case, Value, When, F

T = TypeVar("T")
def all_attr_ofclass(cls, classes : Union[tuple, type[T]]) -> dict[str, T]:
	return {
		attr: getattr(cls, attr)
		for attr in dir(cls)
		if isinstance(getattr(cls, attr), classes)
	}

@dataclass
class ChoiceMap[T, U]:
	choices : list[tuple[T, U]]
	def virtual_to_db(self, virtual_value : T):
		for virtual, db in self.choices:
			if virtual == virtual_value:
				return db 
	def db_to_virtual(self, db_value : U):
		for virtual, db in self.choices:
			if db == db_value:
				return virtual
	def django_case(self, field_name):
		whens = []
		for virtual_value, db_value in self.choices:
			whens.append(When(**{field_name: db_value, "then": Value(virtual_value)}))
		return Case(*whens)
	def virtual_values(self):
		return list(map(lambda choice: choice[0], self.choices))
	def db_values(self):
		return list(map(lambda choice: choice[1], self.choices))

@dataclass
class FieldBind:
	"""Um bind para um valor, onde o valor pode ser contante sempre o mesmo ou uma string para o campo virtual que deve ser conectado"""
	
	value : object 
	"""O valor do bind do campo, poder ser um valor contante ou uma string do nome do campo virtual a se conectar"""
	
	const : bool = False
	"""Flag indicando se o bind é um valor contante, onde todas a coluna em todas as linhas do bind deve ter o mesmo valor"""
	
	key : bool = False
	"""Flag indicando que bind é uma chave primaria do bind, ou seja, deve ser oferecida quando for feito uma busca para conseguir encontrar a linha correspondente"""

@dataclass
class FieldPath:
	"""Um identificador de um campo, onde table indica o nome do TableBinding do modelo virtual, e name indica o nome do campo no TableBinding """
	
	table : str
	"""Nome da tabela onde o campo deve estar"""
	
	name : str
	"""Nome do campo no TableBinding"""
@dataclass
class VirtualFieldDescriptor:
	"""Descreve as informações de um campo virtual"""

	name : str 
	"""O nome do campo virtual, ele serve como identificador do campo virtual"""

	key : bool
	"""Flag indicando se o campo virtual é faz parte da chave primaria ou não"""
	null : bool
	choicemap : Optional[ChoiceMap] 
	db_field_path : FieldPath
	"""Caminho para o campo fisico de onde deve ser feito leitura de informações
	Um campo virtual pode definir valores de muitos campos fisicos em linhas filhas, porém é nescessario uma tabela de onde se deve obter o valor na leitura.
	"""

	def db_field_name(self):
		"""Retorna o nome do campo no banco de dados de onde se deve ler o campo virtual"""
		return self.db_field_path.name
	def db_table_name(self):
		"""Retorna o nome do TableBinding de onde se deve ler o campo"""
		return self.db_field_path.table
	def db_table_model(self, desc : "VirtualModelDescriptor"):
		"""Retorna o Model do django que está atrelado o modelo fisico de onde deve ser feito a leitura do campo"""
		return desc.bindings[self.db_field_path.table].table
	def validate(self, value) -> str:
		if not self.null and value == None:
			return "Campo não pode ser nulo"
		if self.choicemap != None and value not in  self.choicemap.virtual_values():
			return f"Campos não é uma escolha valida entre as opções [{", ".join(self.choicemap.virtual_values())}]"
		return None
@dataclass
class VirtualModelDescriptor:
	"""Descreve as informações de um modelo virtual"""

	fields : dict[str, VirtualFieldDescriptor]
	"""Dicionario de campos virtuais, a chave é o nome que identifica o campo o valor é um descriptor que detalha informações do campo"""
	main_row_name : str
	"""Principal binding do modelo virtual, é a binding onde deve contar a chave primaria do modelo virtual"""
	bindings : dict[str, "TableBinding"]
	"""Dicionario dos bidings, a chave é o nome que identifica o binding e o valor é o binding com as informações de como ele deve ser."""
	source : type["VirtualModel"]
	"""Modelo fonte do descriptor"""

	def get_fieldbind(self, fieldpath : FieldPath):
		"""A partir do caminho para um campo num binding, retorna o FieldBind do repesctivo campo """
		return self.bindings[fieldpath.table].fields[fieldpath.name]


	def keys(self):
		"""retorna um dicionario dos campos pertencentes a chave primaria do modelo virtual, onde o a chave é o nome do campo, e o valor é o descriptor do campo virtual"""
		return { k: v for k,v in self.fields.items() if v.key}
	
	def debug_str(self):
		string = f"virtual {self.source.__name__}:\n" 
		max_len = max(map(lambda a: len(a), self.fields.keys()))
		for k, v in self.fields.items():
			path = f"VirtualField(source=(\"{v.db_field_path.table}\", \"{v.db_field_path.name}\"))"
			string += "    " + f"{v.name:<{max_len}} = {path}" +"\n"
		for binding_name, binding in self.bindings.items():
			string += f"    bind {binding_name}:\n" 
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
	"""Define um campo virtual"""
	source : Optional[tuple[str, str]] = None
	"""Indica o caminho para campo em um dos bindings que deve ser usado de fonte da informação quando é feito leitura do campo, o primeiro valor é o nome do binding e o segundo valor é o nome do campo fisico no binding"""
	key : bool = False
	"""Indica se o campo virtual faz parte da chave do modelo virtual"""
	null : bool =  False
	choicemap : Optional[ChoiceMap] = None

class TableBinding:
	"""Define uma binding entre um modelo virtual e uma linha em uma tabela"""
	table : django_models.Model
	"""Modelo fisico que em que o binding se conecta"""
	fields : dict[str, FieldBind]
	"""Dicionario de bindings dos campos, onde a chave é o nome que identifica a coluna no modelo fisico, e o valor é as informações para fazer essa conexão"""
	def __init__(self, **kwargs : dict[str, FieldBind]):
		self.fields = kwargs
	def model_from_data(self , **kwargs):
		"""A partir de um dicinario de dados do modelo virtual, onde cada chave é o nome que identifica um campo virtual e o valor é o valor que deve ser guardado no banco de dados para o respectivo campo, retorna um dicionario onde as chaves são os nomes dos campos fisicos para o respectivo binding, e o valor são o valor que deve estar no banco para o respectivo campo"""
		result = {}
		for concrete_field, field_bind in self.fields.items():
			if field_bind.const:
				result[concrete_field] = field_bind.value
				continue
			result[concrete_field] = kwargs.get(field_bind.value, None)
		return result
	def model_to_data(self ,data, model : django_models.Model):
		for concrete_field, field_bind in self.fields.items():
			if field_bind.const:
				continue
			data[field_bind.value] = getattr(model, concrete_field)

	def row_data_from(self, virtual_data) -> django_models.Model:
		"""A partir dos dados do modelo virtual, retorna o Modelo fisico do binding que está no momento armazenado no banco de dados"""
		pk = {
			k: v.value if v.const else virtual_data[v.value]
			for k, v in self.keys().items()
		}
		return self.table.objects.get(**pk)
	def keys(self):
		"""Retorna dicionario dos campos que fazem parte da chave primaria"""
		return { k: v for k,v in self.fields.items() if v.key}
	def updatable_fields(self) -> list[str]: 
		"""Retorna lista dos nomes que indetificam os campos do binding que são modificaveis"""
		return [f.value for f in self.fields.values() if not f.const and not f.key]
class VirtualModel:
	"""Indica um modelo virtual, onde possui seus campos virtuais que apenas definem uma interface de como os dados devem ser recebidos e retornados, e bindings, que definem como deve ser guardado os campos virtuais, em modelos fisicos, onde cada binding indica uma linha que deve ser conectada a um outro modelo, que quando é criado é criado junto, e editado é editado junto, e é usado de fonte de dados"""
	@classmethod
	def descriptor(cls) -> VirtualModelDescriptor:
		"""Retorna um descritor de como é o modelo virtual
		descritor existe para que seja possivel customizar como os campos e bindings são definidos apenas modificando esta função"""
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
		"""Retorna os valores de quais são os campos virtuais, obtem a partir dos campos definidos no corpo do VirtualModel, e também caso algum FieldBind defina que faz binding com um campo e o campo não estiver definido no corpo, então aqui é criado o campo virtual"""
		bindings =  cls._get_tablesbindings()
		source_fields_tuples = [
			VirtualFieldDescriptor(
				name = av.value,
				db_field_path = FieldPath(row_name, a),
				key = False, 
				null= False,
				choicemap=None
			)
			for row_name, binding in bindings.items() 
			for a, av  in binding.fields.items()
			if not av.const
		]
		source_fields = {}
		for field in source_fields_tuples:
			if not source_fields.get(field.name, None):
				source_fields[field.name] = field
		virtual_fields = all_attr_ofclass(cls, VirtualField)
		for k, v in virtual_fields.items():
			source_fields[k] = VirtualFieldDescriptor(
				name  = k, 
				db_field_path = FieldPath(v.source[0], v.source[1]),
				key = v.key,
				null = v.null,
				choicemap=v.choicemap
			)
		return source_fields
	@staticmethod
	def annotate_field(last,  desc : "VirtualModelDescriptor",  virtual_field : VirtualFieldDescriptor):
		"""adiciona uma coluna a um queryset, indicando a fonte do campo virtual. Em resumo faz o join com o modelo do binding"""
		keys = desc.bindings[virtual_field.db_field_path.table].keys()
		field = desc.get_fieldbind(virtual_field.db_field_path)
		target = virtual_field.name
		filters = { 
			key_name: 
				bind.value if bind.const else OuterRef(desc.fields[bind.value].db_field_name()) 
			for key_name, bind in keys.items()
		}
		source = virtual_field.db_field_path.name
		table = virtual_field.db_table_model(desc)
		subqueryset = table.objects.all().filter(**filters).values(source)[:1]
		subquery = Subquery(subqueryset)
		value = subquery
		if virtual_field.choicemap != None:
			
			value = Subquery(table.objects.all()
				.filter(**filters)
				.annotate(**{"___mapped": virtual_field.choicemap.django_case(source)})
				.values("___mapped")[:1]
			)
			

		return last.annotate(**{
			target: value  
		})
	@classmethod
	def get_queryset(cls):
		"""Cria um queryset, do modelo virtual, que descreve como deve ser feita a leitura dos campos virtuais no banco de dados"""
		desc = cls.descriptor()
		main_row = desc.bindings[desc.main_row_name]

		queryset = main_row.table.objects.all() 
		
		for virtual_field in desc.fields.values():
			queryset = cls.annotate_field(queryset, desc, virtual_field)
		queryset = queryset.values(*cls.virtual_fields_descriptor().keys())
		return queryset
	@classmethod
	def get(cls, **pk):
		"""A partir da chave primaria de um modelo virtual, retorna o valor do respectivo objeto"""
		pk = {
			k : pk[k]
			for k, v in cls.descriptor().keys().items()
		}
		return cls.get_queryset().get(**pk)
	@classmethod
	def objects(self):
		"""retorna o queryset do modelo virtual, esse metodo existe para a interface publica da classe se assemelhar a de um django model"""
		return self.get_queryset()
	@classmethod
	def _map_virtual_to_db(cls, data):
		result = {**data}
		for field_name, field_desc in cls.descriptor().fields.items():
			if field_desc.choicemap is not None:
				result[field_name]  = field_desc.choicemap.virtual_to_db(result[field_name])
		return result
	@classmethod
	def _map_db_to_virtual(cls, data):
		result = {**data}
		for field_name, field_desc in cls.descriptor().fields.items():
			if field_desc.choicemap is not None:
				result[field_name]  = field_desc.choicemap.db_to_virtual(result[field_name])
		return result
	@classmethod
	@transaction.atomic()
	def create(cls, data):
		result = {**cls._map_virtual_to_db(data)}
		"""Adiciona a informação dos dados do modelo virtual no banco de dados, é usado transactions, então caso aconteça alguma falha na criação é acontece rollback e não é feita a criação incompleta"""
		for subtables in cls.descriptor().bindings.values():
			model_data = subtables.table._default_manager.create(
				**subtables.model_from_data(**result)
			)
			subtables.model_to_data(result, model_data)
		return cls._map_db_to_virtual(result)

	@classmethod
	@transaction.atomic()
	def update(cls,data: dict[str, object]):
		"""A partir do dicionario de dados, onde a chave é o nome do campo virtual que deve ser modificado, e o valor é o novo valor, é editado cada um dos respectivos valores
		atomic: A operação é atomica então caso aconteça algum erro não é feito a modificação em partes"""
		actual = None
		for k, subtable in cls.descriptor().bindings.items():
			updatable_fields =	subtable.updatable_fields()
			if not any(x for x in updatable_fields if x in set(data.keys())):
				continue
			try:
				instance = subtable.row_data_from(data)
				for db_field, v in subtable.fields.items():
					if v.value in data.keys():
						value = v.value if v.const else data[v.value]
						setattr(instance, db_field, value)
				instance.save(force_update=True)
			except ObjectDoesNotExist:
				if(actual == None):
					actual = cls.get(**data)
					for field in cls.descriptor().fields.keys():
						if field in data:
							actual[field] = data[field]

				subtable.table._default_manager.create(
					**subtable.model_from_data(**actual)
				)
			subtable.model_from_data(**data)
		return cls._map_db_to_virtual(data)
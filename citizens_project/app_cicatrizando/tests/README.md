# Como rodar os testes do app_cicatrizando

## Pré-requisitos
- Python 3.12+
- Django e dependências do projeto instaladas (veja `requirements.txt`)
- Banco de dados SQLite (default) ou configurado no settings

## Comando principal
Execute na raiz do projeto (onde está o `manage.py`):

```
python manage.py test app_cicatrizando.tests -v 2
```

- O comando acima executa todos os testes automatizados do app.
- O parâmetro `-v 2` mostra mais detalhes dos testes.

## Rodar um teste específico

Para rodar apenas um teste (por exemplo, PatientAPITest):
- python manage.py test app_cicatrizando.tests.PatientAPITest
"""
Este arquivo define um gancho de pós-processamento personalizado para um gerador de documentação de API (por exemplo, OpenAPI/Swagger).

Ele organiza os endpoints da API em grupos lógicos de tags com base em seus caminhos de URL.
Especificamente, ele identifica os principais segmentos de caminho (por exemplo, 'virtual', 'omop')
e agrupa tags de API relacionadas a eles, melhorando a legibilidade e a navegação
da documentação de API gerada.
"""



import re

def _tokenize_path(path):
    path = re.sub(pattern=r'\{[\w\-]+\}', repl='', string=path)
    # cleanup and tokenize remaining parts.
    tokenized_path = path.rstrip('/').lstrip('/').split('/')
    return [t for t in tokenized_path if t]

def custom_postprocessing_hook(result, generator, request, public):
    groups = ["virtual","omop" ]
    tag_groups = {}
    tag_groups["default"] = []
    tag_groups.update({ g : [] for g in groups})
    paths = {
        tuple(_tokenize_path(p))
        for p in result["paths"].keys()
    }
    for tokens in paths:
        values = tag_groups.get(tokens[0], None)
        if values != None:
            tag_groups[tokens[0]].append(tokens[1])
        else:
            tag_groups['default'].append(tokens[0])

    result["x-tagGroups"] = [ 
        {
            "name": k, 
            "tags": list(set(v))
        } 
        for k , v in tag_groups.items()
    ]
    return result

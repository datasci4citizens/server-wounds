"""
Esta visualização do Django renderiza uma página interativa de documentação da API usando a ferramenta Scalar API Reference.

Ela configura as URLs necessárias (por exemplo, esquema OpenAPI, biblioteca Scalar JavaScript)
e as passa para o modelo 'scalar/scalar.html' para exibição.
Isso permite que os usuários explorem os endpoints, modelos e operações da API diretamente no navegador.
"""



from django.template.response import TemplateResponse
def scalar_viewer(request):
    openapi_url = "/api/schema/"
    title = "Scalar Api Reference"
    scalar_js_url = "https://cdn.jsdelivr.net/npm/@scalar/api-reference"
    scalar_proxy_url = ""
    scalar_favicon_url = "/static/favicon.ico"
    context = {
        "openapi_url": openapi_url,
        "title": title,
        "scalar_js_url": scalar_js_url,
        "scalar_proxy_url": scalar_proxy_url,
        "scalar_favicon_url": scalar_favicon_url,
    }
    return TemplateResponse(request, "scalar/scalar.html", context)

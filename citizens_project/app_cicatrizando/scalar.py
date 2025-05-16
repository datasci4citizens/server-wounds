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

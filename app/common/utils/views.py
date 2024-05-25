class ViewsUtils:
    @classmethod
    def is_htmx_enabled(cls, request) -> bool:
        return request.headers.get("Hx-Request") == "true"

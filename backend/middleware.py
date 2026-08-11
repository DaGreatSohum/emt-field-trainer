class SecurityHeadersMiddleware:
    """Small defense-in-depth header set for the browser training surface."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors "
            "'none'; form-action 'self'; script-src 'self'; style-src 'self'; font-src 'self'; "
            "img-src 'self' data:; connect-src 'self'",
        )
        response.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.setdefault("Cross-Origin-Resource-Policy", "same-site")
        response.setdefault("X-Permitted-Cross-Domain-Policies", "none")
        return response

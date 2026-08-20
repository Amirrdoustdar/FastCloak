from fastapi import APIRouter, Request, HTTPException
from app.services.proxy_service import ProxyService

router = APIRouter(tags=["Proxy"])
proxy_service = ProxyService()


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
)
async def proxy(request: Request, path: str):
    """Proxy requests to upstream with user headers injected"""
    
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = request.state.user
    
    extra_headers = {
        "X-Auth-User": user.email,
        "X-Auth-User-Name": user.name or "",
        "X-Auth-Provider": user.provider,
        "X-Auth-Roles": ",".join(user.roles),
        "X-Auth-Groups": ",".join(user.groups),
    }
    
    return await proxy_service.forward_request(request, path, extra_headers)
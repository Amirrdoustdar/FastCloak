import httpx
from fastapi import Request, Response
from app.config import settings
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class ProxyService:
    """HTTP Reverse Proxy"""
    
    def __init__(self):
        self.upstream_url = settings.UPSTREAM_URL
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
    
    async def forward_request(
        self,
        request: Request,
        path: str,
        extra_headers: Dict[str, str] = None,
    ) -> Response:
        """Forward request to upstream"""
        
        target_url = f"{self.upstream_url}/{path}"
        query_string = request.url.query
        if query_string:
            target_url = f"{target_url}?{query_string}"
        
        body = await request.body()
        
        # Filter headers
        headers = dict(request.headers)
        hop_by_hop = {
            "host", "connection", "keep-alive",
            "transfer-encoding", "te", "trailer",
            "proxy-authorization", "proxy-authenticate",
            "upgrade",
        }
        headers = {k: v for k, v in headers.items() if k.lower() not in hop_by_hop}
        headers["host"] = self.upstream_url.split("//")[-1]
        
        if extra_headers:
            headers.update(extra_headers)
        
        try:
            response = await self.client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
            )
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type"),
            )
            
        except httpx.ConnectError:
            logger.error(f"Cannot connect to upstream: {self.upstream_url}")
            return Response(content=b"Upstream unavailable", status_code=502)
        except httpx.TimeoutException:
            logger.error("Upstream timeout")
            return Response(content=b"Gateway timeout", status_code=504)
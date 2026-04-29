from fastapi import Header, HTTPException


async def get_active_client(x_client_id: str = Header(None)):
    if not x_client_id:
        raise HTTPException(
            status_code=403,
            detail="Falta Identidad Soberana (X-Client-ID)"
        )
    return x_client_id

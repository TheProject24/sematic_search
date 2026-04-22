import jwt
from fastapi import HTTPException, Header
from app.core.config import settings

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    
    token = authorization.replace("Bearer ", "")
    
    # --- Attempt 1: HS256 (Supabase Default) ---
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={
                "verify_aud": False,
                "verify_iat": False,
                "verify_exp": True # We should verify expiration
            }
        )
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except (jwt.DecodeError, jwt.InvalidAlgorithmError):
        # If HS256 fails, it might be an RS256 token from an external provider/JWKS
        pass

    # --- Attempt 2: RS256 (Supabase JWKS) ---
    try:
        SUPABASE_JWKS_URL = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/jwks"
        jwks_client = jwt.PyJWKClient(SUPABASE_JWKS_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256"],
            options={
                "verify_aud": False,
                "verify_iss": False,
                "verify_exp": True
            }
        )
        return payload.get("sub")

    except Exception as e:
        # Fallback for debugging
        print(f"DEBUG AUTH ERROR: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication Failed")
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings

# This tells FastAPI to look for the Authorization header
bearer_scheme = HTTPBearer()

# Fetch and cache the JSON Web Key Set from Clerk
jwks_url = f"{settings.CLERK_ISSUER_URL}/.well-known/jwks.json"
jwks_client = PyJWKClient(jwks_url)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    """
    Validates the Clerk JWT and returns the user's Clerk ID.
    Inject this dependency into any protected FastAPI route.
    """
    token = credentials.credentials

    try:
        # Dynamically fetch the signing key based on the token's header
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Decode and validate the token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.CLERK_ISSUER_URL,
            options={"verify_audience": False} # Set to True if you configure audiences in Clerk
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing subject (user_id)"
            )
            
        return user_id

    except jwt.PyJWKClientError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unable to fetch Clerk signing keys"
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Invalid token: {str(e)}"
        )
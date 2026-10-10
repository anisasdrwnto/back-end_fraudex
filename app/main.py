from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.limiter import limiter
from app.routers import auth

app = FastAPI(title="Fraudex API")
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    # format {"detail": ...} supaya frontend bisa menampilkan pesannya
    return JSONResponse(
        status_code=429,
        content={"detail": "Terlalu banyak percobaan. Coba lagi sebentar lagi."},
    )


# Ditambahkan paling akhir = lapisan terluar, supaya respons error (termasuk 429)
# tetap membawa header CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    # URL preview Vercel berubah-ubah, jadi pakai pola
    allow_origin_regex=r"https://front-end-fraudex.*\.vercel\.app",
    allow_credentials=False,  # token dikirim lewat header Authorization, bukan cookie
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(auth.router)
app.include_router(api_v1)


@app.get("/health")
def health():
    return {"status": "ok"}
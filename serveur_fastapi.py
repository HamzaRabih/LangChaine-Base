"""Le même serveur MCP, monté DANS une application FastAPI.

Utile quand on a déjà une API REST : une seule application expose à la fois
des routes classiques (pour un front, un autre service…) et un endpoint MCP
(pour les agents). Les tools restent définis une seule fois, dans serveur_mcp.py.

Lancement :
    uv run uvicorn serveur_fastapi:app --port 8002
    -> REST : http://127.0.0.1:8002/sante    MCP : http://127.0.0.1:8002/mcp
"""
import contextlib

from fastapi import FastAPI

from serveur_mcp import STOCK, mcp

# Le transport HTTP de MCP a besoin d'un « session manager » démarré avec l'application.
@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    async with mcp.session_manager.run():
        yield

app = FastAPI(title="Boutique : REST + MCP", lifespan=lifespan)


@app.get("/sante")
def sante() -> dict:
    """Route REST classique, sans rapport avec MCP."""
    return {"statut": "ok", "articles": len(STOCK)}


# streamable_http_app() sert déjà sur /mcp : on le monte à la racine.
app.mount("/", mcp.streamable_http_app())

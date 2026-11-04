"""Serveur MCP minimal avec FastMCP (SDK officiel `mcp`).

FastMCP transforme de simples fonctions Python en :
- tools     : actions que le LLM peut appeler          -> @mcp.tool()
- resources : données en lecture, adressées par une URI -> @mcp.resource("uri")
- prompts   : modèles de prompt réutilisables           -> @mcp.prompt()

Le nom, la docstring et les annotations de type de chaque fonction deviennent
le schéma JSON que le client (et donc le LLM) reçoit : ils doivent être clairs.

Lancement :
    uv run serveur_mcp.py                 # HTTP « streamable », http://127.0.0.1:8001/mcp
    uv run serveur_mcp.py --stdio         # stdio : le client lance lui-même le process
"""
import sys

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("boutique", host="127.0.0.1", port=8001, log_level="WARNING")

# Fausse base de données : le sujet ici est MCP, pas SQL.
STOCK = {"BALLON01": 42, "MAILLOT02": 0, "GOURDE03": 7}
PRIX = {"BALLON01": 19.9, "MAILLOT02": 35.0, "GOURDE03": 8.5}


@mcp.tool()
def consulter_stock(reference: str) -> int:
    """Renvoie la quantité en stock d'un article à partir de sa référence (ex. BALLON01)."""
    if reference not in STOCK:
        raise ValueError(f"Référence inconnue : {reference}")
    return STOCK[reference]


@mcp.tool()
def calculer_devis(reference: str, quantite: int) -> dict:
    """Calcule le montant HT d'un devis pour un article et une quantité."""
    if reference not in PRIX:
        raise ValueError(f"Référence inconnue : {reference}")
    return {"reference": reference, "quantite": quantite,
            "prix_unitaire": PRIX[reference], "total_ht": round(PRIX[reference] * quantite, 2)}


@mcp.resource("catalogue://articles")
def catalogue() -> str:
    """Liste des références disponibles."""
    return "\n".join(f"{ref} : {prix} €" for ref, prix in PRIX.items())


@mcp.prompt()
def redaction_relance(client: str) -> str:
    """Prompt réutilisable : relance commerciale polie."""
    return f"Rédige un court e-mail de relance commerciale, poli et professionnel, pour le client {client}."


if __name__ == "__main__":
    mcp.run(transport="stdio" if "--stdio" in sys.argv else "streamable-http")

"""
Mistral AI Service — Structured risk report generation
======================================================
Direct port of `backend/services/mistral.service.ts`.

Builds a structured prompt from the risk assessment data and expert
form fields, then calls the Mistral Chat Completions API requesting
a deterministic JSON output.

Falls back to a deterministic report if the API key is not configured.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from core.config import settings

CLIENT_TIMEOUT = 30.0


def _niveau_label(global_score: int) -> str:
    if global_score >= 70:
        return "critique"
    if global_score >= 50:
        return "eleve"
    if global_score >= 30:
        return "modere"
    return "faible"


def _niveau_label_fr(global_score: int) -> str:
    labels = {"faible": "faible", "modere": "modéré", "eleve": "élevé", "critique": "critique"}
    return labels.get(_niveau_label(global_score), "modéré")


def _build_fallback_report(
    scores: dict[str, int],
    address_label: str,
) -> dict[str, Any]:
    niveau = _niveau_label(scores.get("global_score", 0))
    niveau_fr = _niveau_label_fr(scores.get("global_score", 0))

    inondation = scores.get("inondation", 0)
    rga = scores.get("rga", 0)
    tempete = scores.get("tempete", 0)
    incendie = scores.get("incendie", 0)
    seisme = scores.get("seisme", 0)
    global_score = scores.get("global_score", 0)

    return {
        "niveauRisque": niveau,
        "resume": (
            f"Le bien situé à {address_label} présente un profil de risque {niveau_fr} "
            f"avec un score global de {global_score}/100. L'analyse couvre 5 périls "
            f"principaux: inondation ({inondation}), RGA ({rga}), tempête ({tempete}), "
            f"incendie ({incendie}) et séisme ({seisme})."
        ),
        "pointsVigilance": [
            f"Risque inondation {'élevé' if inondation >= 50 else 'maîtrisé'} "
            f"({inondation}/100)",
            f"Exposition aux argiles {'significative' if rga >= 40 else 'modérée'} "
            f"({rga}/100)",
            f"Vulnérabilité tempête {'notable' if tempete >= 40 else 'correcte'} "
            f"({tempete}/100)",
        ],
        "recommandations": [
            {
                "priorite": "haute",
                "action": "Vérification de l'état de la toiture et de l'étanchéité",
                "impact": "Réduction du risque tempête de 15 à 20%",
            },
            {
                "priorite": "moyenne",
                "action": "Installation d'un clapet anti-retour sur les canalisations",
                "impact": "Réduction du risque inondation de 10%",
            },
            {
                "priorite": "faible",
                "action": "Réalisation d'un diagnostic des fondations",
                "impact": "Meilleure évaluation du risque RGA",
            },
        ],
        "syntheseTexte": (
            f"Ce bien immobilier présente un profil de risque {niveau_fr} selon notre "
            f"analyse multi-périls. Le score composite de {global_score}/100 a été calculé "
            f"à partir de données issues de Géorisques, de la BDNB et du formulaire "
            f"déclaratif expert. Les principaux facteurs de risque identifiés sont "
            f"l'exposition au risque inondation (score {inondation}/100), au "
            f"retrait-gonflement des argiles (score {rga}/100) et aux tempêtes "
            f"(score {tempete}/100). Ce profil justifie une attention particulière "
            f"lors de la souscription et potentiellement l'application de clauses "
            f"spécifiques ou de franchises modulées. Note: rapport généré en mode "
            f"dégradé (clé API Mistral non configurée)."
        ),
        "scoreJustification": (
            f"Score de {global_score}/100 calculé selon la pondération réglementaire: "
            f"inondation 30% + RGA 25% + tempête 20% + incendie 15% + séisme 10%."
        ),
    }


class MistralService:
    """Generate structured risk reports using Mistral AI."""

    SYSTEM_PROMPT = (
        "Tu es un expert en évaluation de risques immobiliers pour une compagnie "
        "d'assurance française. Tu analyses des données structurées (BDNB, Géorisques, "
        "formulaire expert) et génères un rapport de risque structuré. Tu réponds "
        "UNIQUEMENT en JSON valide, sans markdown, sans backticks, sans texte avant "
        "ou après le JSON. La langue est le français. Sois précis, concis et professionnel."
    )

    @staticmethod
    def _build_user_prompt(
        address_label: str,
        building_data: dict | None,
        risks_data: dict | None,
        expert_fields: dict[str, str],
        scores: dict[str, int],
    ) -> str:
        building = building_data or {}
        risks = risks_data or {}
        naturels = risks.get("naturels", {})

        inondation_present = naturels.get("inondation", {}).get("present", False)
        inondation_level = naturels.get("inondation", {}).get("level", "inconnu")
        rga_present = naturels.get("retrait_gonflement_argile", {}).get("present", False)
        rga_level = naturels.get("retrait_gonflement_argile", {}).get("level", "inconnu")
        seisme_present = naturels.get("seisme", {}).get("present", False)
        seisme_level = naturels.get("seisme", {}).get("level", "inconnu")
        feu_present = naturels.get("feu_foret", {}).get("present", False)
        catnat_count = risks.get("catnat_last_10_years", 0)

        return (
            f"Analyse ce bien immobilier et génère un rapport de risque structuré.\n\n"
            f"## Bien analysé\n"
            f"Adresse: {address_label}\n"
            f"Année construction: {building.get('built_year', 'Inconnue')}\n"
            f"Surface: {building.get('surface_utile', 'Inconnue')} m²\n"
            f"Niveaux: {building.get('levels', 'Inconnu')}\n"
            f"Matériaux murs: {building.get('wall_material', 'Inconnu')}\n"
            f"Toiture: {building.get('roof_material', 'Inconnue')}\n"
            f"DPE: {building.get('dpe_class', 'Inconnu')}\n\n"
            f"## Scores de risque calculés (0-100, 100 = risque maximal)\n"
            f"- Score global: {scores.get('global_score', 0)}/100\n"
            f"- Inondation: {scores.get('inondation', 0)}/100\n"
            f"- Retrait-Gonflement Argiles: {scores.get('rga', 0)}/100\n"
            f"- Tempête/Vent: {scores.get('tempete', 0)}/100\n"
            f"- Incendie/Feux de forêt: {scores.get('incendie', 0)}/100\n"
            f"- Séisme: {scores.get('seisme', 0)}/100\n\n"
            f"## Données Géorisques\n"
            f"- Zone inondation: {'Oui (' + str(inondation_level) + ')' if inondation_present else 'Non'}\n"
            f"- RGA: {'Oui (' + str(rga_level) + ')' if rga_present else 'Non'}\n"
            f"- Séisme: {'Oui (' + str(seisme_level) + ')' if seisme_present else 'Non'}\n"
            f"- Feu de forêt: {'Oui' if feu_present else 'Non'}\n"
            f"- CATNAT 10 dernières années: {catnat_count} événements\n\n"
            f"## Formulaire expert (déclaratif)\n"
            f"- Type bien: {expert_fields.get('type_bien', 'Non renseigné')}\n"
            f"- Sous-sol: {expert_fields.get('sous_sol', 'Non renseigné')}\n"
            f"- Hauteur plancher: {expert_fields.get('hauteur_plancher', 'Non renseigné')} cm\n"
            f"- Clapet anti-retour: {expert_fields.get('clapet', 'Non renseigné')}\n"
            f"- Profondeur fondations: {expert_fields.get('prof_fondations', 'Non renseigné')}\n"
            f"- Fissures: {expert_fields.get('fissures', 'Non renseigné')}\n"
            f"- Âge toiture: {expert_fields.get('age_toiture', 'Non renseigné')} ans\n"
            f"- Capital assuré: {expert_fields.get('capital_assure', 'Non renseigné')} €\n"
        )

    @staticmethod
    async def generate_report(
        address_label: str,
        building_data: dict | None,
        risks_data: dict | None,
        expert_fields: dict[str, str],
        scores: dict[str, int],
    ) -> dict[str, Any]:
        """
        Generate a structured risk report using Mistral AI.
        Falls back to a deterministic report if the API key is not configured.
        """
        if not settings.MISTRAL_API_KEY:
            return _build_fallback_report(scores, address_label)

        messages = [
            {"role": "system", "content": MistralService.SYSTEM_PROMPT},
            {
                "role": "user",
                "content": MistralService._build_user_prompt(
                    address_label, building_data, risks_data, expert_fields, scores
                ),
            },
        ]

        async with httpx.AsyncClient(timeout=CLIENT_TIMEOUT) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
                },
                json={
                    "model": settings.MISTRAL_MODEL,
                    "messages": messages,
                    "temperature": 0.2,
                    "max_tokens": 1500,
                    "response_format": {"type": "json_object"},
                },
            )

            if not response.is_success:
                error_text = response.text
                raise RuntimeError(f"Mistral API error {response.status_code}: {error_text}")

            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content")
            if not content:
                raise RuntimeError("Empty response from Mistral")

            parsed = json.loads(content)

            # Validate required fields
            if not parsed.get("niveauRisque") or not parsed.get("syntheseTexte"):
                raise RuntimeError("Invalid Mistral response structure")

            return parsed

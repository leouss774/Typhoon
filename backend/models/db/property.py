"""
Property ORM Model
==================
Port of `backend/database/schema.ts` → `properties` table.
Contains 50+ fields covering address, structure, roof, insulation,
basement, electricity, exposure, flood, RGA, insurance, DPE, etc.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.db.mixins import TimestampMixin


class Property(Base, TimestampMixin):
    __tablename__ = "properties"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clients.id", ondelete="cascade"), nullable=False
    )

    # ── Address ──
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    postal_code: Mapped[str | None] = mapped_column("postal_code", String(10), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ── General ──
    type_bien: Mapped[str | None] = mapped_column("type_bien", String(30), nullable=True)
    surface: Mapped[float | None] = mapped_column(Float, nullable=True)
    nb_pieces: Mapped[int | None] = mapped_column("nb_pieces", Integer, nullable=True)
    nb_etages: Mapped[int | None] = mapped_column("nb_etages", Integer, nullable=True)
    annee_construction: Mapped[int | None] = mapped_column("annee_construction", Integer, nullable=True)
    annee_renovation: Mapped[int | None] = mapped_column("annee_renovation", Integer, nullable=True)

    # ── Structure ──
    type_structure: Mapped[str | None] = mapped_column("type_structure", String(30), nullable=True)
    etat_structure: Mapped[str | None] = mapped_column("etat_structure", String(20), nullable=True)
    fissures: Mapped[str | None] = mapped_column(String(30), nullable=True)
    affaissement: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # ── Roof & Insulation ──
    type_toiture: Mapped[str | None] = mapped_column("type_toiture", String(30), nullable=True)
    age_toiture: Mapped[int | None] = mapped_column("age_toiture", Integer, nullable=True)
    annee_toiture: Mapped[int | None] = mapped_column("annee_toiture", Integer, nullable=True)
    etat_toiture: Mapped[str | None] = mapped_column("etat_toiture", String(20), nullable=True)
    isolation_toiture: Mapped[str | None] = mapped_column("isolation_toiture", String(15), nullable=True)
    isolation_murs: Mapped[str | None] = mapped_column("isolation_murs", String(15), nullable=True)
    isolation_sol: Mapped[str | None] = mapped_column("isolation_sol", String(15), nullable=True)
    infiltrations: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # ── Basement & Equipment ──
    presence_sous_sol: Mapped[bool | None] = mapped_column("presence_sous_sol", Boolean, nullable=True)
    presence_cave: Mapped[bool | None] = mapped_column("presence_cave", Boolean, nullable=True)
    presence_garage: Mapped[bool | None] = mapped_column("presence_garage", Boolean, nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(20), nullable=True)
    climatisation: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    chauffage_principal: Mapped[str | None] = mapped_column("chauffage_principal", String(30), nullable=True)

    # ── Electricity & Safety ──
    installation_electrique_annee: Mapped[int | None] = mapped_column(
        "installation_electrique_annee", Integer, nullable=True
    )
    presence_detecteurs_fumee: Mapped[bool | None] = mapped_column(
        "presence_detecteurs_fumee", Boolean, nullable=True
    )

    # ── Exposure & Environment ──
    exposition_solaire: Mapped[str | None] = mapped_column("exposition_solaire", String(15), nullable=True)
    zone_mitoyennete: Mapped[str | None] = mapped_column("zone_mitoyennete", String(30), nullable=True)

    # ── Flood ──
    hauteur_plancher: Mapped[float | None] = mapped_column("hauteur_plancher", Float, nullable=True)
    clapet_anti_retour: Mapped[bool | None] = mapped_column("clapet_anti_retour", Boolean, nullable=True)
    equipements_elec_sous_sol: Mapped[bool | None] = mapped_column(
        "equipements_elec_sous_sol", Boolean, nullable=True
    )

    # ── RGA ──
    profondeur_fondations: Mapped[str | None] = mapped_column("profondeur_fondations", String(30), nullable=True)
    arbres_proches: Mapped[bool | None] = mapped_column("arbres_proches", Boolean, nullable=True)
    materiau_toit: Mapped[str | None] = mapped_column("materiau_toit", String(30), nullable=True)
    panneaux_solaires: Mapped[bool | None] = mapped_column("panneaux_solaires", Boolean, nullable=True)

    # ── Insurance ──
    capital_assure: Mapped[float | None] = mapped_column("capital_assure", Float, nullable=True)

    # ── DPE & BDNB ──
    dpe_class: Mapped[str | None] = mapped_column("dpe_class", String(5), nullable=True)
    built_year: Mapped[int | None] = mapped_column("built_year", Integer, nullable=True)
    ban_id: Mapped[str | None] = mapped_column("ban_id", String(50), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Observations ──
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Form status ──
    form_completed: Mapped[bool | None] = mapped_column("form_completed", Boolean, default=False)

    # Relationships
    client = relationship("Client", back_populates="properties")
    assessments = relationship("Assessment", back_populates="property", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Property {self.address}>"

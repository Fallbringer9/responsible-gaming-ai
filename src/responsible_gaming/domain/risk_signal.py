from dataclasses import dataclass
from decimal import Decimal

from responsible_gaming.domain.risk_signal_code import RiskSignalCode
from responsible_gaming.domain.severity import Severity


@dataclass(frozen=True, slots=True)
class RiskSignal:
    code: RiskSignalCode
    severity: Severity
    observed_value: Decimal | int
    threshold: Decimal | int

    @property
    def title(self) -> str:
        return _SIGNAL_METADATA[self.code]["title"]

    @property
    def description(self) -> str:
        return _SIGNAL_METADATA[self.code]["description"]


_SIGNAL_METADATA = {
    RiskSignalCode.HIGH_DEPOSIT: {
        "title": "Dépôts importants",
        "description": (
            "Le montant total des dépôts du joueur dépasse le seuil configuré."
        ),
    },
    RiskSignalCode.NIGHT_SESSION: {
        "title": "Sessions de jeu nocturnes",
        "description": (
            "Le joueur dépasse le nombre configuré de sessions de jeu nocturnes."
        ),
    },
    RiskSignalCode.FREQUENT_DEPOSIT: {
        "title": "Dépôts fréquents",
        "description": ("Le joueur dépasse le nombre configuré de dépôts."),
    },
    RiskSignalCode.LIMIT_INCREASE: {
        "title": "Demandes d'augmentation des limites",
        "description": (
            "Le joueur dépasse le nombre configuré de "
            "demandes d'augmentation des limites."
        ),
    },
    RiskSignalCode.FAILED_DEPOSIT: {
        "title": "Tentatives de dépôt refusées",
        "description": (
            "Le joueur dépasse le nombre configuré de tentatives de dépôt refusées."
        ),
    },
    RiskSignalCode.CANCELLED_WITHDRAWAL: {
        "title": "Retraits annulés",
        "description": ("Le joueur dépasse le nombre configuré de retraits annulés."),
    },
}

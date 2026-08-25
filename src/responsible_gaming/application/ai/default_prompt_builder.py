from responsible_gaming.application.ai.prompt import Prompt
from responsible_gaming.application.ai.prompt_builder import PromptBuilder
from responsible_gaming.application.rag.knowledge_document import (
    KnowledgeDocument,
)
from responsible_gaming.domain.risk_analysis_result import RiskAnalysisResult


class DefaultPromptBuilder(PromptBuilder):
    """Builds the AI prompt from risk signals and retrieved knowledge."""

    def build(
        self,
        analysis: RiskAnalysisResult,
        documents: tuple[KnowledgeDocument, ...],
    ) -> Prompt:
        signal_lines = [
            (
                f"- {signal.title}: "
                f"observed={signal.observed_value}, "
                f"threshold={signal.threshold}, "
                f"severity={signal.severity}"
            )
            for signal in analysis.signals
        ]

        document_sections = [
            (
                f"Source: {document.title}\n"
                f"Reference: {document.source}\n"
                f"Content: {document.content}"
            )
            for document in documents
        ]

        system_prompt = """
You are a responsible gaming risk assessment assistant.

Assess the player's risk using only:
- the deterministic risk signals provided,
- the retrieved reference documents.

Do not invent facts that are not supported by the provided information.

Return only valid JSON matching this exact structure:

{
  "risk_level": "LOW | MEDIUM | HIGH | CRITICAL",
  "confidence": 0.0,
  "reasoning": "string",
  "recommendation": {
    "summary": "string",
    "actions": [
      {
        "title": "string",
        "description": "string",
        "priority": "LOW | MEDIUM | HIGH",
        "category": "ALLOWED_CATEGORY"
      }
    ]
  }
}

Allowed category values:
- DEPOSIT_LIMIT
- LOSS_LIMIT
- SESSION_LIMIT
- COOLING_OFF
- SELF_EXCLUSION
- RESPONSIBLE_GAMING_INFORMATION
- HUMAN_CONTACT

Rules:
- confidence must be between 0 and 1,
- risk_level must use one of the allowed values,
- priority must use one of the allowed values,
- category must use one of the allowed category values,
- recommendation.actions must contain at least one action,
- Never invent or infer numerical thresholds, monetary amounts,
  durations, limits, or intervention parameters.
- If a specific value is not explicitly supported by the provided
  risk signals or reference documents, do not provide that value.
- Recommendations must remain qualitative when the provided
  information does not support a specific value.
- do not include Markdown,
- do not include text before or after the JSON.
"""

        user_prompt = (
            "Detected risk signals:\n"
            f"{'\n'.join(signal_lines)}\n\n"
            "Reference documents:\n"
            f"{'\n\n'.join(document_sections)}"
        )

        return Prompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

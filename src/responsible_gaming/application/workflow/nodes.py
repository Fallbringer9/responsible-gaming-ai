from responsible_gaming.application.ai.prompt_builder import PromptBuilder
from responsible_gaming.application.ai.risk_assessment_service import (
    RiskAssessmentService,
)
from responsible_gaming.application.ai.risk_level import RiskLevel
from responsible_gaming.application.rag.knowledge_query_builder import (
    KnowledgeQueryBuilder,
)
from responsible_gaming.application.rag.retrieve_knowledge_service import (
    RetrieveKnowledgeService,
)
from responsible_gaming.application.workflow.state import ResponsibleGamingState
from responsible_gaming.application.workflow.state_mapper import (
    analysis_from_state,
    analysis_to_state,
    assessment_from_state,
    assessment_to_state,
    documents_from_state,
    documents_to_state,
    prompt_from_state,
    prompt_to_state,
    snapshot_from_state,
)
from responsible_gaming.domain.risk_analysis_service import RiskAnalysisService


def analyze_node(
    state: ResponsibleGamingState,
    analysis_service: RiskAnalysisService,
) -> dict:
    snapshot = snapshot_from_state(
        state["snapshot"],
    )

    analysis = analysis_service.analyze(snapshot)

    return {
        "analysis": analysis_to_state(analysis),
    }


def retrieve_knowledge_node(
    state: ResponsibleGamingState,
    query_builder: KnowledgeQueryBuilder,
    retriever: RetrieveKnowledgeService,
) -> dict:
    analysis = analysis_from_state(
        state["analysis"],
    )

    query = query_builder.build(analysis)
    documents = retriever.retrieve(query)

    return {
        "documents": documents_to_state(documents),
    }


def build_prompt_node(
    state: ResponsibleGamingState,
    prompt_builder: PromptBuilder,
) -> dict:
    analysis = analysis_from_state(
        state["analysis"],
    )

    documents = documents_from_state(
        state["documents"],
    )

    prompt = prompt_builder.build(
        analysis=analysis,
        documents=documents,
    )

    return {
        "prompt": prompt_to_state(prompt),
    }


def assess_risk_node(
    state: ResponsibleGamingState,
    assessment_service: RiskAssessmentService,
) -> dict:
    prompt = prompt_from_state(
        state["prompt"],
    )

    assessment = assessment_service.assess(prompt)

    return {
        "assessment": assessment_to_state(assessment),
    }


def decide_human_review_node(
    state: ResponsibleGamingState,
) -> dict:
    assessment = assessment_from_state(
        state["assessment"],
    )

    human_review_required = assessment.risk_level in {
        RiskLevel.HIGH,
        RiskLevel.CRITICAL,
    }

    return {
        "human_review_required": human_review_required,
    }

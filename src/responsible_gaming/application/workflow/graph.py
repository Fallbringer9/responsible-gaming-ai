from langgraph.graph import END, START, StateGraph

from responsible_gaming.application.ai.prompt_builder import PromptBuilder
from responsible_gaming.application.ai.risk_assessment_service import (
    RiskAssessmentService,
)
from responsible_gaming.application.rag.knowledge_query_builder import (
    KnowledgeQueryBuilder,
)
from responsible_gaming.application.rag.retrieve_knowledge_service import (
    RetrieveKnowledgeService,
)
from responsible_gaming.application.workflow.nodes import (
    analyze_node,
    assess_risk_node,
    build_low_risk_assessment_node,
    build_prompt_node,
    decide_human_review_node,
    retrieve_knowledge_node,
    route_after_analysis,
)
from responsible_gaming.application.workflow.state import ResponsibleGamingState
from responsible_gaming.domain.risk_analysis_service import RiskAnalysisService


def build_responsible_gaming_graph(
    analysis_service: RiskAnalysisService,
    query_builder: KnowledgeQueryBuilder,
    retriever: RetrieveKnowledgeService,
    prompt_builder: PromptBuilder,
    assessment_service: RiskAssessmentService,
):
    builder = StateGraph(ResponsibleGamingState)

    builder.add_node(
        "analyze",
        lambda state: analyze_node(
            state=state,
            analysis_service=analysis_service,
        ),
    )

    builder.add_node(
        "build_low_risk_assessment",
        build_low_risk_assessment_node,
    )

    builder.add_node(
        "retrieve_knowledge",
        lambda state: retrieve_knowledge_node(
            state=state,
            query_builder=query_builder,
            retriever=retriever,
        ),
    )

    builder.add_node(
        "build_prompt",
        lambda state: build_prompt_node(
            state=state,
            prompt_builder=prompt_builder,
        ),
    )

    builder.add_node(
        "assess_risk",
        lambda state: assess_risk_node(
            state=state,
            assessment_service=assessment_service,
        ),
    )

    builder.add_node(
        "decide_human_review",
        decide_human_review_node,
    )

    builder.add_edge(
        START,
        "analyze",
    )

    builder.add_conditional_edges(
        "analyze",
        route_after_analysis,
        {
            "retrieve_knowledge": "retrieve_knowledge",
            "build_low_risk_assessment": "build_low_risk_assessment",
        },
    )

    builder.add_edge(
        "build_low_risk_assessment",
        END,
    )

    builder.add_edge(
        "retrieve_knowledge",
        "build_prompt",
    )

    builder.add_edge(
        "build_prompt",
        "assess_risk",
    )

    builder.add_edge(
        "assess_risk",
        "decide_human_review",
    )

    builder.add_edge(
        "decide_human_review",
        END,
    )

    return builder.compile()

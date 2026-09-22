const API_BASE_URL = "/api";

const reviewList = document.getElementById("review-list");
const refreshButton = document.getElementById("refresh-button");

const emptyState = document.getElementById("empty-state");
const assessmentPanel = document.getElementById("assessment-panel");

const assessmentIdElement = document.getElementById("assessment-id");
const riskLevelElement = document.getElementById("risk-level");
const confidenceElement = document.getElementById("confidence");
const reviewStatusElement = document.getElementById("review-status");
const reasoningElement = document.getElementById("reasoning");

const recommendationSummaryElement = document.getElementById(
    "recommendation-summary",
);
const recommendationActionsElement = document.getElementById(
    "recommendation-actions",
);

const reviewComment = document.getElementById("review-comment");
const approveButton = document.getElementById("approve-button");
const rejectButton = document.getElementById("reject-button");
const decisionMessage = document.getElementById("decision-message");

const decisionModal = document.getElementById("decision-modal");
const decisionModalIcon = document.getElementById("decision-modal-icon");
const decisionModalTitle = document.getElementById("decision-modal-title");
const decisionModalDescription = document.getElementById(
    "decision-modal-description",
);
const decisionModalAssessmentId = document.getElementById(
    "decision-modal-assessment-id",
);
const decisionModalCancel = document.getElementById(
    "decision-modal-cancel",
);
const decisionModalConfirm = document.getElementById(
    "decision-modal-confirm",
);

let selectedAssessmentId = null;
let pendingDecision = null;


async function fetchJson(url, options = {}) {
    const response = await fetch(url, options);

    let body = null;

    try {
        body = await response.json();
    } catch {
        body = null;
    }

    if (!response.ok) {
        const message = body?.error ?? `HTTP error ${response.status}`;
        throw new Error(message);
    }

    return body;
}


async function loadReviews() {
    reviewList.innerHTML = "<p>Loading assessments...</p>";
    refreshButton.disabled = true;

    try {
        const data = await fetchJson(
            `${API_BASE_URL}/assessments?limit=20`,
        );

        renderReviewList(data.reviews);
    } catch (error) {
        reviewList.innerHTML = "";

        const message = document.createElement("p");
        message.textContent = `Unable to load assessments: ${error.message}`;

        reviewList.appendChild(message);
    } finally {
        refreshButton.disabled = false;
    }
}


function renderReviewList(reviews) {
    reviewList.innerHTML = "";

    if (reviews.length === 0) {
        const emptyMessage = document.createElement("p");
        emptyMessage.textContent = "No pending assessments.";

        reviewList.appendChild(emptyMessage);
        return;
    }

    for (const review of reviews) {
        const button = document.createElement("button");

        button.type = "button";
        button.className = "review-item";
        button.dataset.assessmentId = review.assessment_id;

        const assessmentId = document.createElement("span");
        assessmentId.className = "review-item-id";
        assessmentId.textContent = review.assessment_id;

        const metadata = document.createElement("div");
        metadata.className = "review-item-meta";

        const riskLevel = document.createElement("span");
        riskLevel.textContent = review.assessment.risk_level;

        const confidence = document.createElement("span");
        confidence.textContent = formatConfidence(
            review.assessment.confidence,
        );

        metadata.append(riskLevel, confidence);
        button.append(assessmentId, metadata);

        button.addEventListener("click", () => {
            loadAssessment(review.assessment_id);
        });

        reviewList.appendChild(button);
    }
}


async function loadAssessment(assessmentId) {
    setDecisionLoading(false);

    decisionMessage.textContent = "";
    reviewComment.value = "";

    try {
        const review = await fetchJson(
            `${API_BASE_URL}/assessments/${assessmentId}`,
        );

        selectedAssessmentId = assessmentId;

        renderAssessment(review);
        markSelectedReview(assessmentId);
    } catch (error) {
        decisionMessage.textContent =
            `Unable to load assessment: ${error.message}`;
    }
}


function renderAssessment(review) {
    const assessment = review.assessment;
    const recommendation = assessment.recommendation;

    emptyState.hidden = true;
    assessmentPanel.hidden = false;

    assessmentIdElement.textContent = review.assessment_id;
    riskLevelElement.textContent = assessment.risk_level;

    confidenceElement.textContent = formatConfidence(
        assessment.confidence,
    );

    reviewStatusElement.textContent =
        review.review_status ?? "UNKNOWN";

    reasoningElement.textContent = assessment.reasoning;

    recommendationSummaryElement.textContent =
        recommendation?.summary ?? "No recommendation available.";

    renderRecommendationActions(recommendation?.actions ?? []);
}


function renderRecommendationActions(actions) {
    recommendationActionsElement.innerHTML = "";

    for (const action of actions) {
        const card = document.createElement("article");
        card.className = "recommendation-action";

        const title = document.createElement("h4");
        title.textContent = action.title;

        const description = document.createElement("p");
        description.textContent = action.description;

        const metadata = document.createElement("div");
        metadata.className = "recommendation-meta";

        const priority = document.createElement("span");
        priority.className = "priority-badge";
        priority.textContent = action.priority;

        const category = document.createElement("span");
        category.className = "category-badge";
        category.textContent = formatCategory(action.category);

        metadata.append(priority, category);
        card.append(title, description, metadata);

        recommendationActionsElement.appendChild(card);
    }
}


function openDecisionModal(decision) {
    if (!selectedAssessmentId) {
        return;
    }

    pendingDecision = decision;

    const isApproval = decision === "APPROVED";

    decisionModalTitle.textContent = isApproval
        ? "Approve this assessment?"
        : "Reject this assessment?";

    decisionModalDescription.textContent = isApproval
        ? "This decision will resume the suspended workflow and finalize the human review."
        : "This decision will resume the suspended workflow with a rejected human review.";

    decisionModalAssessmentId.textContent = selectedAssessmentId;

    decisionModalIcon.textContent = isApproval ? "✓" : "×";
    decisionModalIcon.className =
        `decision-modal-icon ${isApproval ? "approve" : "reject"}`;

    decisionModalConfirm.textContent = isApproval
        ? "Approve"
        : "Reject";

    decisionModalConfirm.className =
        `modal-confirm-button ${isApproval ? "approve" : "reject"}`;

    decisionModal.hidden = false;
    document.body.classList.add("modal-open");

    decisionModalConfirm.focus();
}


function closeDecisionModal() {
    if (decisionModalConfirm.disabled) {
        return;
    }

    decisionModal.hidden = true;
    document.body.classList.remove("modal-open");

    pendingDecision = null;
}


async function submitDecision(decision) {
    if (!selectedAssessmentId) {
        return;
    }

    setDecisionLoading(true);
    setModalLoading(true);

    decisionMessage.textContent = "Submitting decision...";

    try {
        const result = await fetchJson(
            `${API_BASE_URL}/assessments/${selectedAssessmentId}/review`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    decision,
                    comment: reviewComment.value.trim() || null,
                }),
            },
        );

        decisionModal.hidden = true;
        document.body.classList.remove("modal-open");

        pendingDecision = null;

        decisionMessage.textContent =
            `Review ${result.review_status.toLowerCase()} successfully.`;

        await loadReviews();

        selectedAssessmentId = null;

        window.setTimeout(() => {
            resetAssessment();
        }, 700);
    } catch (error) {
        decisionMessage.textContent =
            `Unable to submit decision: ${error.message}`;

        decisionModal.hidden = true;
        document.body.classList.remove("modal-open");

        pendingDecision = null;
    } finally {
        setDecisionLoading(false);
        setModalLoading(false);
    }
}


function markSelectedReview(assessmentId) {
    const reviewItems = document.querySelectorAll(".review-item");

    for (const item of reviewItems) {
        item.classList.toggle(
            "active",
            item.dataset.assessmentId === assessmentId,
        );
    }
}


function resetAssessment() {
    selectedAssessmentId = null;

    assessmentPanel.hidden = true;
    emptyState.hidden = false;

    reviewComment.value = "";
    decisionMessage.textContent = "";
}


function setDecisionLoading(isLoading) {
    approveButton.disabled = isLoading;
    rejectButton.disabled = isLoading;
}


function setModalLoading(isLoading) {
    decisionModalConfirm.disabled = isLoading;
    decisionModalCancel.disabled = isLoading;
}


function formatConfidence(confidence) {
    if (typeof confidence !== "number") {
        return "—";
    }

    return `${Math.round(confidence * 100)}%`;
}


function formatCategory(category) {
    if (!category) {
        return "OTHER";
    }

    return category
        .toLowerCase()
        .split("_")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ");
}


refreshButton.addEventListener("click", loadReviews);

approveButton.addEventListener("click", () => {
    openDecisionModal("APPROVED");
});

rejectButton.addEventListener("click", () => {
    openDecisionModal("REJECTED");
});

decisionModalCancel.addEventListener("click", closeDecisionModal);

decisionModalConfirm.addEventListener("click", () => {
    if (pendingDecision) {
        submitDecision(pendingDecision);
    }
});

decisionModal.addEventListener("click", (event) => {
    if (event.target === decisionModal) {
        closeDecisionModal();
    }
});

document.addEventListener("keydown", (event) => {
    if (
        event.key === "Escape"
        && !decisionModal.hidden
    ) {
        closeDecisionModal();
    }
});


loadReviews();

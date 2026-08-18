# Responsible Gaming AI

Plateforme d'analyse du jeu responsable basée sur Python, AWS et l'intelligence artificielle générative.

## Présentation

Après 12 années d'expérience dans l'industrie des casinos, j'ai entrepris une reconversion vers le développement backend, le cloud et l'intelligence artificielle.

Responsible Gaming AI est un projet qui combine cette expertise métier avec des pratiques modernes d'ingénierie logicielle et d'IA.

L'objectif est de construire une plateforme capable de :

- détecter des indicateurs de risque à partir de règles métier déterministes ;
- enrichir cette analyse avec des documents de référence grâce à une architecture RAG ;
- utiliser un Large Language Model pour produire une évaluation structurée du risque ;
- proposer des recommandations explicables à destination des opérateurs de jeu responsable ;
- conserver un humain dans la boucle pour la décision finale.

Ce projet est développé comme une application portfolio mettant en pratique l'architecture hexagonale, le Domain-Driven Design, le RAG, l'intégration de modèles génératifs et les services AWS.

---

## Architecture

```text
                     Player Activity
                            │
                            ▼
                PlayerActivitySnapshot
                            │
                            ▼
              Deterministic Risk Analysis
                            │
                            ▼
                 RiskAnalysisResult
                            │
                            ▼
             DefaultKnowledgeQueryBuilder
                            │
                            ▼
                    KnowledgeQuery
                            │
                            ▼
              Bedrock Knowledge Base
                       (RAG)
                            │
                            ▼
                  KnowledgeDocument[]
                            │
                            ▼
                DefaultPromptBuilder
                            │
                            ▼
                         Prompt
                            │
                            ▼
                Amazon Bedrock / Claude
                            │
                            ▼
                   RiskAssessment
                            │
                            ▼
              Structured Recommendations
                            │
                            ▼
                     Human Review
```

Le pipeline est orchestré par `AnalyzePlayerUseCase`.

---

## Architecture logicielle

Le projet suit une architecture inspirée de l'architecture hexagonale afin de séparer la logique métier des services externes.

```text
src/responsible_gaming/
│
├── domain/
│   ├── PlayerActivitySnapshot
│   ├── RiskSignal
│   ├── RiskAnalysisResult
│   ├── RiskAnalysisService
│   └── deterministic detectors
│
├── application/
│   ├── ai/
│   │   ├── Prompt
│   │   ├── PromptBuilder
│   │   ├── DefaultPromptBuilder
│   │   ├── RiskAssessment
│   │   └── RiskAssessmentService
│   │
│   ├── rag/
│   │   ├── KnowledgeQuery
│   │   ├── KnowledgeQueryBuilder
│   │   ├── DefaultKnowledgeQueryBuilder
│   │   ├── KnowledgeDocument
│   │   └── RetrieveKnowledgeService
│   │
│   └── use_cases/
│       └── AnalyzePlayerUseCase
│
├── adapters/
│   └── bedrock/
│       ├── BedrockKnowledgeRetriever
│       ├── BedrockRiskAssessmentService
│       └── BedrockClientFactory
│
└── bootstrap/
    └── Composition Root
```

### Domain

Le domaine contient la logique métier indépendante de toute infrastructure.

Les signaux de risque sont détectés à l'aide de règles déterministes telles que :

- montant élevé de dépôts ;
- fréquence élevée des dépôts ;
- sessions de jeu nocturnes ;
- demandes d'augmentation de limites ;
- tentatives de dépôt échouées ;
- annulations de retraits.

Les seuils métier sont injectés dans les détecteurs et ne dépendent pas de l'infrastructure AWS ou du LLM.

### Application

La couche application orchestre les différentes étapes du pipeline.

Elle définit également des contrats avec `Protocol` afin que la logique applicative ne dépende pas directement d'Amazon Bedrock.

Exemple :

```text
RiskAssessmentService
        ▲
        │
BedrockRiskAssessmentService
```

Cette séparation permet notamment de remplacer les services externes par des fakes pendant les tests.

### Adapters

Les adapters contiennent les implémentations liées aux services externes.

`BedrockKnowledgeRetriever` traduit les résultats d'une Amazon Bedrock Knowledge Base vers des objets métier `KnowledgeDocument`.

`BedrockRiskAssessmentService` envoie le prompt au modèle via Amazon Bedrock et transforme la réponse JSON en objets Python structurés :

```text
Bedrock response
       │
       ▼
      JSON
       │
       ▼
RiskAssessment
├── RiskLevel
├── confidence
├── reasoning
└── Recommendation
```

### Composition Root

Le Composition Root constitue le point d'assemblage de l'application.

Il connecte les implémentations concrètes aux contrats utilisés par `AnalyzePlayerUseCase` :

```text
AnalyzePlayerUseCase
│
├── RiskAnalysisService
├── DefaultKnowledgeQueryBuilder
├── BedrockKnowledgeRetriever
├── DefaultPromptBuilder
└── BedrockRiskAssessmentService
```

Cette approche applique le principe d'inversion des dépendances (Dependency Inversion Principle).

---

## RAG

Le projet utilise une architecture Retrieval-Augmented Generation pour enrichir l'analyse avec des documents de référence sur le jeu responsable.

Le corpus contient notamment des documents réglementaires et des guides utilisés comme sources de connaissance.

```text
RiskAnalysisResult
        │
        ▼
KnowledgeQuery
        │
        ▼
Bedrock Knowledge Base
        │
        ▼
Relevant documents
        │
        ▼
LLM context
```

Le modèle reçoit ainsi à la fois :

- les signaux déterministes détectés ;
- les valeurs observées ;
- les seuils associés ;
- les documents pertinents récupérés par le RAG.

---

## Sortie structurée du LLM

Le modèle doit produire une réponse JSON respectant un contrat défini par l'application.

Exemple simplifié :

```json
{
  "risk_level": "HIGH",
  "confidence": 0.91,
  "reasoning": "...",
  "recommendation": {
    "summary": "...",
    "actions": [
      {
        "title": "...",
        "description": "...",
        "priority": "HIGH",
        "category": "HUMAN_CONTACT"
      }
    ]
  }
}
```

La réponse est ensuite validée et transformée en objets Python typés.

Le LLM ne remplace pas les règles métier déterministes et ne prend pas la décision finale : il intervient comme couche d'analyse et de recommandation.

---

## Tests

La suite de tests couvre actuellement :

- les modèles du domaine ;
- les détecteurs déterministes ;
- le moteur d'analyse des risques ;
- la construction des requêtes RAG ;
- le mapping des résultats Bedrock ;
- la construction des prompts ;
- le parsing des évaluations LLM ;
- l'orchestration du `AnalyzePlayerUseCase` ;
- le câblage du Composition Root.

Les services AWS sont remplacés par des fakes ou mocks dans les tests unitaires afin de garantir :

- des tests rapides ;
- aucune dépendance réseau ;
- aucun coût AWS ;
- aucune dépendance aux credentials AWS.

Exécution :

```bash
uv run pytest
```

Qualité du code :

```bash
ruff check .
ruff format --check .
```

---

## Stack technique

### Backend

- Python 3.13
- Domain-Driven Design
- Architecture hexagonale
- Dependency Inversion Principle
- Python Protocols

### IA

- Retrieval-Augmented Generation (RAG)
- Amazon Bedrock Knowledge Bases
- Amazon Bedrock
- Claude
- Structured LLM outputs

### Qualité

- Pytest
- Ruff
- uv

### Cloud / Infrastructure

En cours d'intégration :

- AWS Lambda
- Amazon S3
- Amazon SQS
- Amazon CloudFront
- Terraform
- GitHub Actions
- Datadog

### Orchestration

Prévu :

- LangGraph

---

## État actuel

### Implémenté

- ✅ Structure du projet
- ✅ Modèle de domaine
- ✅ Détection déterministe des signaux de risque
- ✅ Service d'analyse déterministe
- ✅ Contrats applicatifs avec `Protocol`
- ✅ Construction des requêtes RAG
- ✅ Adapter Amazon Bedrock Knowledge Base
- ✅ Mapping des documents RAG
- ✅ Construction du prompt LLM
- ✅ Contrat de sortie JSON structuré
- ✅ Adapter d'évaluation du risque via Bedrock
- ✅ Mapping vers `RiskAssessment`
- ✅ Orchestration avec `AnalyzePlayerUseCase`
- ✅ Composition Root
- ✅ Tests unitaires du pipeline

### En cours / prochaines étapes

- 🚧 Connexion et validation end-to-end avec les services AWS réels
- 🚧 Orchestration du workflow avec LangGraph
- 🚧 Lambda / API
- 🚧 Infrastructure as Code avec Terraform
- 🚧 CI/CD avec GitHub Actions
- 🚧 Observabilité
- 🚧 Interface de revue humaine

---

## Principes du projet

### Déterministe avant génératif

Les signaux de risque sont détectés par des règles métier déterministes.

Le LLM intervient ensuite pour enrichir l'analyse et générer des recommandations contextualisées.

```text
Business Rules
      ↓
Risk Signals
      ↓
RAG
      ↓
LLM reasoning
      ↓
Recommendation
      ↓
Human decision
```

### Human-in-the-loop

Le système est conçu comme un outil d'aide à la décision.

L'évaluation produite par l'IA ne remplace pas l'expertise d'un opérateur de jeu responsable. La décision finale reste humaine.

### Séparation métier / infrastructure

Le domaine ne dépend ni d'AWS, ni de Bedrock, ni d'un modèle spécifique.

Cette séparation permet de faire évoluer l'infrastructure sans modifier la logique métier centrale.

---

## Objectifs

Ce projet vise à démontrer la capacité à construire une application AI/backend combinant :

- expertise métier ;
- clean architecture ;
- développement Python typé ;
- intégration AWS ;
- RAG ;
- LLM ;
- tests automatisés ;
- infrastructure cloud ;
- observabilité ;
- pratiques CI/CD.

---

## Licence

MIT

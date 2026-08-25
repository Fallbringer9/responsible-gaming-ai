# Responsible Gaming AI

Plateforme d'analyse du jeu responsable basée sur Python, AWS et l'intelligence artificielle générative.

## Présentation

Après 12 années d'expérience dans l'industrie des casinos, j'ai entrepris une reconversion vers le développement backend, le cloud et l'intelligence artificielle.

Responsible Gaming AI est un projet qui combine cette expertise métier avec des pratiques modernes d'ingénierie logicielle, d'architecture cloud et d'IA.

L'objectif est de construire une plateforme capable de :

- détecter des indicateurs de risque à partir de règles métier déterministes ;
- enrichir cette analyse avec des documents de référence grâce à une architecture RAG ;
- utiliser un Large Language Model pour produire une évaluation structurée du risque ;
- proposer des recommandations explicables à destination des opérateurs de jeu responsable ;
- orchestrer le traitement de manière événementielle sur AWS ;
- conserver un humain dans la boucle pour la décision finale.

Ce projet est développé comme une application portfolio mettant en pratique l'architecture hexagonale, le Domain-Driven Design, le RAG, LangGraph, les services AWS et l'Infrastructure as Code avec Terraform.

---

## Architecture

Le pipeline est conçu autour d'une architecture événementielle.

```text
                    Player Activity JSON
                            │
                            ▼
                       Amazon S3
                            │
                     ObjectCreated
                            ▼
                       Amazon SQS
                      ┌─────┴─────┐
                      │           │
                      │          DLQ
                      ▼
                  Dispatcher Lambda
                            │
                            ▼
                    AWS Step Functions
                            │
                            ▼
                    Assessment Lambda
                            │
                            ▼
                        LangGraph
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
                Amazon Bedrock / Claude
                            │
                            ▼
                   RiskAssessment
                            │
                            ▼
                  NeedHumanReview?
                       (Choice)
                     ┌──────┴──────┐
                     │             │
                   false          true
                     │             │
                     │      WaitForHumanReview
                     │        (placeholder)
                     │             │
                     └──────┬──────┘
                            ▼
                         Finalize
                            │
                            ▼
                     Amazon DynamoDB
```

Le pipeline d'analyse applicatif est orchestré avec LangGraph.

AWS Step Functions orchestre le traitement distribué entre les composants AWS et porte la logique de branchement vers la revue humaine.

Les événements d'entrée sont déposés dans Amazon S3 puis transmis via Amazon SQS à une Lambda de dispatch, qui démarre une nouvelle exécution Step Functions.

Les évaluations produites sont finalement persistées dans Amazon DynamoDB.

---

## Architecture logicielle

Le projet suit une architecture inspirée de l'architecture hexagonale afin de séparer la logique métier des services externes et de l'infrastructure AWS.

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
│   │   ├── Recommendation
│   │   └── RiskAssessmentService
│   │
│   ├── rag/
│   │   ├── KnowledgeQuery
│   │   ├── KnowledgeQueryBuilder
│   │   ├── DefaultKnowledgeQueryBuilder
│   │   ├── KnowledgeDocument
│   │   └── RetrieveKnowledgeService
│   │
│   ├── workflow/
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   ├── state.py
│   │   └── state_mapper.py
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
├── interfaces/
│   └── lambda_handlers/
│       ├── dispatcher.py
│       └── assessment.py
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

Les seuils métier sont injectés dans les détecteurs et ne dépendent ni d'AWS, ni de Bedrock, ni du LLM.

Cette séparation permet de conserver une logique métier testable et prévisible avant toute intervention de l'IA générative.

### Application

La couche application contient les cas d'usage et les composants nécessaires à l'orchestration du pipeline d'analyse.

Elle définit également des contrats avec `Protocol` afin que la logique applicative ne dépende pas directement des implémentations AWS.

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

`BedrockKnowledgeRetriever` traduit les résultats d'une Amazon Bedrock Knowledge Base vers des objets applicatifs `KnowledgeDocument`.

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
    └── actions[]
```

### Composition Root

Le Composition Root constitue le point d'assemblage de l'application.

Il connecte les implémentations concrètes aux contrats utilisés par le pipeline :

```text
AnalyzePlayerUseCase
│
├── RiskAnalysisService
├── DefaultKnowledgeQueryBuilder
├── BedrockKnowledgeRetriever
├── DefaultPromptBuilder
└── BedrockRiskAssessmentService
```

Cette approche applique notamment le principe d'inversion des dépendances (Dependency Inversion Principle).

---

## Workflow LangGraph

LangGraph orchestre les différentes étapes nécessaires à la production d'une évaluation.

```text
Analyze
   │
   ▼
Retrieve Knowledge
   │
   ▼
Build Prompt
   │
   ▼
Assess Risk
   │
   ▼
Decide Human Review
```

Chaque node possède une responsabilité spécifique.

L'état LangGraph utilise des structures sérialisables afin de permettre au workflow de circuler proprement entre les différentes étapes.

LangGraph reste responsable du workflow d'analyse IA.

AWS Step Functions est utilisé à un niveau supérieur pour orchestrer le traitement distribué, les composants AWS et, à terme, l'attente asynchrone liée à la validation humaine.

Cette séparation permet notamment d'éviter de maintenir une Lambda active pendant une revue humaine potentiellement longue.

---

## Pipeline événementiel AWS

L'entrée du système repose sur Amazon S3.

Un snapshot d'activité joueur au format JSON est déposé dans le bucket d'entrée :

```text
JSON
 │
 ▼
Amazon S3
 │
 │ ObjectCreated
 ▼
Amazon SQS
 │
 ▼
Dispatcher Lambda
 │
 ▼
AWS Step Functions
```

Amazon SQS joue le rôle de buffer entre l'arrivée des fichiers et leur traitement.

Une Dead-Letter Queue permet d'isoler les messages qui échouent après plusieurs tentatives.

Le mapping Lambda/SQS utilise également le mécanisme de partial batch failure afin qu'un message invalide n'impose pas le retraitement des messages correctement traités du même batch.

La Lambda `dispatcher` transforme l'événement reçu en un contrat plus simple contenant notamment :

```json
{
  "assessment_id": "...",
  "input": {
    "bucket": "...",
    "key": "..."
  }
}
```

Elle démarre ensuite une exécution AWS Step Functions.

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

L'objectif est de conserver une base déterministe pour la détection tout en utilisant le LLM pour contextualiser l'analyse et produire des recommandations structurées.

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

## Human-in-the-loop

Le système est conçu comme un outil d'aide à la décision.

L'évaluation produite par l'IA ne remplace pas l'expertise d'un opérateur de jeu responsable. La décision finale reste humaine.

Après l'évaluation, le workflow produit notamment :

```json
{
  "human_review_required": true
}
```

AWS Step Functions utilise ensuite un état `Choice` pour déterminer le chemin à emprunter :

```text
RiskAssessment
      │
      ▼
human_review_required
      │
      ▼
NeedHumanReview
     Choice
   ┌───┴───┐
 false    true
   │        │
   ▼        ▼
Finalize  WaitForHumanReview
```

Le branchement conditionnel est actuellement implémenté et validé sur AWS.

`WaitForHumanReview` constitue pour le moment un placeholder dans le workflow.

La prochaine étape consiste à implémenter une véritable attente asynchrone avec le mécanisme Task Token de Step Functions, puis à permettre à un opérateur d'approuver ou de rejeter l'évaluation depuis une interface dédiée.

---

## Persistance

Les évaluations produites par le workflow sont persistées dans Amazon DynamoDB.

La table utilise `assessment_id` comme partition key :

```text
responsible-gaming-assessments-dev

assessment_id (PK)
│
├── assessment
│   ├── risk_level
│   ├── confidence
│   ├── reasoning
│   └── recommendation
│
└── human_review_required
```

Pour la V1, la table utilise le mode `PAY_PER_REQUEST`.

L'écriture est effectuée directement par AWS Step Functions via l'intégration DynamoDB `PutItem`, sans ajouter une Lambda dédiée uniquement à la persistance.

Le rôle IAM de Step Functions dispose uniquement de la permission nécessaire sur la table concernée.

---

## Infrastructure as Code

L'infrastructure AWS est définie avec Terraform.

Les principaux composants sont organisés en modules :

```text
infra/
│
├── modules/
│   ├── storage/
│   ├── queue/
│   ├── dispatcher/
│   ├── assessment/
│   ├── workflow/
│   └── assessment_store/
│
└── environments/
    └── dev/
```

Terraform provisionne actuellement notamment :

- le bucket Amazon S3 d'entrée ;
- la file Amazon SQS ;
- la Dead-Letter Queue ;
- les politiques SQS nécessaires aux événements S3 ;
- la Dispatcher Lambda ;
- le mapping SQS → Lambda ;
- l'Assessment Lambda ;
- AWS Step Functions ;
- les rôles et politiques IAM ;
- la table Amazon DynamoDB.

Les permissions IAM sont séparées selon les responsabilités des composants afin d'éviter de donner des permissions globales inutiles.

---

## Validation end-to-end

Le pipeline a été validé sur une infrastructure AWS réelle.

Un snapshot JSON de test est déposé dans Amazon S3 et traverse le pipeline complet :

```text
Amazon S3
    │
    ▼
Amazon SQS
    │
    ▼
Dispatcher Lambda
    │
    ▼
AWS Step Functions
    │
    ▼
Assessment Lambda
    │
    ▼
LangGraph
    │
    ├── Deterministic Risk Analysis
    ├── Bedrock Knowledge Base
    └── Amazon Bedrock / Claude
    │
    ▼
RiskAssessment
    │
    ▼
Choice
    │
    ▼
DynamoDB PutItem
    │
    ▼
Persisted Assessment
```

Le scénario de validation utilisé produit notamment une évaluation `CRITICAL`, déclenche `human_review_required = true`, emprunte la branche de revue humaine du workflow puis persiste l'évaluation dans DynamoDB.

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
- les nodes du workflow LangGraph ;
- le mapping entre objets métier et état LangGraph ;
- le câblage du Composition Root ;
- le dispatcher Lambda ;
- le traitement partiel des erreurs SQS.

Les services AWS sont remplacés par des fakes ou mocks dans les tests unitaires afin de garantir :

- des tests rapides ;
- aucune dépendance réseau ;
- aucun coût AWS ;
- aucune dépendance aux credentials AWS.

Exécution :

```bash
uv run --no-editable pytest
```

Qualité du code :

```bash
uv run ruff check .
uv run ruff format --check .
```

Les tests unitaires sont complétés par des validations end-to-end sur l'infrastructure AWS déployée.

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

### Orchestration

- LangGraph
- AWS Step Functions

### Cloud / Infrastructure

- AWS Lambda
- Amazon S3
- Amazon SQS
- Amazon SQS Dead-Letter Queue
- AWS Step Functions
- Amazon DynamoDB
- IAM
- Terraform

### Qualité

- Pytest
- Ruff
- uv

### Prévu

- API de revue humaine
- Interface opérateur
- GitHub Actions
- Observabilité et monitoring

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
- ✅ Adapter d'évaluation du risque via Amazon Bedrock
- ✅ Mapping vers `RiskAssessment`
- ✅ Composition Root
- ✅ Workflow d'analyse avec LangGraph
- ✅ Nodes et état LangGraph sérialisable
- ✅ Détermination du besoin de revue humaine
- ✅ Bucket d'entrée Amazon S3
- ✅ Pipeline événementiel S3 → SQS
- ✅ Dead-Letter Queue SQS
- ✅ Dispatcher Lambda
- ✅ Partial batch failure pour SQS
- ✅ Assessment Lambda
- ✅ Orchestration AWS Step Functions
- ✅ Branchement conditionnel avec un état `Choice`
- ✅ Persistance des évaluations dans Amazon DynamoDB
- ✅ IAM avec permissions dédiées aux composants
- ✅ Infrastructure AWS avec Terraform
- ✅ Tests unitaires du pipeline
- ✅ Validation end-to-end sur AWS jusqu'à DynamoDB

### En cours / prochaines étapes

- 🚧 Callback Human-in-the-loop avec Step Functions Task Token
- 🚧 API de validation opérateur
- 🚧 Interface minimaliste de revue humaine
- 🚧 Validation / rejet d'une évaluation
- 🚧 CI/CD avec GitHub Actions
- 🚧 Observabilité et monitoring
- 🚧 Sécurisation et durcissement de l'infrastructure

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

Cette séparation permet de ne pas déléguer au modèle génératif la détection initiale des comportements à risque.

### Human-in-the-loop

Le système est conçu pour assister un opérateur et non pour automatiser entièrement une décision sensible.

Les évaluations nécessitant une revue humaine sont explicitement identifiées par le workflow avant d'être dirigées vers la branche HITL.

### Séparation métier / infrastructure

Le domaine ne dépend ni d'AWS, ni de Bedrock, ni d'un modèle spécifique.

Les dépendances externes sont placées derrière des contrats applicatifs et connectées au système depuis le Composition Root.

Cette séparation permet de faire évoluer l'infrastructure sans modifier la logique métier centrale.

### Orchestration à plusieurs niveaux

LangGraph et AWS Step Functions répondent à deux responsabilités différentes.

```text
LangGraph
└── workflow d'analyse IA

AWS Step Functions
└── orchestration distribuée AWS / HITL
```

Cette séparation permet de conserver le workflow IA dans l'application tout en déléguant les traitements distribués et les attentes longues à l'orchestrateur cloud.

---

## Objectifs

Ce projet vise à démontrer la capacité à construire une application AI/backend combinant :

- expertise métier ;
- clean architecture ;
- développement Python typé ;
- architecture événementielle ;
- intégration AWS ;
- RAG ;
- LLM ;
- orchestration de workflows IA ;
- orchestration cloud ;
- Human-in-the-loop ;
- tests automatisés ;
- Infrastructure as Code ;
- observabilité ;
- pratiques CI/CD.

---

## Licence

MIT

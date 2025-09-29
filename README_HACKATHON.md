# 🏰 Château de Versailles - Assistant Conversationnel

Assistant intelligent pour les visiteurs du Château de Versailles avec interface de chat moderne et API d'évaluation.

## 🚀 Démarrage Rapide

### 1. Prérequis

- **Python 3.8+** avec pip
- **Node.js 16+** avec npm
- **Clé API Mistral** (configurée dans `.env`)
- **Ngrok** (pour l'évaluation)

### 2. Configuration

```bash
# Cloner et aller dans le projet
cd lumiereversailles

# Installer les dépendances Python
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec votre clé API Mistral
```

### 3. Lancement

#### Option A: Démarrage automatique
```bash
# Terminal 1: Backend
python start_backend.py

# Terminal 2: Frontend
python start_frontend.py

# Terminal 3: Ngrok (pour évaluation)
python setup_ngrok.py
```

#### Option B: Démarrage manuel
```bash
# Terminal 1: Backend
cd backend && python main.py

# Terminal 2: Frontend
cd frontend && npm install && npm start

# Terminal 3: Ngrok
ngrok http 8000
```

### 4. Accès

- **Chat Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Ngrok Dashboard**: http://127.0.0.1:4040

## 📋 Évaluation Hackathon

### Format API d'Évaluation

**Endpoint**: `POST /api/evaluate`

**Requête**:
```json
{
  "query": "On est à Paris avec deux enfants (7 et 10 ans), jamais venus à Versailles..."
}
```

**Réponse**:
```json
{
  "reponse": "Pour une première visite en famille à Versailles avec des enfants de 7 et 10 ans..."
}
```

### URL d'évaluation avec Ngrok

1. Lancez le backend: `python start_backend.py`
2. Lancez ngrok: `python setup_ngrok.py`
3. Récupérez l'URL publique: https://[id].ngrok.io
4. **URL d'évaluation**: `https://[id].ngrok.io/api/evaluate`

## 🏗️ Architecture

### Backend (FastAPI)
- **Agent Versailles**: Intelligence conversationnelle avec Mistral AI
- **API Chat**: Interface temps réel pour le frontend
- **API Évaluation**: Endpoint standardisé pour le hackathon
- **MCP Integration**: Outils météo et services externes

### Frontend (React + TypeScript)
- **Interface moderne**: Design responsive avec Tailwind CSS
- **Chat en temps réel**: Messages, suggestions, indicateurs de frappe
- **Gestion d'état**: Conversations persistantes côté client
- **API Integration**: Axios pour les appels backend

### Services
- **Mistral AI**: Modèle de langage principal
- **MCP Tools**: Outils météo et données externes
- **Ngrok**: Exposition publique pour évaluation

## 🛠️ Fonctionnalités

### Interface Chat
- ✅ **Design intuitif** avec thème Versailles
- ✅ **Suggestions rapides** pour commencer
- ✅ **Indicateurs visuels** (frappe, connexion)
- ✅ **Historique** des conversations
- ✅ **Responsive** mobile et desktop

### Agent Intelligent
- ✅ **Itinéraires personnalisés** selon profil visiteur
- ✅ **Informations pratiques** (billets, horaires, transport)
- ✅ **Météo temps réel** pour optimiser la visite
- ✅ **Recommandations familiales** adaptées aux enfants
- ✅ **Spots photo** et conseils pratiques

### Évaluation
- ✅ **API standardisée** selon cahier des charges
- ✅ **Format de réponse conforme** (`reponse` en français)
- ✅ **Gestion d'erreurs robuste** pour l'évaluation
- ✅ **Exposition Ngrok** pour tests externes

## 📊 Critères d'Évaluation

### Évaluation Qualitative (25%)
- **Intuitivité**: Interface claire et navigation fluide
- **Réactivité**: Temps de réponse < 3 secondes
- **Pertinence**: Questions et suggestions contextuelles
- **Itinéraires**: Recommandations personnalisées précises
- **Originalité**: Fonctionnalités innovantes (météo, profiling)

### Évaluation Quantitative (25%)
- **Précision**: Réponses conformes aux attentes expertes
- **Complétude**: Toutes informations requises présentes
- **Format**: Respect strict du format API d'évaluation

### Jury Final (50%)
- **Pertinence technique**: Architecture, choix technologiques
- **Innovation**: Approches originales (MCP, profiling automatique)
- **Complexité**: Agent intelligent, RAG, orchestration
- **Robustesse**: Stack solide, gestion d'erreurs
- **Présentation**: Clarté, démonstration efficace

## 🔧 Structure du Projet

```
lumiereversailles/
├── backend/                 # API FastAPI
│   └── main.py             # Serveur principal
├── frontend/               # Interface React
│   ├── src/
│   │   ├── components/     # Composants chat
│   │   ├── services/       # API calls
│   │   └── types/          # Types TypeScript
│   └── package.json
├── agents/                 # Agent intelligent
│   ├── core/              # Logique principale
│   ├── prompts/           # Instructions système
│   └── config/            # Configuration
├── start_backend.py       # Script démarrage backend
├── start_frontend.py      # Script démarrage frontend
├── setup_ngrok.py         # Configuration Ngrok
└── requirements.txt       # Dépendances Python
```

## 🎯 Points Forts

1. **Interface moderne et intuitive** avec design Versailles
2. **Agent intelligent** avec profiling automatique des visiteurs
3. **Intégration météo temps réel** pour optimiser les visites
4. **API robuste** conforme aux exigences d'évaluation
5. **Architecture modulaire** facilement extensible
6. **Scripts de démarrage automatisés** pour démonstration rapide

## 📱 Démonstration

### Scénarios Types
1. **Famille avec enfants**: Itinéraire adapté, activités ludiques
2. **Visiteur international**: Informations pratiques, transport
3. **Visite rapide**: Circuit express, incontournables
4. **Photographe**: Spots photo, conseils timing/lumière

### Fonctionnalités Innovantes
- **Profiling automatique** à partir du message utilisateur
- **Recommandations météo contextuelles**
- **Suggestions adaptatives** selon le profil
- **Interface conversationnelle naturelle**

---

*Développé pour le Hackathon "Les Clés de Versailles" - Équipe Assistant IA*
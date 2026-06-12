# Annexe B — Diagrammes UML

## B.1 Diagramme de cas d'utilisation

```mermaid
flowchart LR
    subgraph Acteurs
        G[Gérant]
        SYS[Système]
    end
    subgraph CyberCafé Manager
        UC1[Consulter tableau de bord]
        UC2[Démarrer session]
        UC3[Arrêter session]
        UC4[Consulter chronomètre]
        UC5[Générer ticket]
        UC6[Consulter statistiques journalières]
        UC7[Gérer tarifs]
        UC8[Configurer postes]
    end
    G --> UC1
    G --> UC2
    G --> UC3
    G --> UC4
    G --> UC5
    G --> UC6
    G --> UC7
    G --> UC8
    UC2 --> UC4
    UC3 --> UC5
    UC3 ..> UC2 : <<include>>
    UC5 ..> UC3 : <<include>>
    SYS --> UC4
```

**Acteur principal :** Gérant du cybercafé.  
**Acteur secondaire :** Système (chronomètre automatique).

---

## B.2 Diagramme de séquence — Démarrage de session

```mermaid
sequenceDiagram
    actor G as Gérant
    participant UI as Electron UI
    participant API as FastAPI
    participant SVC as SessionService
    participant DB as SQLite

    G->>UI: Sélectionne poste libre + tarif
    UI->>UI: Valide poste_id et tarif_code
    UI->>API: POST /sessions/start
    API->>API: Valider SessionStartIn (Pydantic)
    API->>SVC: demarrer(payload)
    SVC->>DB: Vérifier poste actif
    SVC->>DB: Vérifier absence session en_cours
    SVC->>DB: Récupérer tarif par code
    SVC->>DB: INSERT session (en_cours)
    DB-->>SVC: session_id
    SVC-->>API: SessionOut
    API-->>UI: 200 OK
    UI-->>G: Affiche poste occupé + chronomètre
```

---

## B.3 Diagramme de séquence — Arrêt de session et ticket

```mermaid
sequenceDiagram
    actor G as Gérant
    participant UI as Electron UI
    participant API as FastAPI
    participant SVC as SessionService
    participant PRC as Pricing (domain)
    participant DB as SQLite

    G->>UI: Clique poste occupé
    UI->>API: POST /sessions/stop
    API->>SVC: arreter(session_id)
    SVC->>DB: SELECT session en_cours
    SVC->>PRC: calculer_montant(duree, prix/h)
    SVC->>PRC: generer_numero_ticket(id)
    SVC->>DB: UPDATE session terminee
    DB-->>SVC: OK
    SVC-->>API: SessionOut
    API-->>UI: 200 OK
    UI->>API: GET /sessions/{id}/ticket
    API-->>UI: TicketOut
    UI-->>G: Affiche ticket de caisse
```

---

## B.4 Diagramme de classes

```mermaid
classDiagram
    class Poste {
        +int id
        +int numero
        +string libelle
        +bool actif
    }
    class Tarif {
        +int id
        +string code
        +string libelle
        +float prix_par_heure
    }
    class Session {
        +int id
        +int poste_id
        +int tarif_id
        +datetime debut
        +datetime fin
        +int duree_secondes
        +float montant
        +string statut
        +string numero_ticket
    }
    class SessionService {
        +demarrer(SessionStartIn)
        +arreter(SessionStopIn)
        +ticket(session_id)
    }
    class PosteRepository {
        +list_etat()
        +get_by_id()
        +has_active_session()
    }
    class SessionRepository {
        +create()
        +close()
        +stats_journalieres()
    }
    class Pricing {
        <<domain>>
        +calculer_montant()
        +generer_numero_ticket()
    }
    Poste "1" --> "*" Session
    Tarif "1" --> "*" Session
    SessionService --> PosteRepository
    SessionService --> SessionRepository
    SessionService --> TarifRepository
    SessionService --> Pricing
```

**Relations :** Un poste accueille plusieurs sessions (dans le temps). Un tarif s'applique à plusieurs sessions. Les services orchestrent les repositories ; la logique de calcul est isolée dans `Pricing` (domaine).

---

## B.5 Diagramme d'activités — Flux de gestion d'une session

```mermaid
flowchart TD
    A([Début]) --> B{Poste libre?}
    B -->|Non| C[Message: poste occupé]
    C --> Z([Fin])
    B -->|Oui| D[Sélection tarif]
    D --> E{Tarif valide?}
    E -->|Non| F[Erreur validation]
    F --> Z
    E -->|Oui| G[Créer session en_cours]
    G --> H[Afficher chronomètre]
    H --> I{Gérant arrête?}
    I -->|Non| H
    I -->|Oui| J[Calculer durée et montant]
    J --> K[Générer numéro ticket]
    K --> L[Persister session terminée]
    L --> M[Afficher ticket + MAJ stats]
    M --> Z
```

# Theme Enhancement Flowchart

```mermaid
flowchart TD
    A[Start: Enhanced Multilingual Request] --> B{Theme Parameter?}
    
    B -->|No| C[Original Workflow]
    B -->|Yes| D[Parse Theme Subparameters]
    
    C --> C1[Detect Informativeness]
    C1 --> C2{Informative?}
    C2 -->|No| C3[Return informative: 0, question: null]
    C2 -->|Yes| C4[Generate Question based on type]
    C4 --> C5[Return informative: 1, question: generated]
    
    D --> E[Extract Themes & Importance %]
    E --> F[Detect Informativeness]
    F --> G{Informative?}
    
    G -->|No| H[Return informative: 0, question: null]
    
    G -->|Yes| I[Analyze Response for Theme Matches]
    I --> J{Any Themes Found?}
    
    J -->|No| K[Generate Question: Why not mention important themes?]
    K --> L[Return informative: 1, question: theme-related]
    
    J -->|Yes| M[Find Theme with Highest Importance %]
    M --> N[Generate Question based on: Highest Theme + Type]
    N --> O[Return informative: 1, question: theme+type-based]
    
    style A fill:#e1f5fe
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#e8f5e8
    style K fill:#ffebee
    style N fill:#e8f5e8
    style O fill:#e8f5e8
```

## Request Structure

### When Theme = "No"
```json
{
  "question": "What challenges do you face at work?",
  "response": "I struggle with time management.",
  "type": "reason",
  "language": "English",
  "theme": "No"
}
```

### When Theme = "Yes"
```json
{
  "question": "What challenges do you face at work?",
  "response": "I struggle with time management and communication.",
  "type": "reason",
  "language": "English",
  "theme": "Yes",
  "theme_parameters": {
    "themes": [
      {"name": "leadership", "importance": 80},
      {"name": "communication", "importance": 60},
      {"name": "technology", "importance": 40}
    ]
  }
}
```

## Response Examples

### Scenario 1: Theme = "No"
```json
{
  "informative": 1,
  "question": "Why do you struggle with time management?",
  "original_question": "What challenges do you face at work?",
  "original_response": "I struggle with time management.",
  "type": "reason",
  "language": "English",
  "theme": "No"
}
```

### Scenario 2: Theme = "Yes", Theme Found
```json
{
  "informative": 1,
  "question": "How does your communication challenge affect team collaboration?",
  "original_question": "What challenges do you face at work?",
  "original_response": "I struggle with time management and communication.",
  "type": "reason",
  "language": "English",
  "theme": "Yes",
  "detected_theme": "communication",
  "theme_importance": 60
}
```

### Scenario 3: Theme = "Yes", No Theme Found
```json
{
  "informative": 1,
  "question": "Why do you think leadership skills weren't mentioned in your response?",
  "original_question": "What challenges do you face at work?",
  "original_response": "I struggle with time management.",
  "type": "reason",
  "language": "English",
  "theme": "Yes",
  "detected_theme": null,
  "highest_importance_theme": "leadership"
}
``` 
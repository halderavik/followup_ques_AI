# Theme Enhanced Optional API Flowchart

This Mermaid diagram illustrates the complete flow of the `/generate-theme-enhanced-optional` API endpoint, showing all decision points, processing paths, and response generation.

```mermaid
flowchart TD
    A[Client Request] --> B[POST /generate-theme-enhanced-optional]
    B --> C{Validate Request Body}
    
    C -->|Invalid| D[Return 422 Validation Error]
    C -->|Valid| E[Parse ThemeEnhancedOptionalRequest]
    
    E --> F{Theme = No?}
    
    F -->|Yes| G{check_informative = True?}
    F -->|No| H{check_informative = True?}
    
    G -->|False| I[Generate Multilingual Question]
    G -->|True| J[Detect Informativeness]
    
    I --> K[Return Standard Response]
    K --> L[informative: None, question: generated, explanation: None]
    
    J --> M{Response Informative?}
    M -->|No| N[Return Non-Informative Response]
    N --> O[informative: 0, question: None, explanation: None]
    
    M -->|Yes| P[Generate Multilingual Question]
    P --> Q[Return Standard Response]
    Q --> R[informative: 1, question: generated, explanation: None]
    
    H -->|False| S[Theme Analysis Only]
    H -->|True| T[Parallel Processing]
    
    S --> U[Detect Themes in Response]
    U --> V{Theme Found?}
    
    V -->|Yes| W[Generate Theme-Based Question]
    V -->|No| X[Find Highest Importance Theme]
    
    W --> Y[Return Theme-Based Response]
    Y --> Z[informative: None, question: generated, explanation: included, detected_theme: found, theme_importance: calculated]
    
    X --> AA[Generate Missing Theme Question]
    AA --> BB[Return Missing Theme Response]
    BB --> CC[informative: None, question: generated, explanation: included, highest_importance_theme: used]
    
    T --> DD[Parallel Tasks]
    DD --> EE[Task 1: Detect Informativeness]
    DD --> FF[Task 2: Detect Themes]
    
    EE --> GG[Wait for Both Results]
    FF --> GG
    
    GG --> HH{Response Informative?}
    
    HH -->|No| II[Return Non-Informative Response]
    II --> JJ[informative: 0, question: None, explanation: None]
    
    HH -->|Yes| KK{Theme Found?}
    
    KK -->|Yes| LL[Generate Theme-Based Question]
    KK -->|No| MM[Find Highest Importance Theme]
    
    LL --> NN[Return Theme-Based Response]
    NN --> OO[informative: 1, question: generated, explanation: included, detected_theme: found, theme_importance: calculated]
    
    MM --> PP[Generate Missing Theme Question]
    PP --> QQ[Return Missing Theme Response]
    QQ --> RR[informative: 1, question: generated, explanation: included, highest_importance_theme: used]
    
    %% Error Handling
    C -->|Exception| SS[Return 400 Bad Request]
    I -->|Error| TT[Return 502 OpenAI Error]
    J -->|Error| TT
    P -->|Error| TT
    U -->|Error| TT
    W -->|Error| TT
    X -->|Error| TT
    AA -->|Error| TT
    DD -->|Error| TT
    EE -->|Error| TT
    FF -->|Error| TT
    LL -->|Error| TT
    MM -->|Error| TT
    PP -->|Error| TT
    
    %% Styling
    classDef startEnd fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef response fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class A,B startEnd
    class F,G,H,M,V,HH,KK decision
    class C,E,I,J,P,S,U,W,X,AA,BB,DD,EE,FF,GG,LL,MM,PP,QQ process
    class D,K,L,N,O,Q,R,Y,Z,CC,II,JJ,NN,OO,RR response
    class SS,TT error
```

## Key Features of the Flow

### 1. **Request Validation**
- Validates `ThemeEnhancedOptionalRequest` model
- Checks required fields: `question`, `response`, `type`, `language`, `theme`, `check_informative`
- Validates `theme_parameters` when `theme="Yes"`

### 2. **Three Main Processing Paths**

#### **Standard Workflow** (`theme="No"`)
- Respects `check_informative` parameter
- Performs informativeness detection when `check_informative=true`
- Skips theme analysis (no theme parameters needed)
- Returns multilingual question with appropriate informative status

#### **Theme Analysis Only** (`check_informative=False`)
- Performs theme detection without informativeness check
- Generates theme-based or missing theme questions
- Sets `informative: None` in response

#### **Full Processing** (`check_informative=True`)
- Parallel processing of informativeness detection and theme analysis
- Early return for non-informative responses
- Generates appropriate questions based on theme detection results

### 3. **Theme Detection Logic**
- **Flexible Matching**: Exact words, partial matches, semantic relationships
- **Fallback String Matching**: Enhanced with semantic word mappings
- **Importance Ranking**: Uses theme importance percentages for decision making

### 4. **Response Generation**
- **Theme-Based Questions**: When themes are detected in the response
- **Missing Theme Questions**: When no themes are found, asks about highest importance theme
- **Standard Questions**: When theme analysis is disabled

### 5. **Error Handling**
- **Validation Errors**: 422 for invalid request data
- **Bad Request**: 400 for malformed requests
- **OpenAI Errors**: 502 for API service failures
- **Internal Errors**: 500 for unexpected server errors

### 6. **Performance Optimizations**
- **Parallel Processing**: Concurrent informativeness and theme detection
- **Caching**: Response caching for repeated requests
- **Connection Pooling**: Optimized HTTP session management
- **Fast Path**: Direct route for standard workflow

## Request/Response Examples

### Request Body
```json
{
  "question": "What is your experience with teamwork?",
  "response": "I enjoy working together with colleagues on projects.",
  "type": "reason",
  "language": "English",
  "theme": "Yes",
  "check_informative": false,
  "theme_parameters": {
    "themes": [
      {"name": "collaboration", "importance": 80},
      {"name": "communication", "importance": 60}
    ]
  }
}
```

### Response Body
```json
{
  "informative": null,
  "question": "What specific aspects of working together do you find most rewarding?",
  "explanation": "Generated a reason-based question focusing on the detected 'collaboration' theme...",
  "original_question": "What is your experience with teamwork?",
  "original_response": "I enjoy working together with colleagues on projects.",
  "type": "reason",
  "language": "English",
  "theme": "Yes",
  "check_informative": false,
  "detected_theme": "collaboration",
  "theme_importance": 80,
  "highest_importance_theme": null
}
``` 
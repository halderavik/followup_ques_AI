# Theme-Enhanced API Flowchart

This flowchart documents the complete flow of the `/generate-theme-enhanced` API endpoint, including the recent updates for 1-10 themes and highest importance theme selection.

```mermaid
flowchart TD
    A[Client Request] --> B[POST /generate-theme-enhanced]
    B --> C[Validate Request Body]
    
    C --> D{Valid Request?}
    D -->|No| E[Return 422 Validation Error]
    D -->|Yes| F[Extract Request Data]
    
    F --> G[Check Theme Parameter]
    G --> H{theme = "No"?}
    
    H -->|Yes| I[Standard Workflow]
    H -->|No| J[Theme Analysis Workflow]
    
    %% Standard Workflow Path
    I --> K[Detect Informativeness]
    K --> L{Informative?}
    L -->|No| M[Return Non-Informative Response]
    L -->|Yes| N[Generate Standard Question]
    N --> O[Return Standard Response]
    
    %% Theme Analysis Workflow Path
    J --> P{theme_parameters provided?}
    P -->|No| Q[Return 400 Error - Missing Parameters]
    P -->|Yes| R[Validate Theme Count 1-10]
    
    R --> S{Valid Theme Count?}
    S -->|No| T[Return 422 Validation Error]
    S -->|Yes| U[Detect Informativeness]
    
    U --> V{Informative?}
    V -->|No| W[Return Non-Informative Response]
    V -->|Yes| X[Detect Themes in Response]
    
    X --> Y{Theme Detected?}
    
    %% Theme Found Path
    Y -->|Yes| Z[Generate Theme-Based Question]
    Z --> AA[Return Theme-Based Response]
    
    %% No Theme Found Path
    Y -->|No| BB[Find Highest Importance Theme]
    BB --> HH[Generate Missing Theme Question]
    HH --> II[Return Missing Theme Response]
    
    %% Response Structure
    M --> JJ[Response: informative=0, question=null]
    O --> KK[Response: informative=1, question=text, theme="No"]
    W --> LL[Response: informative=0, question=null, theme="Yes"]
    AA --> MM[Response: informative=1, question=text, detected_theme=name, theme_importance=value]
    II --> NN[Response: informative=1, question=text, highest_importance_theme=name]
    
    %% Error Handling
    E --> OO[Error Response: validation_error]
    Q --> PP[Error Response: bad_request]
    T --> QQ[Error Response: validation_error]
    
    %% DeepSeek API Errors
    K --> RR{DeepSeek Error?}
    RR -->|Yes| SS[Return 502 DeepSeek Error]
    N --> TT{DeepSeek Error?}
    TT -->|Yes| UU[Return 502 DeepSeek Error]
    Z --> VV{DeepSeek Error?}
    VV -->|Yes| WW[Return 502 DeepSeek Error]
    HH --> XX{DeepSeek Error?}
    XX -->|Yes| YY[Return 502 DeepSeek Error]
    
    %% Styling
    classDef success fill:#d4edda,stroke:#155724,color:#155724
    classDef error fill:#f8d7da,stroke:#721c24,color:#721c24
    classDef process fill:#d1ecf1,stroke:#0c5460,color:#0c5460
    classDef decision fill:#fff3cd,stroke:#856404,color:#856404
    
    class JJ,KK,LL,MM,NN success
    class E,OO,PP,QQ,SS,UU,WW,YY error
    class B,C,F,G,I,J,K,N,P,R,U,X,Z,BB,HH process
    class D,H,L,P,S,V,Y,RR,TT,VV,XX decision
```

## Key Features Documented

### 1. **Theme Count Validation (1-10)**
- Validates that `theme_parameters.themes` contains between 1 and 10 themes
- Returns 422 validation error if count is outside this range

### 2. **Highest Importance Theme Selection**
- When no themes are detected in the response, the system finds the theme with the highest importance percentage
- The highest importance theme is used to generate a follow-up question about why it wasn't mentioned

### 3. **Two Main Workflows**
- **Standard Workflow** (`theme="No"`): Simple question generation without theme analysis
- **Theme Analysis Workflow** (`theme="Yes"`): Full theme detection and analysis

### 4. **Response Types**
- **Non-informative**: `informative=0`, no question generated
- **Standard**: `informative=1`, question generated, no theme data
- **Theme-based**: `informative=1`, question generated, includes `detected_theme` and `theme_importance`
- **Missing theme**: `informative=1`, question generated, includes `highest_importance_theme`

### 5. **Error Handling**
- Validation errors (422): Invalid request structure or theme count
- Bad request errors (400): Missing required parameters
- DeepSeek errors (502): External API failures
- Internal errors (500): Unexpected server errors

### 6. **Caching and Performance**
- All DeepSeek API calls are cached to improve performance
- Connection pooling with retry logic for reliability
- Timeout handling for external API calls

## Request/Response Structure

### Request
```json
{
  "question": "string",
  "response": "string", 
  "type": "string",
  "language": "string",
  "theme": "Yes" | "No",
  "theme_parameters": {
    "themes": [
      {
        "name": "string",
        "importance": 0-100
      }
    ]
  }
}
```

### Response
```json
{
  "informative": 0 | 1,
  "question": "string | null",
  "explanation": "string | null",
  "original_question": "string",
  "original_response": "string", 
  "type": "string",
  "language": "string",
  "theme": "Yes" | "No",
  "detected_theme": "string | null",
  "theme_importance": "number | null",
  "highest_importance_theme": "string | null"
}
``` 
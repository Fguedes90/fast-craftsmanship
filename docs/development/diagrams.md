# Diagramas com Mermaid

O Fast Craftsmanship suporta a criação de diagramas diretamente na documentação usando a sintaxe [Mermaid](https://mermaid-js.github.io/mermaid/).

## O que é Mermaid?

Mermaid é uma ferramenta baseada em JavaScript que permite gerar diagramas e fluxogramas a partir de descrições em texto, similar à forma como o Markdown funciona para criar documentos formatados.

## Tipos de Diagramas Suportados

### Fluxogramas (Flowcharts)

```mermaid
graph TD
    A[Início] --> B{É novo projeto?}
    B -->|Sim| C[Inicializar projeto]
    B -->|Não| D[Verificar estrutura]
    C --> E[Gerar arquivos]
    D --> E
    E --> F[Concluído]
```

### Diagramas de Sequência

```mermaid
sequenceDiagram
    participant U as Usuário
    participant C as CLI
    participant G as GitHub API
    
    U->>C: fcship github create-repo
    C->>U: Solicita nome do repo
    U->>C: Fornece nome
    C->>G: Cria repositório
    G->>C: Retorna resultado
    C->>U: Exibe confirmação
```

### Diagramas de Classe

```mermaid
classDiagram
    class Command {
        +name: str
        +execute(): Result
    }
    
    class GitHubCommand {
        +api_client: GitHubClient
        +create_repo(): Result
        +setup_workflows(): Result
    }
    
    class ProjectCommand {
        +template: str
        +create(): Result
        +validate(): Result
    }
    
    Command <|-- GitHubCommand
    Command <|-- ProjectCommand
```

### Diagramas de Estado

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing: execute()
    Processing --> Success: result.is_ok()
    Processing --> Failed: result.is_error()
    Success --> [*]
    Failed --> Idle: retry()
    Failed --> [*]: abort()
```

### Diagramas ER (Entidade-Relacionamento)

```mermaid
erDiagram
    PROJECT ||--o{ TEMPLATE : uses
    PROJECT {
        string name
        string path
        date created_at
    }
    TEMPLATE ||--|{ FILE : contains
    TEMPLATE {
        string name
        string type
        string description
    }
    FILE {
        string name
        string content
        string path
    }
```

### Diagramas Gantt

```mermaid
gantt
    title Plano de Implementação
    dateFormat  YYYY-MM-DD
    
    section Fase 1
    Implementação do CLI        :a1, 2023-01-01, 30d
    Comandos Básicos            :a2, after a1, 20d
    
    section Fase 2
    Integração com GitHub       :b1, after a2, 25d
    Testes Automatizados        :b2, after a1, 40d
    
    section Fase 3
    Documentação                :c1, after b1, 15d
    Lançamento v1.0             :milestone, after c1, 0d
```

### Diagramas de Jornada do Usuário

```mermaid
journey
    title Jornada do Usuário - Criação de Projeto
    section Instalação
      Instalar CLI: 5: Usuário
      Executar help: 5: Usuário
    section Uso
      Criar projeto: 3: Usuário
      Configurar GitHub: 4: Usuário
      Gerar estrutura: 5: Usuário
      Executar testes: 4: Usuário
    section Finalização
      Publicar código: 5: Usuário
```

### Diagramas de Arquitetura C4 (com Integração Mermaid)

```mermaid
graph TD
  subgraph Context
    FCSHIP["Fast Craftsmanship CLI"]
    PROJ["Projeto do Usuário"]
    GH["API do GitHub"]
    DOCKER["Docker"]
  end

  FCSHIP -->|"gerencia"| PROJ
  FCSHIP -->|"integra-se com"| GH
  FCSHIP -->|"configura"| DOCKER
```

## Como Usar Diagramas na Documentação

Para adicionar um diagrama Mermaid à documentação, utilize a sintaxe de código com o tipo `mermaid`:

````markdown
```mermaid
graph TD
    A[Início] --> B[Fim]
```
````

## Recomendações para Bons Diagramas

1. **Mantenha-os simples**: Diagramas devem ajudar a entender o conceito, não complicá-lo.
2. **Use cores com moderação**: Cores podem ajudar a destacar elementos importantes.
3. **Forneça legendas**: Explique o diagrama com texto antes ou depois dele.
4. **Consistência**: Mantenha um estilo consistente em todos os diagramas.
5. **Tamanho adequado**: Evite diagramas muito grandes que são difíceis de visualizar.

## Usando Diagramas para Documentar a Arquitetura do Fast Craftsmanship

Aqui está um exemplo de como usamos diagramas para documentar a arquitetura do Fast Craftsmanship:

```mermaid
graph TD
    CLI[CLI Interface] --> Commands
    
    subgraph "Command Layer"
        Commands --> GitHub
        Commands --> Project
        Commands --> Verify
    end
    
    subgraph "Service Layer"
        GitHub --> GitHubService
        Project --> ProjectService
        Verify --> VerifyService
    end
    
    subgraph "Infrastructure"
        GitHubService --> GitHubAPI
        ProjectService --> FileSystem
        VerifyService --> Linters
    end
    
    style CLI fill:#d0e0ff,stroke:#0066cc
    style Commands fill:#d0e0ff,stroke:#0066cc
    style GitHubService fill:#ffe0d0,stroke:#cc6600
    style ProjectService fill:#ffe0d0,stroke:#cc6600
    style VerifyService fill:#ffe0d0,stroke:#cc6600
```

## Documentação Railway Oriented Programming com Mermaid

Este é um exemplo de como podemos documentar o fluxo do Railway Oriented Programming (ROP) usando Mermaid:

```mermaid
graph LR
    classDef success fill:#b7eb8f,stroke:#135200
    classDef error fill:#ffa39e,stroke:#5c0011
    
    A[Entrada] --> B[Validação]
    B --> |"Ok(valor)"| C[Transformação]
    B --> |"Error(erro)"| E[Tratamento de Erro]
    C --> |"Ok(resultado)"| D[Resultado Final]
    C --> |"Error(erro)"| E
    E --> F[Log de Erro]
    D --> G[Sucesso]
    
    class D,G success
    class E,F error
```

Para mais informações sobre a sintaxe Mermaid, consulte a [documentação oficial do Mermaid](https://mermaid-js.github.io/mermaid/). 
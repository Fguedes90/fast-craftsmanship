"""Documentation commands for Fast Craftsmanship.

Este módulo contém comandos para gerenciar a documentação usando MkDocs.
"""
import subprocess

from pathlib import Path
from typing import Any

import questionary

from expression import Error, Ok, Result
from rich.console import Console

console = Console()

# Temas disponíveis para MkDocs Material
MATERIAL_THEMES = [
    "default",
    "slate",
    "material",
    "readthedocs",
    "mkdocs",
]

# Paletas de cores disponíveis
COLOR_SCHEMES = [
    "indigo",
    "red",
    "pink",
    "purple",
    "deep-purple",
    "blue",
    "light-blue",
    "cyan",
    "teal",
    "green",
    "light-green",
    "lime",
    "yellow",
    "amber",
    "orange",
    "deep-orange",
    "brown",
    "grey",
    "blue-grey",
]

# Plugins populares para MkDocs
AVAILABLE_PLUGINS = [
    "search",
    "mkdocstrings",
    "mkdocstrings-python",
    "autorefs",
    "git-revision-date-localized",
    "git-authors",
    "minify",
    "social",
    "glightbox",
    "macros",
    "table-reader",
    "redirects",
    "blog",
]

# Extensões populares para Markdown
MARKDOWN_EXTENSIONS = [
    "admonition",
    "pymdownx.highlight",
    "pymdownx.inlinehilite",
    "pymdownx.snippets",
    "pymdownx.superfences",
    "pymdownx.tabbed",
    "pymdownx.details",
    "footnotes",
    "attr_list",
    "def_list",
    "pymdownx.emoji",
    "pymdownx.tasklist",
    "toc",
]

def mkdocs_exists() -> bool:
    """Verifica se o arquivo mkdocs.yml já existe no projeto."""
    return Path("mkdocs.yml").exists()

def mkdocs_installed() -> Result[bool, str]:
    """Verifica se o MkDocs está instalado."""
    try:
        subprocess.run(["mkdocs", "--version"], check=True, capture_output=True)
        return Ok(True)
    except (subprocess.SubprocessError, FileNotFoundError):
        return Error("MkDocs não está instalado. Instale-o com 'pip install mkdocs mkdocs-material'")

def ensure_mkdocs_installed() -> Result[bool, str]:
    """Assegura que o MkDocs está instalado, ou tenta instalá-lo."""
    installed = mkdocs_installed()
    
    if hasattr(installed, "error"):
        console.print("[yellow]MkDocs não detectado. Tentando instalar...[/yellow]")
        try:
            subprocess.run(
                ["pip", "install", "mkdocs", "mkdocs-material", "mkdocstrings", "mkdocstrings-python"], 
                check=True
            )
            console.print("[green]MkDocs instalado com sucesso![/green]")
            return Ok(True)
        except subprocess.SubprocessError as e:
            return Error(f"Falha ao instalar MkDocs: {e}")
    
    return Ok(True)

def get_theme_config() -> dict[str, Any]:
    """Obtém as configurações de tema do usuário de forma interativa."""
    selected_theme = questionary.select(
        "Selecione o tema principal:",
        choices=["material", "mkdocs", "readthedocs"]
    ).ask()
    
    theme_config = {"name": selected_theme}
    
    if selected_theme == "material":
        features = questionary.checkbox(
            "Selecione os recursos do tema Material:",
            choices=[
                "navigation.instant",
                "navigation.tracking",
                "navigation.tabs",
                "navigation.sections",
                "navigation.expand",
                "navigation.indexes",
                "navigation.top",
                "toc.follow",
                "toc.integrate",
                "content.code.copy",
                "content.code.annotate",
                "search.highlight",
                "search.share",
            ]
        ).ask()
        
        primary_color = questionary.select(
            "Selecione a cor primária:",
            choices=COLOR_SCHEMES
        ).ask()
        
        accent_color = questionary.select(
            "Selecione a cor de destaque:",
            choices=COLOR_SCHEMES
        ).ask()
        
        theme_config.update({
            "features": features,
            "palette": [
                {
                    "media": "(prefers-color-scheme: light)",
                    "scheme": "default",
                    "primary": primary_color,
                    "accent": accent_color,
                    "toggle": {
                        "icon": "material/brightness-7",
                        "name": "Switch to dark mode"
                    }
                },
                {
                    "media": "(prefers-color-scheme: dark)",
                    "scheme": "slate",
                    "primary": primary_color,
                    "accent": accent_color,
                    "toggle": {
                        "icon": "material/brightness-4",
                        "name": "Switch to light mode"
                    }
                }
            ]
        })
        
        # Se deseja personalizar mais
        if questionary.confirm("Deseja personalizar mais o tema (fontes, ícones)?").ask():
            theme_config["font"] = {
                "text": questionary.select(
                    "Fonte para texto:",
                    choices=["Roboto", "Open Sans", "Lato", "Source Sans Pro"]
                ).ask(),
                "code": questionary.select(
                    "Fonte para código:",
                    choices=["Roboto Mono", "Source Code Pro", "Fira Mono", "JetBrains Mono"]
                ).ask()
            }
    
    return theme_config

def get_plugins_config() -> list[dict[str, Any]]:
    """Obtém as configurações de plugins do usuário de forma interativa."""
    selected_plugins = questionary.checkbox(
        "Selecione os plugins que deseja utilizar:",
        choices=AVAILABLE_PLUGINS
    ).ask()
    
    plugins_config = []
    
    # Sempre adiciona o plugin de busca se não foi selecionado
    if "search" not in selected_plugins:
        selected_plugins.append("search")
    
    for plugin in selected_plugins:
        if plugin == "mkdocstrings":
            plugins_config.append({
                "mkdocstrings": {
                    "default_handler": "python",
                    "handlers": {
                        "python": {
                            "selection": {
                                "docstring_style": "google",
                                "docstring_options": {
                                    "ignore_init_summary": True,
                                    "merge_init_into_class": True,
                                    "trim_doctest_flags": True
                                }
                            },
                            "rendering": {
                                "show_root_heading": True,
                                "show_root_full_path": True,
                                "show_source": True,
                                "show_signature": True,
                                "merge_init_into_class": True,
                                "docstring_section_style": "table"
                            }
                        }
                    }
                }
            })
        else:
            plugins_config.append(plugin)
    
    return plugins_config

def get_markdown_extensions() -> list[dict[str, Any]]:
    """Obtém as extensões markdown selecionadas pelo usuário."""
    extensions = questionary.checkbox(
        "Selecione as extensões Markdown que deseja ativar:",
        choices=MARKDOWN_EXTENSIONS
    ).ask()
    
    md_extensions = []
    
    # Configurações específicas para algumas extensões
    for ext in extensions:
        if ext == "pymdownx.superfences":
            md_extensions.append({
                "pymdownx.superfences": {
                    "custom_fences": [
                        {
                            "name": "mermaid",
                            "class": "mermaid",
                            "format": "!!python/name:pymdownx.superfences.fence_code_format"
                        }
                    ]
                }
            })
        elif ext == "pymdownx.highlight":
            md_extensions.append({
                "pymdownx.highlight": {
                    "anchor_linenums": True
                }
            })
        elif ext == "pymdownx.emoji":
            md_extensions.append({
                "pymdownx.emoji": {
                    "emoji_index": "!!python/name:material.extensions.emoji.twemoji",
                    "emoji_generator": "!!python/name:material.extensions.emoji.to_svg"
                }
            })
        elif ext == "pymdownx.tasklist":
            md_extensions.append({
                "pymdownx.tasklist": {
                    "custom_checkbox": True
                }
            })
        elif ext == "toc":
            md_extensions.append({
                "toc": {
                    "permalink": True
                }
            })
        else:
            md_extensions.append(ext)
    
    return md_extensions

def generate_mkdocs_yml(config: dict[str, Any]) -> str:
    """Gera o conteúdo do arquivo mkdocs.yml."""
    import yaml
    
    # Configuração para preservar a formatação em blocos
    class BlockDumper(yaml.SafeDumper):
        def represent_mapping(self, tag, mapping, _=None):
            return super().represent_mapping(tag, mapping, flow_style=False)
    
    # Configuração para formatar o output YAML
    yaml.add_representer(dict, BlockDumper.represent_mapping, Dumper=BlockDumper)
    
    # Converter para YAML
    return yaml.dump(config, sort_keys=False, Dumper=BlockDumper)

def generate_workflow_file() -> str:
    """Gera o conteúdo do workflow para GitHub Actions."""
    return """name: Documentation

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
      - '.github/workflows/docs.yml'
  pull_request:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
      - '.github/workflows/docs.yml'
  workflow_dispatch:

# Permissões necessárias para deploy no GitHub Pages
permissions:
  contents: write
  pages: write
  id-token: write
  deployments: write

# Configuração do ambiente para GitHub Pages
concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Fetch all history for proper versioning

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install mkdocs>=1.6.0 mkdocs-material>=9.6.7 
          pip install mkdocstrings>=0.29.0 mkdocstrings-python>=1.16.5 mkdocs-autorefs>=1.4.1
          pip install pillow cairosvg  # Para ícones SVG

      # Criar diretório de sobreposição do tema
      - name: Create theme override directory
        run: |
          mkdir -p docs/overrides
          touch docs/overrides/.gitkeep

      # Criar deployment no GitHub
      - name: Create GitHub deployment
        id: create_deployment
        uses: chrnorm/deployment-action@v2
        with:
          token: "${{ secrets.GITHUB_TOKEN }}"
          environment: github-pages
          initial-status: "in_progress"
          description: "Deployment of documentation for commit ${{ github.sha }}"
          ref: ${{ github.sha }}

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Build documentation
        run: |
          mkdocs build

      - name: Create .nojekyll file
        run: |
          touch site/.nojekyll
          echo "theme: material" > site/.mkdocs-material-theme
          
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: 'site'
          
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4

      # Atualizar o status do deployment
      - name: Update deployment status
        if: success()
        uses: chrnorm/deployment-status@v2
        with:
          token: "${{ secrets.GITHUB_TOKEN }}"
          deployment-id: ${{ steps.create_deployment.outputs.deployment_id }}
          state: "success"
          environment-url: ${{ steps.deployment.outputs.page_url }}

      # Em caso de falha, atualizar o status do deployment
      - name: Update deployment status (failure)
        if: failure()
        uses: chrnorm/deployment-status@v2
        with:
          token: "${{ secrets.GITHUB_TOKEN }}"
          deployment-id: ${{ steps.create_deployment.outputs.deployment_id }}
          state: "failure"
      
      # Criar uma tag de release para a documentação
      - name: Create Docs Tag
        if: success() && github.event_name != 'pull_request'
        run: |
          CURRENT_DATE=$(date '+%Y%m%d%H%M%S')
          TAG_NAME="docs-${CURRENT_DATE}"
          git config --global user.name "GitHub Actions"
          git config --global user.email "actions@github.com"
          git tag -a "${TAG_NAME}" -m "Documentation updated at ${CURRENT_DATE}"
          git push origin "${TAG_NAME}"
"""

def create_initial_docs_structure() -> None:
    """Cria a estrutura inicial de diretórios para documentação."""
    dirs = ["docs", "docs/assets", "docs/assets/images", "docs/assets/js", "docs/overrides"]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Criar arquivo index.md inicial
    index_content = """# Bem-vindo à Documentação

## Sobre este Projeto

Escreva aqui uma introdução ao seu projeto.

## Funcionalidades

- Lista de funcionalidades
- Recursos principais

## Instalação

```bash
pip install seu-pacote
```

## Uso Básico

```python
import seu_pacote

seu_pacote.fazer_algo()
```
"""
    
    with open("docs/index.md", "w") as f:
        f.write(index_content)

def create_mermaid_init_js() -> None:
    """Cria o arquivo de inicialização para Mermaid."""
    mermaid_init_content = """document.addEventListener('DOMContentLoaded', function() {
    mermaid.initialize({
        startOnLoad: true,
        theme: 'default',
        securityLevel: 'loose',
        flowchart: {
            useMaxWidth: true,
            htmlLabels: true,
            curve: 'basis'
        },
        sequence: {
            diagramMarginX: 50,
            diagramMarginY: 10,
            actorMargin: 100,
            height: 40
        },
        gantt: {
            titleTopMargin: 25,
            barHeight: 20,
            barGap: 4,
            topPadding: 50
        }
    });
});
"""
    
    with open("docs/assets/js/mermaid-init.js", "w") as f:
        f.write(mermaid_init_content)

def setup_docs(
    force_overwrite: bool = False,
    site_name: str | None = None,
    site_description: str | None = None,
    site_url: str | None = None,
    repo_url: str | None = None,
    theme: str | None = None,
    add_mermaid: bool = True,
    add_mkdocstrings: bool = True,
    setup_github_workflow: bool = False
) -> Result[str, str]:
    """Configura o MkDocs interativamente e cria a estrutura da documentação.
    
    Args:
        force_overwrite: Se True, sobrescreve configurações existentes sem perguntar
        site_name: Nome do site de documentação
        site_description: Descrição breve do site
        site_url: URL do site publicado
        repo_url: URL do repositório GitHub
        theme: Tema a ser usado ('material', 'mkdocs', 'readthedocs')
        add_mermaid: Se True, adiciona suporte para diagramas Mermaid
        add_mkdocstrings: Se True, adiciona plugin mkdocstrings para documentação de API
        setup_github_workflow: Se True, configura workflow de GitHub Actions
    
    Returns:
        Result contendo mensagem de sucesso ou erro
    """
    # Verificar se o MkDocs está instalado
    installed = ensure_mkdocs_installed()
    if hasattr(installed, "error"):
        return Error("Não foi possível instalar o MkDocs. Instale manualmente com 'pip install mkdocs mkdocs-material'.")
    
    # Verificar se já existe um arquivo mkdocs.yml
    if mkdocs_exists() and not force_overwrite:
        should_replace = questionary.confirm(
            "Arquivo mkdocs.yml já existe. Deseja substituí-lo?", default=False
        ).ask()
        
        if not should_replace:
            return Error("Operação cancelada pelo usuário.")
    
    # Coletar informações do projeto
    project_info = {}
    project_info["site_name"] = site_name or questionary.text(
        "Nome do site:", default="My Documentation"
    ).ask()
    
    project_info["site_description"] = site_description or questionary.text(
        "Descrição do site:", default="Documentation for my project"
    ).ask()
    
    # Adicionar URL do site se o usuário fornecer
    site_url_value = site_url or questionary.text(
        "URL do site (deixe em branco se não souber):", default=""
    ).ask()
    if site_url_value:
        project_info["site_url"] = site_url_value
    
    # Adicionar URL do repositório
    repo_url_value = repo_url or questionary.text(
        "URL do repositório GitHub (deixe em branco se não houver):", default=""
    ).ask()
    if repo_url_value:
        project_info["repo_url"] = repo_url_value
        project_info["repo_name"] = repo_url_value.split("github.com/")[-1] if "github.com/" in repo_url_value else ""
    
    # Configurações de tema
    theme_config = {"name": theme} if theme else get_theme_config()
    
    project_info["theme"] = theme_config
    
    # Configurações adicionais
    extras = []
    
    # Adicionar Mermaid se especificado ou se o usuário confirmar
    should_add_mermaid = add_mermaid
    if not add_mermaid and not force_overwrite:
        should_add_mermaid = questionary.confirm("Adicionar suporte a Mermaid para diagramas?").ask()
    
    if should_add_mermaid:
        extras.append("https://unpkg.com/mermaid@10.8.0/dist/mermaid.min.js")
        extras.append("assets/js/mermaid-init.js")
        create_mermaid_init_js()
    
    if extras:
        project_info["extra_javascript"] = extras
    
    # Plugins
    selected_plugins = []
    if not force_overwrite:
        selected_plugins = get_plugins_config()
    else:
        # Adicionar plugins padrão se for execução não interativa
        selected_plugins = ["search"]
        if add_mkdocstrings:
            selected_plugins.append({
                "mkdocstrings": {
                    "default_handler": "python",
                    "handlers": {
                        "python": {
                            "selection": {
                                "docstring_style": "google"
                            },
                            "rendering": {
                                "show_root_heading": True,
                                "show_source": True
                            }
                        }
                    }
                }
            })
    
    if selected_plugins:
        project_info["plugins"] = selected_plugins
    
    # Extensões Markdown
    if not force_overwrite:
        md_extensions = get_markdown_extensions()
        if md_extensions:
            project_info["markdown_extensions"] = md_extensions
    else:
        # Adicionar extensões padrão se for execução não interativa
        project_info["markdown_extensions"] = [
            "admonition",
            "pymdownx.highlight",
            "pymdownx.superfences",
            "footnotes",
            "toc"
        ]
        
        if should_add_mermaid:
            project_info["markdown_extensions"].append({
                "pymdownx.superfences": {
                    "custom_fences": [
                        {
                            "name": "mermaid",
                            "class": "mermaid",
                            "format": "!!python/name:pymdownx.superfences.fence_code_format"
                        }
                    ]
                }
            })
    
    # Criar estrutura inicial de diretórios
    create_initial_docs_structure()
    
    # Gerar mkdocs.yml
    mkdocs_content = generate_mkdocs_yml(project_info)
    with open("mkdocs.yml", "w") as f:
        f.write(mkdocs_content)
    
    # Perguntar se deseja criar o workflow do GitHub
    should_setup_workflow = setup_github_workflow
    if not setup_github_workflow and not force_overwrite:
        should_setup_workflow = questionary.confirm(
            "Deseja configurar o workflow de GitHub Actions para deploy da documentação?"
        ).ask()
    
    if should_setup_workflow:
        # Certificar-se de que o diretório existe
        workflow_dir = Path(".github/workflows")
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        # Criar o arquivo do workflow
        workflow_path = workflow_dir / "docs.yml"
        with open(workflow_path, "w") as f:
            f.write(generate_workflow_file())
        
        console.print("[green]Workflow de GitHub Actions configurado com sucesso![/green]")
    
    # Inicializar o MkDocs
    try:
        subprocess.run(["mkdocs", "build"], check=True)
    except subprocess.SubprocessError as e:
        console.print(f"[yellow]Aviso: Não foi possível construir a documentação: {e}[/yellow]")
    
    # Sucesso
    message = """
🎉 Documentação configurada com sucesso!

- Estrutura de diretórios criada em [bold]docs/[/bold]
- Arquivo de configuração [bold]mkdocs.yml[/bold] gerado
- Execute [bold]mkdocs serve[/bold] para visualizar a documentação localmente

Para saber mais sobre como usar o MkDocs, visite:
https://www.mkdocs.org/
    """
    
    return Ok(message)

def setup_command(
    force_overwrite: bool = False,
    site_name: str | None = None,
    site_description: str | None = None,
    site_url: str | None = None,
    repo_url: str | None = None,
    theme: str | None = None,
    add_mermaid: bool = True,
    add_mkdocstrings: bool = True,
    setup_github_workflow: bool = False
) -> Result[str, str]:
    """Comando para configurar a documentação interativamente.
    
    Args:
        force_overwrite: Se True, sobrescreve configurações existentes sem perguntar
        site_name: Nome do site de documentação
        site_description: Descrição breve do site
        site_url: URL do site publicado
        repo_url: URL do repositório GitHub
        theme: Tema a ser usado ('material', 'mkdocs', 'readthedocs')
        add_mermaid: Se True, adiciona suporte para diagramas Mermaid
        add_mkdocstrings: Se True, adiciona plugin mkdocstrings para documentação de API
        setup_github_workflow: Se True, configura workflow de GitHub Actions
    
    Returns:
        Result contendo mensagem de sucesso ou erro
    """
    try:
        return setup_docs(
            force_overwrite=force_overwrite,
            site_name=site_name,
            site_description=site_description,
            site_url=site_url,
            repo_url=repo_url,
            theme=theme,
            add_mermaid=add_mermaid,
            add_mkdocstrings=add_mkdocstrings,
            setup_github_workflow=setup_github_workflow
        )
    except Exception as e:
        return Error(f"Erro ao configurar a documentação: {e!s}")

def serve_docs(
    dev_addr: str = "127.0.0.1:8000",
    livereload: bool = True,
    dirtyreload: bool = False,
    strict: bool = False
) -> Result[str, str]:
    """Inicia o servidor de desenvolvimento do MkDocs.
    
    Args:
        dev_addr: Endereço e porta para o servidor (formato 'host:porta')
        livereload: Se True, ativa o recarregamento automático ao editar arquivos
        dirtyreload: Se True, ativa recarregamento mais rápido (pode ter inconsistências)
        strict: Se True, trata avisos como erros
    
    Returns:
        Result contendo mensagem de sucesso ou erro
    """
    if not mkdocs_exists():
        return Error("Arquivo mkdocs.yml não encontrado. Execute 'fcship docs setup' primeiro.")
    
    try:
        # Construir o comando com os argumentos fornecidos
        cmd = ["mkdocs", "serve"]
        
        if dev_addr != "127.0.0.1:8000":
            cmd.extend(["--dev-addr", dev_addr])
            
        if not livereload:
            cmd.append("--no-livereload")
            
        if dirtyreload:
            cmd.append("--dirtyreload")
            
        if strict:
            cmd.append("--strict")
        
        # Iniciar o servidor em um processo separado
        subprocess.Popen(cmd, shell=True)
        return Ok(f"Servidor MkDocs iniciado em http://{dev_addr}")
    except Exception as e:
        return Error(f"Erro ao iniciar o servidor MkDocs: {e!s}")

def build_docs(
    clean: bool = False,
    strict: bool = False,
    site_dir: str = "site",
    config_file: str | None = None,
    verbose: bool = False
) -> Result[str, str]:
    """Constrói a documentação para produção.
    
    Args:
        clean: Se True, remove arquivos antigos antes da construção
        strict: Se True, trata avisos como erros
        site_dir: Diretório onde os arquivos estáticos serão gerados
        config_file: Caminho para um arquivo de configuração alternativo
        verbose: Se True, exibe mensagens detalhadas durante a construção
    
    Returns:
        Result contendo mensagem de sucesso ou erro
    """
    if not mkdocs_exists() and not config_file:
        return Error("Arquivo mkdocs.yml não encontrado. Execute 'fcship docs setup' primeiro.")
    
    try:
        # Construir o comando com os argumentos fornecidos
        cmd = ["mkdocs", "build"]
        
        if clean:
            cmd.append("--clean")
            
        if strict:
            cmd.append("--strict")
            
        if site_dir != "site":
            cmd.extend(["--site-dir", site_dir])
            
        if config_file:
            cmd.extend(["--config-file", config_file])
            
        if verbose:
            cmd.append("--verbose")
        
        # Executar o comando
        subprocess.run(cmd, check=True)
        return Ok(f"Documentação construída com sucesso na pasta '{site_dir}/'")
    except Exception as e:
        return Error(f"Erro ao construir a documentação: {e!s}") 
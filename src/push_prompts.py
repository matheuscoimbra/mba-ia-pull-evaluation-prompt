"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()
client = Client()


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """Valida estrutura do prompt antes do push."""
    errors = []

    required_fields = ['version', 'description', 'created_at']
    for field in required_fields:
        if not prompt_data.get(field):
            errors.append(f"Campo obrigatório faltando: {field}")

    if not prompt_data.get("system_prompt", "").strip():
        errors.append("system_prompt está vazio")

    if not prompt_data.get("user_prompt", "").strip():
        errors.append("user_prompt está vazio")

    if "TODO" in prompt_data.get("system_prompt", ""):
        errors.append("system_prompt contém TODO")

    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(f"Mínimo 2 técnicas, encontradas: {len(techniques)}")

    return (len(errors) == 0, errors)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """Faz push do prompt otimizado para o LangSmith Hub (público)."""
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("Prompt inválido:")
        for err in errors:
            print(f"   - {err}")
        return False

    system_msg = prompt_data["system_prompt"].strip()
    user_msg = prompt_data.get("user_prompt", "{bug_report}").strip()

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", user_msg),
    ])

    tags = prompt_data.get("tags", [])
    techniques = prompt_data.get("techniques_applied", [])
    description = prompt_data.get("description", "")

    print(f"   Fazendo push: {prompt_name}")
    url = client.push_prompt(
        prompt_name,
        object=prompt_template,
        is_public=True,
        description=description,
        tags=tags + [f"technique:{t}" for t in techniques],
    )
    print(f"   Push realizado com sucesso >> {url}")

    return True


def main():
    print_section_header("PUSH DE PROMPTS OTIMIZADOS AO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    project_root = Path(__file__).parent.parent
    yaml_path = str(project_root / "prompts" / "bug_to_user_story_v2.yml")

    prompt_file = load_yaml(yaml_path)
    if not prompt_file:
        return 1

    prompt_data = prompt_file.get("bug_to_user_story_v2")
    if not prompt_data:
        print("Chave 'bug_to_user_story_v2' nao encontrada no YAML")
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB", "matheuscoimbra")
    prompt_name = f"{username}/bug_to_user_story_v2"

    if push_prompt_to_langsmith(prompt_name, prompt_data):
        print(f"\nPrompt publicado em: https://smith.langchain.com/hub/{prompt_name}")
        print(f"Tags: {prompt_data.get('tags', [])}")
        print(f"Tecnicas: {prompt_data.get('techniques_applied', [])}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())

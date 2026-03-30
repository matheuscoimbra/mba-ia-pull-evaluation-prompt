"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header
from langsmith import Client

load_dotenv()
client = Client()

def pull_prompts_from_langsmith() -> dict:

    prompt_name = "leonanluppi/bug_to_user_story_v1"
    print(f"Fazendo pull >> {prompt_name}")

    prompt = hub.pull(prompt_name)

    prompt_data = ""

    for msg in prompt.messages:
        template = msg.prompt.template if hasattr(msg, 'prompt') else str(msg)
        if msg.__class__.__name__ == "SystemMessagePromptTemplate":
            prompt_data = template

    print(f"   Prompt extraído com sucesso")
    return prompt_data


def main():
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    prompt_data = pull_prompts_from_langsmith()

    project_root = Path(__file__).parent.parent
    output_path = str(project_root / "prompts" / "raw_prompts.yml")
    if save_yaml(prompt_data, output_path):
        print(f"Prompt salvo em: {output_path}")
        return 0

    print("Falha ao salvar prompt")
    return 1


if __name__ == "__main__":
    sys.exit(main())

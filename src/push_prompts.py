"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

DICAS DE IMPLEMENTAÇÃO:

- O push é feito pelo cliente do LangSmith:

      from langsmith import Client
      from langchain_core.prompts import ChatPromptTemplate

      client = Client()
      prompt = ChatPromptTemplate.from_messages([
          ("system", system_prompt),
          ("user", user_prompt),
      ])
      url = client.push_prompt(
          f"{username}/bug_to_user_story_v2",
          object=prompt,
          is_public=True,
          description="...",
          tags=[...],
      )

- `username` vem de USERNAME_LANGSMITH_HUB no .env e precisa ser o seu handle
  do Hub. Se você ainda não tem um handle, veja as instruções no .env.example.

- A variável do template precisa ser {bug_report}, que é a chave de entrada
  usada no dataset de avaliação.

- Use `load_yaml` de utils.py para ler o arquivo .yml.
"""

import os
import sys

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

from utils import check_env_vars, load_yaml, print_section_header

load_dotenv()

def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    client = Client()
    
    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "")
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt),
    ])
    
    description = prompt_data.get("description", "Otimizado")
    tags = prompt_data.get("techniques_applied", [])
    
    try:
        url = client.push_prompt(
            prompt_name,
            object=prompt_template,
            is_public=True,
            description=description,
            tags=tags,
        )
        print(f"✅ Push realizado com sucesso! URL: {url}")
        return True
    except Exception as e:
        print(f"❌ Erro ao fazer push: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    from utils import validate_prompt_structure
    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""
    print_section_header("PUSH PROMPT DO LANGSMITH")
            
    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1
            
    username = os.getenv("USERNAME_LANGSMITH_HUB")
    
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "bug_to_user_story_v2.yml")
    prompt_data = load_yaml(prompt_path)
    
    if not prompt_data:
        print("❌ Erro ao carregar o prompt.")
        return 1
        
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Erros de validação:")
        for e in errors:
            print(f"- {e}")
        return 1
        
    prompt_name = f"{username}/bug_to_user_story_v2"
    if push_prompt_to_langsmith(prompt_name, prompt_data):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())

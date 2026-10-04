"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt semente do desafio
3. Salva localmente em prompts/bug_to_user_story_v1.yml

DICAS DE IMPLEMENTAÇÃO:

- O pull é feito pelo cliente do LangSmith:

      from langsmith import Client
      client = Client()
      prompt = client.pull_prompt(
          "leonanluppi/bug_to_user_story_v1",
          dangerously_pull_public_prompt=True,
      )

- O parâmetro `dangerously_pull_public_prompt=True` é obrigatório sempre que o
  identificador tem dono explícito ("owner/nome"). O LangSmith bloqueia esse pull
  por padrão porque um prompt do Hub é um objeto LangChain serializado, que pode
  vir de terceiros. Aqui o prompt é o do desafio, então o risco é conhecido.

- O retorno é um ChatPromptTemplate. Para extrair o conteúdo das mensagens,
  use a serialização nativa do LangChain (`prompt.messages`, e o atributo
  `.prompt.template` de cada mensagem).

- Use `save_yaml` de utils.py para gravar o resultado no arquivo .yml.
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client

from utils import check_env_vars, print_section_header, save_yaml

load_dotenv()

def pull_prompts_from_langsmith():
    print("Iniciando pull do prompt original...")
    
    # Conectando ao LangSmith
    client = Client()
    
    # Pull do prompt
    prompt = client.pull_prompt(
        "leonanluppi/bug_to_user_story_v1",
        dangerously_pull_public_prompt=True,
    )
    
    print("Prompt recuperado com sucesso!")
    
    # Extraindo dados
    prompt_data = {
        "version": "v1",
        "description": "Prompt original de baixa qualidade",
        "system_prompt": "",
        "user_prompt": ""
    }
    
    for msg in prompt.messages:
        class_name = type(msg).__name__
        if 'System' in class_name:
            prompt_data["system_prompt"] = msg.prompt.template
        elif 'Human' in class_name or 'User' in class_name:
            prompt_data["user_prompt"] = msg.prompt.template

    # Salva o yaml na pasta prompts
    output_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"
    save_yaml(prompt_data, str(output_path))
    print(f"Prompt salvo localmente em: {output_path}")


def main():
    """Função principal"""
    print_section_header("PULL PROMPT DO LANGSMITH")
    
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1
        
    try:
        pull_prompts_from_langsmith()
        return 0
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

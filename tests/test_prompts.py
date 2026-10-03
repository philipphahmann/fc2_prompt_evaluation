"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    @pytest.fixture(scope="class")
    def prompt_data(self):
        prompt_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
        return load_prompts(str(prompt_path))

    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' ausente no YAML."
        assert len(prompt_data["system_prompt"].strip()) > 0, "'system_prompt' está vazio."

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = prompt_data.get("system_prompt", "").lower()
        has_role = "você é" in system_prompt or "atuará como" in system_prompt or "você atuará" in system_prompt
        assert has_role, "Prompt não define a persona do LLM (ex: 'Você é um PM')."

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data.get("system_prompt", "").lower()
        has_format = "markdown" in system_prompt or "user story" in system_prompt
        assert has_format, "Prompt não exige saída em formato Markdown ou User Story explícita."

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data.get("system_prompt", "").lower()
        has_examples = "exemplo" in system_prompt or "few-shot" in system_prompt
        assert has_examples, "Prompt não parece conter exemplos explícitos de Few-Shot."

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        system_prompt = prompt_data.get("system_prompt", "")
        assert "TODO" not in system_prompt, "A string 'TODO' foi encontrada no prompt."

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied", [])
        assert isinstance(techniques, list) and len(techniques) >= 2, f"Esperado ao menos 2 técnicas em 'techniques_applied', encontradas {len(techniques)}."

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
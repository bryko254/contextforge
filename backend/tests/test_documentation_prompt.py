import unittest

from app.prompts.documentation_prompt import build_documentation_prompt


class DocumentationPromptTests(unittest.TestCase):
    def test_prompt_contains_required_schema_and_guardrails(self) -> None:
        prompt = build_documentation_prompt(
            project_summary={"project_name": "demo", "file_tree": ["README.md", "app/main.py"]},
            stack_summary={
                "languages": ["Python"],
                "frameworks": ["FastAPI"],
                "database": [],
                "infrastructure": [],
                "package_managers": ["pip"],
                "confidence_notes": ["Detected FastAPI from imports."],
            },
            selected_files=[
                {"path": "README.md", "content": "# Demo", "size": 6},
                {"path": "app/main.py", "content": "from fastapi import FastAPI", "size": 27},
            ],
        )

        self.assertIn('"readme": "...markdown..."', prompt)
        self.assertIn('"agent_md": "...markdown..."', prompt)
        self.assertIn('"setup": "...markdown..."', prompt)
        self.assertIn('"architecture": "...markdown..."', prompt)
        self.assertIn('"project_name_guess": "..."', prompt)
        self.assertIn("Do not invent dependencies", prompt)
        self.assertIn("Clearly mark uncertain assumptions", prompt)
        self.assertIn("future AI coding agents", prompt)
        self.assertIn("Include setup commands only when supported", prompt)
        self.assertIn("safe development rules", prompt)
        self.assertIn("README.md", prompt)
        self.assertIn("from fastapi import FastAPI", prompt)

    def test_prompt_truncates_large_file_content(self) -> None:
        prompt = build_documentation_prompt(
            project_summary={"project_name": "large"},
            stack_summary={},
            selected_files=[{"path": "huge.py", "content": "x" * 20_000, "size": 20_000}],
        )

        self.assertIn("...[truncated for prompt size]...", prompt)
        self.assertLess(len(prompt), 16_000)


if __name__ == "__main__":
    unittest.main()

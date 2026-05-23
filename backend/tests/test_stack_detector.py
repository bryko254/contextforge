import unittest

from app.services.stack_detector import detect_stack


class StackDetectorTests(unittest.TestCase):
    def test_detects_django_postgres_project(self) -> None:
        result = detect_stack(
            [
                {"path": "manage.py", "content": "from django.core.management import execute_from_command_line"},
                {
                    "path": "config/settings.py",
                    "content": "INSTALLED_APPS = []\nENGINE = 'django.db.backends.postgresql'\n",
                },
                {"path": "requirements.txt", "content": "Django\npsycopg[binary]\n"},
                {"path": "Dockerfile", "content": "FROM python:3.11\n"},
            ]
        )

        self.assertIn("Python", result.languages)
        self.assertIn("Django", result.frameworks)
        self.assertIn("PostgreSQL", result.database)
        self.assertIn("Docker", result.infrastructure)
        self.assertIn("pip", result.package_managers)
        self.assertTrue(any("Django" in note for note in result.confidence_notes))

    def test_detects_react_vite_typescript_tailwind_project(self) -> None:
        result = detect_stack(
            [
                {
                    "path": "package.json",
                    "content": '{"dependencies":{"react":"latest","vite":"latest","tailwindcss":"latest"},"devDependencies":{"typescript":"latest"}}',
                },
                {"path": "src/App.tsx", "content": "import React from 'react'; export function App() { return <div /> }"},
                {"path": "vite.config.ts", "content": "import { defineConfig } from 'vite';"},
                {"path": "tailwind.config.ts", "content": "export default {};"},
            ]
        )

        self.assertIn("Node.js", result.languages)
        self.assertIn("TypeScript", result.languages)
        self.assertIn("React", result.frameworks)
        self.assertIn("Vite", result.frameworks)
        self.assertIn("Tailwind", result.frameworks)
        self.assertIn("npm", result.package_managers)


if __name__ == "__main__":
    unittest.main()

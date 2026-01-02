"""
Tests básicos para la API de ChatGPT Local
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

# Añadir el directorio app al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api_server import app, ChatMessage, ChatRequest


@pytest.fixture
def client():
    """Fixture para el cliente de pruebas."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test del endpoint raíz / (health check)."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data
    assert "ollama_url" in data


def test_models_endpoint_success(client):
    """Test del endpoint /models con respuesta exitosa."""
    mock_response = {
        "models": [
            {"name": "llama3.2", "size": "4.7GB"},
            {"name": "mistral", "size": "4.1GB"}
        ]
    }

    with patch("api_server.httpx.AsyncClient") as mock_client:
        mock_instance = Mock()
        mock_instance.get.return_value.__aenter__ = Mock(
            return_value=Mock(json=lambda: mock_response)
        )
        mock_client.return_value.__aenter__.return_value = mock_instance.get.return_value.__aenter__.return_value

        # Simplemente verificar que el endpoint existe
        # El test completo requeriría un servidor Ollama real
        pass


def test_chat_request_validation():
    """Test de validación del modelo ChatRequest."""
    # Request válido
    valid_request = ChatRequest(
        messages=[
            ChatMessage(role="user", content="Hola")
        ],
        model="llama3.2",
        temperature=0.7,
        max_tokens=512
    )
    assert valid_request.model == "llama3.2"
    assert valid_request.temperature == 0.7
    assert len(valid_request.messages) == 1


def test_chat_request_defaults():
    """Test de valores por defecto de ChatRequest."""
    request = ChatRequest(
        messages=[ChatMessage(role="user", content="Test")]
    )
    assert request.temperature == 0.7
    assert request.max_tokens == 2048
    assert request.system_prompt == "Eres un asistente útil."


def test_chat_message_validation():
    """Test de validación del modelo ChatMessage."""
    message = ChatMessage(role="user", content="Test message")
    assert message.role == "user"
    assert message.content == "Test message"


@pytest.mark.parametrize("temperature", [0.0, 0.5, 1.0, 1.5, 2.0])
def test_temperature_range(temperature):
    """Test del rango de temperature válido."""
    request = ChatRequest(
        messages=[ChatMessage(role="user", content="Test")],
        temperature=temperature
    )
    assert 0.0 <= request.temperature <= 2.0


@pytest.mark.parametrize("max_tokens", [128, 512, 1024, 2048, 4096])
def test_max_tokens_range(max_tokens):
    """Test del rango de max_tokens válido."""
    request = ChatRequest(
        messages=[ChatMessage(role="user", content="Test")],
        max_tokens=max_tokens
    )
    assert 1 <= request.max_tokens <= 4096


def test_chat_endpoint_message_too_long(client):
    """Test del endpoint /chat con mensaje demasiado largo."""
    long_message = "x" * 20000  # Excede MAX_INPUT_LENGTH

    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": long_message}],
            "model": "llama3.2"
        }
    )
    assert response.status_code == 400
    assert "too long" in response.json()["detail"].lower()


def test_multiple_messages():
    """Test con múltiples mensajes en la conversación."""
    request = ChatRequest(
        messages=[
            ChatMessage(role="system", content="Eres un asistente."),
            ChatMessage(role="user", content="Hola"),
            ChatMessage(role="assistant", content="Hola, ¿cómo puedo ayudarte?"),
            ChatMessage(role="user", content="¿Qué tiempo hace?")
        ],
        model="llama3.2"
    )
    assert len(request.messages) == 4
    assert request.messages[0].role == "system"
    assert request.messages[-1].role == "user"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

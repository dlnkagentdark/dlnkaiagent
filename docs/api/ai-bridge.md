# AI Bridge API

**Version:** 1.0
**Last Updated:** December 25, 2025

## Overview

The AI Bridge is a central service that connects the dLNk IDE client to various backend AI providers. It handles request routing, authentication, and fallback logic, ensuring a seamless and reliable AI experience.

This service is composed of three main parts:
1.  **gRPC Client:** For high-performance communication with the primary Antigravity/Jetski endpoint.
2.  **WebSocket Server:** For real-time, bidirectional communication with the dLNk IDE extension.
3.  **REST API Server:** For standard HTTP-based interactions and management.

## WebSocket API

The WebSocket API is the primary method for the dLNk IDE extension to communicate with the AI Bridge.

- **Endpoint:** `ws://localhost:8765/chat`
- **Protocol:** WebSocket

### Connection

The client should establish a WebSocket connection to the endpoint. Once connected, it can send and receive JSON-formatted messages.

### Message Format

**Client to Server:**
```json
{
  "type": "chat.message",
  "payload": {
    "prompt": "Explain this Python code for me",
    "context": "def hello():\n  print(\"Hello, World!\")",
    "model": "default"
  }
}
```

**Server to Client (Streaming):**
```json
{
  "type": "chat.stream.chunk",
  "payload": {
    "chunk": "This Python code defines a function..."
  }
}
```

**Server to Client (Final):**
```json
{
  "type": "chat.stream.end",
  "payload": {
    "full_response": "This Python code defines a function named hello that prints the string \"Hello, World!\" to the console."
  }
}
```

## REST API

The REST API provides endpoints for status checks and configuration.

- **Base URL:** `http://localhost:8766/api/v1`

### Endpoints

#### `GET /status`

Checks the status of the AI Bridge and its connection to backend providers.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-12-25T18:30:00Z",
  "providers": {
    "antigravity": "connected",
    "gemini": "available",
    "openai": "available"
  }
}
```

#### `GET /config`

Retrieves the current configuration of the AI Bridge.

**Response:**
```json
{
  "fallback_enabled": true,
  "default_provider": "antigravity",
  "rate_limit": 100
}
```

## gRPC Communication

The AI Bridge communicates with the Antigravity/Jetski backend using gRPC over HTTP/2. This communication is handled internally and is not exposed directly to the client extension.

- **Service:** `exa.language_server_pb.LanguageServerService`
- **Method:** `SendUserCascadeMessage`
- **Encoding:** Binary Protobuf

## Authentication

All requests to the AI Bridge are authenticated via a token system managed by the `TokenManager`. The dLNk IDE extension receives a token upon successful license validation, which is then passed in the headers of WebSocket and REST API requests.

## Fallback System

The bridge includes a robust fallback system that automatically switches to a secondary provider if the primary Antigravity service is unavailable. The order of fallback is:

1.  Gemini
2.  OpenAI
3.  Groq
4.  Ollama (local)

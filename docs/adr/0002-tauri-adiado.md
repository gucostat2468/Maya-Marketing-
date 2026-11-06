# ADR 0002: Shell desktop Tauri adiado para a Fase 1.5

- **Status:** aceita
- **Data:** 2026-11-06

## Contexto

O Tauri empacota a interface como aplicativo Windows (WebView2). A Fase 1 foi construída em
um container Linux sem as bibliotecas de sistema do WebView, onde não é possível compilar
nem testar o shell. Além disso, distribuir o backend Python junto do Tauri exige empacotá-lo
como executável (*sidecar*, via PyInstaller), com riscos próprios: antivírus, tamanho,
inicialização e encerramento do processo.

## Decisão

Não incluir código Tauri não verificado. A interface já está preparada (`base: "./"` no Vite,
roteamento por hash, origens `tauri://localhost` liberadas no CORS). O shell será adicionado
e **testado no Windows** na Fase 1.5.

## Consequências

- Hoje a aplicação roda no navegador, apontando para o backend local (`scripts\dev.ps1`).
- Requisitos para a Fase 1.5: Rust (rustup), Microsoft C++ Build Tools, WebView2 (já vem no
  Windows 11) e PyInstaller para o *sidecar*.

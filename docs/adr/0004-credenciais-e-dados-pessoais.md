# ADR 0004: Credenciais no cofre do Windows; dados pessoais mascarados nos logs

- **Status:** aceita
- **Data:** 2026-11-06

## Decisão

- Tokens OAuth e chaves de API são gravados com `keyring`, que no Windows usa o
  **Gerenciador de Credenciais**. Nunca no banco, no código, no `.env`, nos logs ou no frontend.
- O backend só escuta em `127.0.0.1` e o CORS aceita apenas as origens da própria interface.
- Os logs passam por um filtro que mascara e-mail, telefone, CPF e valores de token.
- Real e demonstração ficam em arquivos de banco separados.

## Pendente (Fase 3, junto com leads)

Política de retenção configurável, exportação e exclusão de dados de um titular (LGPD), e
controle de acesso local (senha do aplicativo), se necessário.

# Registro de evidências — US-32 / SC-66

**Release 2 / Sprint 2.** A conferência manual foi concluída, conforme informado
pelo responsável. Os resultados automatizados estão registrados nos arquivos abaixo.

## Documentação

- [Roteiro dos testes manuais e automatizados](../../roteiro-testes-us32.md).
- [Relatório da execução, ambiente e rastreabilidade](../../relatorio-alinhamento-us32.md).

## Resultados automatizados

| Verificação | Resultado | Evidência |
| --- | --- | --- |
| Backend completo | 197 aprovados | [JUnit Pytest](automatizados/pytest-backend.xml) |
| US-32, incluída no backend completo | 42 aprovados | Mesmo JUnit; casos `test_us32_usuarios` |
| Proteção das fixtures E2E, incluída no backend completo | 6 aprovados | Mesmo JUnit; casos `test_seed_e2e` |
| Smoke — Chrome | 5 aprovados | [Resumo](automatizados/chrome-smoke-resumo.json) · [JUnit](automatizados/chrome-smoke-junit.xml) |
| Regressão — Chrome | 32 aprovados | [Resumo](automatizados/chrome-regressao-resumo.json) · [JUnit](automatizados/chrome-regressao-junit.xml) |
| Regressão — Electron | 32 aprovados | [Resumo](automatizados/electron-regressao-resumo.json) · [JUnit](automatizados/electron-regressao-junit.xml) |

Os subconjuntos da US-32 e das fixtures fazem parte dos 197 testes de backend.
As execuções nos dois navegadores cobrem os mesmos 12 critérios de aceite.

## Capturas

A pasta `automatizados/` contém 16 capturas selecionadas da execução no Chrome,
com os casos CT32–CT43 e os estados intermediários de confirmação, desativação
e bloqueio por vínculos. O relatório relaciona cada captura ao critério correspondente.

O [manifesto dos arquivos](automatizados/manifesto.json) lista os relatórios e
as imagens desta execução. Relatórios Cucumber completos e vídeos locais estão
em `frontend/artifacts/cypress/`.

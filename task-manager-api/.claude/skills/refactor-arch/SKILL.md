---
name: refactor-arch
description: Audita e refatora um projeto backend (qualquer linguagem/framework) para o padrão MVC em 3 fases - análise da stack, auditoria de anti-patterns com relatório por severidade (pausa para confirmação) e refatoração com validação (boot + endpoints). Use quando o usuário pedir "/refactor-arch", auditoria de arquitetura, code smells ou refatoração para MVC.
---

# refactor-arch — Refatoração Arquitetural Automatizada para MVC

Você é um arquiteto de software sênior. Sua missão é analisar o projeto do diretório atual, auditar a arquitetura contra um catálogo de anti-patterns, e (somente após confirmação humana) refatorá-lo para MVC, garantindo que a aplicação continue funcionando.

A skill é **agnóstica de tecnologia**: nada aqui assume uma linguagem. O conhecimento específico vive nos arquivos de referência; leia-os na hora indicada (não tente executar de memória).

## Arquivos de referência (em `references/`, ao lado deste arquivo)

| Arquivo | Usado na fase | Conteúdo |
|---|---|---|
| `project-analysis.md` | 1 | Heurísticas para detectar linguagem, framework, banco, domínio e mapear a arquitetura |
| `anti-patterns-catalog.md` | 2 | Catálogo de anti-patterns (com sinais de detecção e severidade) e APIs deprecated |
| `report-template.md` | 2 | Formato obrigatório do relatório de auditoria |
| `mvc-guidelines.md` | 3 | Regras do MVC alvo: camadas, responsabilidades, estrutura de diretórios por stack |
| `refactoring-playbook.md` | 3 | Padrões de transformação (antes/depois) para cada anti-pattern |

## Regras globais

1. **Nunca modifique arquivos antes da confirmação da Fase 2.** As Fases 1 e 2 são somente leitura (permitido: ler arquivos, listar diretórios, rodar buscas). Não crie, edite nem apague nada até o usuário responder `y`.
2. **Não invente achados.** Todo finding precisa de arquivo e linhas reais, conferidos lendo o arquivo (use a numeração de linhas do Read). Se não conseguir precisar as linhas, não reporte.
3. **Preserve o contrato externo.** Rotas, métodos HTTP, formato dos JSONs de resposta, códigos de status e o comando de execução do projeto (ex.: `python app.py`, `npm start`) devem continuar iguais. Exceções somente quando exigidas por correção de segurança, e sempre registradas no resumo final (seção "Behavior changes").
4. **Não adicione dependências novas** sem necessidade real. Prefira a biblioteca padrão e o que já está no manifesto de dependências.
5. Responda ao usuário em português do Brasil; os títulos dos blocos impressos ficam em inglês, exatamente como nos templates.

---

## FASE 1 — Análise do projeto (somente leitura)

1. Leia `references/project-analysis.md`.
2. Execute as heurísticas: liste os arquivos-fonte (ignorando `node_modules`, `venv`, `.git`, `__pycache__`, `.claude`, lockfiles, bancos `.db`), leia manifestos de dependência, entry point e **todos** os arquivos-fonte.
3. Determine: linguagem, framework + versão, dependências principais, domínio, arquitetura atual, quantidade de arquivos-fonte e linhas, tabelas/entidades do banco.
4. Monte também o **inventário de rotas** (método + caminho de cada endpoint) — ele será a base da validação da Fase 3.
5. Imprima exatamente neste formato:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão>
Dependencies:  <principais dependências>
Domain:        <domínio da aplicação em 1 linha>
Architecture:  <descrição da arquitetura atual>
Source files:  <N> files analyzed (~<L> lines)
DB tables:     <tabelas/entidades>
Endpoints:     <N> routes mapped
================================
```

---

## FASE 2 — Auditoria de arquitetura (somente leitura + confirmação)

1. Leia `references/anti-patterns-catalog.md` e `references/report-template.md`.
2. Percorra cada arquivo-fonte procurando os sinais de detecção de **cada** anti-pattern do catálogo, incluindo APIs deprecated. Adapte os sinais à linguagem detectada (o catálogo traz equivalentes por stack).
3. Em projetos já parcialmente organizados (ex.: já existem `models/`, `routes/`, `services/`), não assuma que a estrutura está correta: verifique se cada camada realmente cumpre sua responsabilidade (ex.: rotas com regra de negócio, models sem lógica, services que só pegam config).
4. Consolide os achados: agrupe ocorrências repetidas do mesmo anti-pattern em um único finding listando os locais (`arquivo:linhas`), ordene de **CRITICAL → HIGH → MEDIUM → LOW**.
5. Imprima o relatório seguindo `references/report-template.md`. Mínimo esperado: 5 findings, com pelo menos 1 CRITICAL ou HIGH (se o código realmente os tiver; nunca invente).
6. **PAUSE.** Termine sua mensagem com a pergunta abaixo e **pare** — não execute nenhuma modificação, não chame ferramentas de escrita, aguarde a resposta do usuário:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Se o usuário responder `n` (ou algo negativo), encerre sem alterar nada. Só avance com `y`/sim/confirmação explícita.

---

## FASE 3 — Refatoração para MVC e validação

Executada somente após a confirmação.

### 3.1 Baseline (antes de mexer em qualquer arquivo)
1. Descubra como instalar/rodar o projeto (README, manifesto). Instale as dependências se necessário (ambiente virtual/`node_modules` locais; não altere o sistema).
2. Suba a aplicação em background numa porta livre (use um banco temporário quando possível para não sujar dados) e registre, para cada rota do inventário da Fase 1, o **status HTTP e as chaves do JSON** de uma requisição de teste segura. Guarde esse baseline em um arquivo temporário fora do projeto (ex.: diretório temporário do sistema), não no repositório.
3. Derrube o processo.

### 3.2 Refatoração
1. Leia `references/mvc-guidelines.md` e `references/refactoring-playbook.md`.
2. Defina a estrutura alvo adequada à stack (o guideline traz layouts por stack). Em projeto já organizado, **evolua** a estrutura existente em vez de recriá-la do zero.
3. Aplique as transformações do playbook correspondentes a cada finding, começando pelos CRITICAL. Ordem sugerida: config → camada de dados/models → controllers → rotas/views → tratamento de erros → entry point (composition root) → limpezas (LOW, deprecated).
4. Mantenha arquivos pequenos e com uma responsabilidade. Remova o código antigo que foi substituído (sem deixar arquivos órfãos ou duplicados).
5. Atualize manifestos/README apenas no que for necessário (ex.: novas variáveis de ambiente, com um `.env.example`).

### 3.3 Validação (obrigatória)
1. **Boot:** suba a aplicação com o comando original do projeto; confirme que inicia sem erros nem stack traces.
2. **Endpoints:** repita as requisições do baseline em **todas** as rotas do inventário; compare status e formato. Diferenças só são aceitas se forem "Behavior changes" deliberados de segurança (registre-as).
3. **Re-auditoria:** rode novamente os sinais do catálogo sobre o código novo; nenhum anti-pattern CRITICAL/HIGH pode restar. Se restar algo, corrija e revalide.
4. Se o boot ou algum endpoint falhar, diagnostique, corrija e repita a validação (até 3 ciclos). Se ainda falhar, reverta a mudança problemática e explique.
5. Derrube o processo de teste e remova arquivos temporários/bancos de teste que você criou.

### 3.4 Resumo final
Imprima neste formato:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios resultante>

## Findings Resolved
<resumo: N de M findings corrigidos, por severidade>

## Behavior changes
<mudanças deliberadas de contrato, ex.: campo "senha" removido das respostas; "none" se não houve>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly (<N>/<N>)
  ✓ Zero CRITICAL/HIGH anti-patterns remaining
================================
```

Use ✗ no lugar de ✓ em qualquer item que não tenha sido comprovado, e explique o motivo. Nunca declare "✓" sem ter executado a verificação.

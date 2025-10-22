# Sistema de Seleção de Ambientes

## Visão Geral

O sistema agora suporta 3 ambientes diferentes que podem ser selecionados durante o login:

- **DEV** - Desenvolvimento
- **HOM** - Homologação (padrão)
- **PRD** - Produção

## Configuração dos Ambientes

As configurações dos ambientes estão definidas no arquivo `environment_config.py`:

```python
ENVIRONMENTS = {
    'DEV': {
        'name': 'Desenvolvimento',
        'database_url': 'postgresql+pg8000://user:pass@prod-host:5432/purchase_db',
        'description': 'Ambiente de desenvolvimento'
    },
    'HOM': {
        'name': 'Homologação',
        'database_url': 'postgresql+pg8000://zaza:Q1w2e3r4t5!@212.85.19.7:9090/purchase_db',
        'description': 'Ambiente de homologação'
    },
    'PRD': {
        'name': 'Produção',
        'database_url': 'postgresql+pg8000://dev:CaralhoAgoraFudeu!@34.234.136.242:9666/purchase_db?sslmode=disable',
        'description': 'Ambiente de produção'
    }
}
```

## Como Usar

### 1. Seleção de Ambiente no Login

- Acesse a página de login
- Selecione o ambiente desejado no dropdown "Ambiente"
- Digite suas credenciais
- Clique em "Entrar"

### 2. Troca de Ambiente Durante a Sessão

- Clique no seu nome de usuário no canto superior direito
- No menu dropdown, você verá a opção "Trocar Ambiente"
- Selecione o ambiente desejado
- O sistema irá reconectar automaticamente ao banco do novo ambiente

### 3. Indicador Visual

- O ambiente atual é exibido na navbar com uma cor específica:
  - **Verde**: Desenvolvimento
  - **Amarelo**: Homologação
  - **Vermelho**: Produção

## Funcionalidades Implementadas

### Arquivos Modificados/Criados:

1. **`environment_config.py`** - Configurações dos ambientes
2. **`config.py`** - Atualizado para suportar múltiplos ambientes
3. **`app/routes/auth.py`** - Lógica de autenticação com seleção de ambiente
4. **`app/templates/auth/login.html`** - Interface de login com seleção de ambiente
5. **`app/templates/base.html`** - Indicador visual e menu de troca de ambiente
6. **`app/__init__.py`** - Contexto de template para informações do ambiente

### Recursos:

- ✅ Seleção de ambiente no login
- ✅ Troca de ambiente durante a sessão
- ✅ Indicador visual do ambiente atual
- ✅ Validação de ambiente selecionado
- ✅ Tratamento de erros de conexão
- ✅ Limpeza de sessão no logout
- ✅ Interface responsiva e intuitiva

## Segurança

- O ambiente selecionado é armazenado na sessão do usuário
- Validação rigorosa dos ambientes disponíveis
- Tratamento de erros de conexão com o banco de dados
- Limpeza automática da sessão no logout

## Ambiente Padrão

O ambiente padrão é **HOM** (Homologação), conforme especificado nas configurações.

## Notas Técnicas

- O sistema reconecta automaticamente ao banco de dados quando o ambiente é alterado
- As configurações de banco são carregadas dinamicamente baseadas no ambiente selecionado
- A interface é atualizada em tempo real para refletir o ambiente atual

# Documentação do Módulo de Autenticação

## Visão Geral
O módulo de autenticação é responsável por gerenciar todo o processo de autenticação e autorização dos usuários na plataforma. Utiliza AWS Cognito como provedor de identidade principal, com uma camada adicional de gerenciamento de sessão usando Redis.

## Endpoints

### 1. Login
**Endpoint:** `/login`
**Método:** POST
**Descrição:** Realiza a autenticação do usuário no sistema.

**Payload:**
```json
{
    "username": "string",
    "password": "string"
}
```
**Headers:**
- Tenant URL é obtido automaticamente através do contexto global (g.tenant_url)

**Resposta de Sucesso:** Retorna os dados da sessão e configura cookies necessários

### 2. Logout
**Endpoint:** `/logout`
**Método:** POST
**Descrição:** Encerra a sessão do usuário
**Autenticação:** Requer token de acesso válido
**Headers Necessários:** Cookie 'session_id'

### 3. Alteração de Senha do Usuário
**Endpoint:** `/alterar-senha-usuario`
**Método:** POST
**Descrição:** Permite que um usuário autenticado altere sua senha

**Payload:**
```json
{
    "senha_atual": "string",
    "nova_senha": "string"
}
```
**Autenticação:** Requer token de acesso válido

### 4. Alteração de Senha Temporária
**Endpoint:** `/alterar-senha`
**Método:** POST
**Descrição:** Permite a alteração de senha temporária (primeiro acesso ou reset)

**Payload:**
```json
{
    "new_password": "string"
}
```
**Headers Necessários:** Cookie 'temp_session_id'

### 5. Reset de Senha com Código
**Endpoint:** `/reset-senha-esquecida`
**Método:** POST
**Descrição:** Permite redefinir a senha usando código de verificação

**Payload:**
```json
{
    "email": "string",
    "codigo": "string",
    "senha": "string"
}
```

### 6. Esqueci Senha
**Endpoint:** `/esqueci-senha`
**Método:** POST
**Descrição:** Inicia o processo de recuperação de senha

**Payload:**
```json
{
    "email": "string"
}
```

### 7. Obter Dados do Usuário
**Endpoint:** `/get-user`
**Método:** GET
**Descrição:** Retorna os dados do usuário logado
**Autenticação:** Requer token de acesso válido
**Headers Necessários:** Cookie 'session_id'

## Fluxos de Autenticação

### 1. Login Normal
1. Usuário envia credenciais
2. Sistema valida com AWS Cognito
3. Cria sessão no Redis
4. Retorna dados do usuário e cookies de sessão

### 2. Primeiro Acesso / Senha Temporária
1. Login inicial com senha temporária
2. Sistema identifica necessidade de troca de senha
3. Armazena sessão temporária no Redis
4. Usuário envia nova senha
5. Sistema atualiza credenciais e finaliza processo de login

### 3. Recuperação de Senha
1. Usuário solicita recuperação via email
2. Sistema envia código de verificação
3. Usuário confirma com código e nova senha
4. Sistema atualiza credenciais

## Segurança

### Middleware de Autenticação
- Decorator `@login_required()`: Valida sessão ativa
- Decorator `@role_required`: Valida permissões específicas

### Armazenamento de Sessão
- Utiliza Redis para gerenciamento de sessões
- Sessões têm tempo de expiração configurável
- Dados sensíveis são armazenados de forma segura

### Integração AWS Cognito
- Gerenciamento de usuários via AWS Cognito
- Políticas de senha configuráveis
- MFA disponível quando configurado

## Dependências
- Flask
- Redis
- AWS Cognito
- Serviços Internos:
  - AuthController
  - RedisService
  - Decorators de autenticação

## Observações Importantes

# Documentação do Módulo de Tenant

## Visão Geral
O módulo de Tenant é responsável por gerenciar as informações específicas de cada parceiro (tenant) no sistema multi-tenant. Ele permite identificar e recuperar informações do tenant com base na URL do subdomínio.

## Arquivos Relacionados
- **Route**: `tenant_route.py`
- **Service**: `parceiro_service.py`
- **Model**: `parceiro_model.py`

## Endpoints

### 1. Obter Informações do Tenant
**Endpoint:** `/get-tenant`
**Métodos:** GET, POST
**Descrição:** Recupera informações públicas do tenant baseado na URL do subdomínio.

#### Funcionamento
1. Obtém a URL do tenant através do contexto global do Flask (g.tenant_url)
2. Consulta as informações do parceiro usando o ParceiroService
3. Retorna informações públicas do tenant

#### Resposta de Sucesso (200 OK)
```json
{
    "nome": "string",
    "logo": "string"
}
```

#### Respostas de Erro
- **404 Not Found**
  - Quando o tenant_url não está presente no contexto
  ```json
  {
      "msg": "Requisição inválida 1"
  }
  ```
  - Quando o tenant não é encontrado no banco de dados
  ```json
  {
      "msg": "Requisição inválida 2"
  }
  ```

## Regras de Negócio
1. O sistema identifica o tenant através do subdomínio da URL
2. Cada tenant deve estar previamente cadastrado no sistema
3. Apenas informações públicas do tenant são expostas (nome e logo)
4. O endpoint é público e não requer autenticação

## Dependências
- **ParceiroService**: Serviço responsável por consultar informações do parceiro
- **Flask g object**: Usado para acessar o contexto global com informações do tenant
- **Blueprint**: Usado para organizar as rotas relacionadas ao tenant

## Observações Importantes
1. Este módulo é fundamental para o funcionamento do sistema multi-tenant
2. A URL do tenant deve ser configurada corretamente no ambiente de produção
3. O endpoint é utilizado principalmente para personalização da interface do usuário
4. As informações retornadas são utilizadas na customização visual da aplicação

## Exemplos de Uso

### Exemplo de Requisição
```http
GET https://tenant-name.domain.com/get-tenant
```

### Exemplo de Resposta Bem-Sucedida
```json
{
    "nome": "Empresa Parceira",
    "logo": "https://storage.domain.com/logos/empresa-parceira.png"
}
```

## Considerações de Segurança
1. O endpoint expõe apenas informações públicas do tenant
2. Não são expostos dados sensíveis ou configurações internas
3. O endpoint é acessível sem autenticação, mas possui validações de existência do tenant

## Integrações
- Sistema de armazenamento para logos
- Sistema de configuração de tenants
- Interface do usuário para customização baseada no tenant
1. Todas as senhas são validadas segundo política do Cognito
2. Sessões temporárias têm tempo de vida limitado
3. Tokens de acesso precisam ser renovados periodicamente
4. Sistema é multi-tenant, com validação por URL do tenant



# Documentação do Módulo de Fornecedor

## Visão Geral
O módulo de Fornecedor gerencia as operações relacionadas aos fornecedores no sistema, incluindo seleção de fornecedor para login, listagem, detalhamento e atualização de informações.

## Arquivos Relacionados
- **Route**: `fornecedor_route.py`
- **Controller**: `fornecedor_controller.py`
- **Model**: `fornecedor_model.py`
- **Controller Auxiliar**: `auth_controller.py`

## Endpoints

### 1. Seleção de Fornecedor para Login
**Endpoint:** `/select-fornecedor-login`
**Método:** POST
**Descrição:** Permite que um usuário do tipo Fornecedor selecione qual fornecedor deseja acessar.

**Autenticação:** 
- Requer login (`@login_required()`)
- Requer role 'Fornecedor' (`@role_required(['Fornecedor'])`)

**Query Parameters:**
```json
{
    "fornecedor_id": "number"
}
```

**Headers Necessários:**
- Cookie: 'session_id'

**Respostas:**
- **401 Unauthorized**: Sessão não encontrada
- **400 Bad Request**: Nenhum fornecedor selecionado

### 2. Listar Fornecedores
**Endpoint:** `/lista_fornecedor`
**Método:** GET
**Descrição:** Retorna lista paginada de fornecedores.

**Autenticação:**
- Requer login (`@login_required()`)
- Requer roles ['Administrador', 'ParceiroAdministrador', 'Parceiro']

**Query Parameters:**
```json
{
    "page": "number (default: 1)",
    "per_page": "number (default: 10)"
}
```

**Contexto Necessário:**
- g.user_data: Dados do usuário logado
- g.tenant_url: URL do tenant atual

**Resposta de Sucesso (200 OK):**
- Lista paginada de fornecedores

### 3. Detalhar Fornecedor
**Endpoint:** `/detalhe_fornecedor`
**Método:** GET
**Descrição:** Retorna informações detalhadas de um fornecedor específico.

**Autenticação:**
- Requer login (`@login_required()`)

**Query Parameters:**
```json
{
    "fornecedor_id": "number"
}
```

**Respostas:**
- **200 OK**: Detalhes do fornecedor
- **400 Bad Request**: ID do fornecedor não fornecido
- **404 Not Found**: Fornecedor não encontrado

### 4. Atualizar Fornecedor
**Endpoint:** `/update_fornecedor`
**Método:** PUT
**Descrição:** Atualiza informações de um fornecedor específico.

**Autenticação:**
- Requer login (`@login_required()`)

**Query Parameters:**
```json
{
    "fornecedor_id": "number"
}
```

**Body:** Dados do fornecedor a serem atualizados

**Respostas:**
- **400 Bad Request**: ID do fornecedor não fornecido
- Status code retornado pelo controller

## Regras de Negócio
1. Apenas usuários autenticados podem acessar as rotas
2. Diferentes níveis de acesso são requeridos para diferentes operações
3. A listagem de fornecedores é paginada
4. O acesso aos dados é filtrado pelo tenant atual
5. Fornecedores podem ter múltiplos vínculos, necessitando seleção específica no login

## Dependências
- **FornecedorController**: Lógica principal de negócio
- **AuthController**: Gerenciamento de autenticação
- **Decorators**: login_required, role_required
- **Flask g object**: Contexto global com dados do usuário e tenant

## Considerações de Segurança
1. Todas as rotas requerem autenticação
2. Validação de roles específicas para cada operação
3. Validação de tenant para garantir isolamento de dados
4. Verificação de propriedade/acesso aos dados do fornecedor

## Integrações
- Sistema de autenticação
- Sistema de gestão de tenant
- Banco de dados de fornecedores
- Sistema de controle de acesso baseado em roles

## Observações Importantes
1. O módulo é fundamental para o funcionamento do sistema multi-tenant
2. As operações são sempre contextualizadas ao tenant atual
3. O sistema suporta múltiplos vínculos de fornecedores
4. A seleção de fornecedor no login é necessária para casos específicos

# Documentação do Módulo de Fornecedor-Parceiro

## Visão Geral
O módulo de Fornecedor-Parceiro gerencia as relações entre fornecedores e parceiros, incluindo ativação/desativação de fornecedores e configuração de taxas (desconto e TAC) tanto em lote quanto individualmente.

## Arquivos Relacionados
- **Route**: `fornecedor_parceiro_route.py`
- **Controller**: `fornecedor_parceiro_controller.py`
- **Model**: `fornecedor_parceiro_model.py`

## Endpoints

### 1. Ativar/Desativar Fornecedor
**Endpoint:** `/ativa_desativa_fornecedor`
**Método:** POST
**Descrição:** Ativa ou desativa um fornecedor específico para um parceiro.

**Autenticação:**
- Requer login (`@login_required()`)
- Requer roles ['Administrador', 'Parceiro', 'ParceiroAdministrador']

**Query Parameters:**
```json
{
    "fornecedor_id": "number"
}
```

**Body:**
```json
{
    "habilitado": "boolean"
}
```

**Respostas:**
- **200 OK**: Operação realizada com sucesso
- **400 Bad Request**: Erro na operação

### 2. Atualizar Taxa de Desconto em Lote
**Endpoint:** `/update_taxa_desconto_lote_fornecedor`
**Método:** POST
**Descrição:** Atualiza a taxa de desconto para múltiplos fornecedores simultaneamente.

**Autenticação:**
- Requer login (`@login_required()`)
- Requer roles ['Administrador', 'Parceiro', 'ParceiroAdministrador']

**Body:** Dados das taxas de desconto em lote

**Respostas:**
- **200 OK**: Taxas atualizadas com sucesso
- **400 Bad Request**: Erro na atualização

### 3. Atualizar Taxa TAC em Lote
**Endpoint:** `/update_taxa_tac_lote_fornecedor`
**Método:** POST
**Descrição:** Atualiza a taxa TAC para múltiplos fornecedores simultaneamente.

**Autenticação:**
- Requer login (`@login_required()`)
- Requer roles ['Administrador', 'Parceiro', 'ParceiroAdministrador']

**Body:** Dados das taxas TAC em lote

**Respostas:**
- **200 OK**: Taxas atualizadas com sucesso
- **400 Bad Request**: Erro na atualização

### 4. Atualizar Taxa de Desconto Individual
**Endpoint:** `/update_taxa_desconto_individual_fornecedor`
**Método:** POST
**Descrição:** Atualiza a taxa de desconto para um fornecedor específico.

**Autenticação:**
- Requer login (`@login_required()`)
- Requer roles ['Administrador', 'Parceiro', 'ParceiroAdministrador']

**Body:** Dados da taxa de desconto individual

**Respostas:**
- **200 OK**: Taxa atualizada com sucesso
- **400 Bad Request**: Erro na atualização

### 5. Atualizar Taxa TAC Individual
**Endpoint:** `/update_taxa_tac_individual_fornecedor`
**Método:** POST
**Descrição:** Atualiza a taxa TAC para um fornecedor específico.

**Autenticação:**
- Requer login (`@login_required()`)
- Requer roles ['Administrador', 'Parceiro', 'ParceiroAdministrador']

**Body:** Dados da taxa TAC individual

**Respostas:**
- **200 OK**: Taxa atualizada com sucesso
- **400 Bad Request**: Erro na atualização

## Regras de Negócio
1. Apenas usuários autenticados com roles específicas podem gerenciar fornecedores
2. As operações são sempre contextualizadas ao tenant atual
3. Taxas podem ser atualizadas em lote ou individualmente
4. Cada operação requer validação de permissões do usuário
5. As alterações são registradas com o usuário que as realizou

## Contexto Necessário
Para todas as operações:
- g.user_data: Dados do usuário logado
- g.tenant_url: URL do tenant atual

## Considerações de Segurança
1. Todas as rotas requerem autenticação
2. Validação de roles específicas para cada operação
3. Validação de tenant para garantir isolamento de dados
4. Verificação de propriedade/acesso aos dados do fornecedor
5. Validação dos dados de entrada para taxas

## Integrações
- Sistema de autenticação e autorização
- Sistema de gestão de tenant
- Sistema de gestão de taxas
- Sistema de notificações (para mudanças de status)

## Observações Importantes
1. As taxas afetam diretamente as operações financeiras
2. Alterações em lote devem ser utilizadas com cautela
3. O sistema mantém histórico das alterações
4. As operações são atômicas para garantir consistência
5. Validações específicas são aplicadas para cada tipo de taxa

# Documentação do Módulo de Assinaturas (Contratos e Termos de Uso)

## Visão Geral
O módulo de Assinaturas gerencia os processos de assinatura de contratos de fornecedores e termos de uso da plataforma. Inclui funcionalidades para visualização e assinatura de documentos.

## Arquivos Relacionados
- **Routes**: 
  - `assinatura_termo_de_uso_route.py`
  - `assinatura_contrato_fornecedor_route.py`
- **Controllers**:
  - `AssinaturaTermoDeUsoController`
  - `AssinaturaContratoFornecedor`
  - `FornecedorController`
- **Templates**:
  - `email_termos_de_uso.html`
  - `contrato_fornecedor.html`

## Endpoints

### 1. Termos de Uso

#### 1.1 Obter Termos de Uso
**Endpoint:** `/get-termo`
**Método:** GET
**Descrição:** Retorna o HTML dos termos de uso da plataforma.

**Autenticação:**
- Requer login (`@login_required()`)

**Resposta:**
- **200 OK**: Retorna o HTML do template de termos de uso

#### 1.2 Assinar Termos de Uso
**Endpoint:** `/assina_termo`
**Método:** POST
**Descrição:** Registra a assinatura dos termos de uso pelo usuário.

**Autenticação:**
- Requer login (`@login_required()`)
- Requer roles ['Fornecedor', 'Parceiro']

**Headers Necessários:**
- Cookie: 'session_id'

**Respostas:**
- **200 OK**: Assinatura registrada com sucesso
- **400 Bad Request**: Erro no processo de assinatura
- **401 Unauthorized**: Usuário inválido

### 2. Contrato de Fornecedor

#### 2.1 Obter Contrato
**Endpoint:** `/get-contrato`
**Método:** GET
**Descrição:** Retorna o HTML do contrato do fornecedor.

**Autenticação:**
- Requer login (`@login_required()`)
- Requer role ['Fornecedor']

**Contexto Necessário:**
- Fornecedor selecionado no user_data

**Respostas:**
- **200 OK**: Retorna o HTML do contrato personalizado
- **400 Bad Request**: Fornecedor não selecionado ou não encontrado

#### 2.2 Assinar Contrato de Fornecedor
**Endpoint:** `/assina_contrato_fornecedor`
**Método:** POST
**Descrição:** Registra a assinatura do contrato pelo fornecedor.

**Autenticação:**
- Requer login (`@login_required()`)
- Requer role ['Fornecedor']

**Headers Necessários:**
- Cookie: 'session_id'

**Respostas:**
- **200 OK**: Assinatura registrada com sucesso
- **400 Bad Request**: Erro no processo de assinatura
- **401 Unauthorized**: Usuário ou fornecedor inválido

## Regras de Negócio

### Termos de Uso
1. Podem ser assinados por Fornecedores e Parceiros
2. A assinatura é única por usuário
3. O sistema mantém registro da data e hora da assinatura
4. A assinatura é vinculada ao tenant atual

### Contrato de Fornecedor
1. Exclusivo para usuários com role Fornecedor
2. Requer fornecedor selecionado no contexto do usuário
3. Contrato é personalizado com dados do fornecedor
4. A assinatura é vinculada ao fornecedor específico

## Considerações de Segurança
1. Todas as rotas requerem autenticação
2. Validação de roles específicas para cada operação
3. Verificação de contexto do tenant
4. Validação de propriedade do fornecedor
5. Registro seguro das assinaturas

## Fluxo de Assinatura
1. Usuário visualiza o documento (termos ou contrato)
2. Sistema valida permissões e contexto
3. Usuário confirma a assinatura
4. Sistema registra a assinatura com:
   - Data e hora
   - Identificação do usuário
   - Contexto do tenant
   - Versão do documento

## Integrações
- Sistema de autenticação
- Sistema de gestão de tenant
- Sistema de templates
- Sistema de registro de assinaturas
- Sistema de gestão de fornecedores

## Observações Importantes
1. Os documentos são renderizados dinamicamente
2. As assinaturas são legalmente vinculantes
3. O sistema mantém histórico completo das assinaturas
4. Os templates podem ser personalizados por tenant
5. As assinaturas são pré-requisito para certas operações no sistema

# Documentação do Módulo de Upload 

## Visão Geral
O módulo de Upload gerencia o carregamento de dados para o sistema através de diferentes métodos: formulário, arquivo CSV e JSON. Oferece funcionalidades para processar dados de parceiros e cedentes, com suporte a diferentes tipos de documentos e formatos.

## Arquivos Relacionados
- **Routes**: `upload_route.py`
- **Controllers**: `upload_controller.py`
- **Services**: `quadro_alerta_service.py`

## Endpoints

### 1. Upload via Formulário
**Endpoint:** `/upload-form`
**Método:** POST
**Descrição:** Processa dados enviados através de formulário estruturado.

**Autenticação:**
- Requer login (`@login_required()`)
- Requer roles ['ParceiroAdministrador', 'Administrador', 'Parceiro']

**Payload (JSON):**
```json
{
  "cnpj_sacado": "string",
  "email_sacado": "string",
  "sacado": "string",
  "socio_representante": "string",
  "cpf_representante": "string",
  "email_representante": "string",
  "telefone": "string",
  "razao_social": "string",
  "nome_fantasia": "string",
  "cpf_cnpj": "string",
  "email": "string",
  "endereco": "string",
  "numero": "string",
  "complemento": "string",
  "bairro": "string",
  "cep": "string",
  "municipio": "string",
  "uf": "string",
  "bco": "string",
  "agencia": "string",
  "conta": "string",
  "tipo_chave": "string",
  "chavepix": "string",
  "documento": "string",
  "tipo_doc": "string",
  "titulo": "string",
  "dt_emis": "string",
  "dt_fluxo": "string",
  "vlr_face": "number",
  "parcelas": "number"
}
```

**Respostas:**
- **200 OK**: Upload processado com sucesso
- **400 Bad Request**: Dados inválidos
- **500 Internal Server Error**: Erro no processamento

### 2. Upload de Arquivo
**Endpoint:** `/upload`
**Método:** POST
**Descrição:** Processa upload de arquivos CSV.

**Autenticação:**
- Requer login (`@login_required()`)
- Requer roles ['ParceiroAdministrador', 'Administrador', 'Parceiro']

**Formato:** Multipart Form Data
**Tipo de Arquivo:** CSV

**Respostas:**
- **200 OK**: Arquivo processado com sucesso
- **400 Bad Request**: Arquivo inválido
- **500 Internal Server Error**: Erro no processamento

### 3. Upload via JSON
**Endpoint:** `/upload-json`
**Método:** POST
**Descrição:** Processa dados enviados em formato JSON.

**Autenticação:**
- Requer login (`@login_required()`)
- Requer roles ['ParceiroAdministrador', 'Administrador', 'Parceiro']

**Headers:**
- Content-Type: application/json

**Payload:**
```json
{
  "data": [
    {
        "cnpj_sacado": "string",
        "email_sacado": "string",
        "sacado": "string",
        "socio_representante": "string",
        "cpf_representante": "string",
        "email_representante": "string",
        "telefone": "string",
        "razao_social": "string",
        "nome_fantasia": "string",
        "cpf_cnpj": "string",
        "email": "string",
        "endereco": "string",
        "numero": "string",
        "complemento": "string",
        "bairro": "string",
        "cep": "string",
        "municipio": "string",
        "uf": "string",
        "bco": "string",
        "agencia": "string",
        "conta": "string",
        "tipo_chave": "string",
        "chavepix": "string",
        "documento": "string",
        "tipo_doc": "string",
        "titulo": "string",
        "dt_emis": "string",
        "dt_fluxo": "string",
        "vlr_face": "number",
        "parcelas": "number"
    }
  ]
}
```

**Respostas:**
- **200 OK**: Dados processados com sucesso
- **400 Bad Request**: JSON inválido
- **500 Internal Server Error**: Erro no processamento

### 4. Consulta Status do Upload
**Endpoint:** `/get-status-upload`
**Método:** GET
**Descrição:** Consulta o status de um upload específico.

**Parâmetros Query:**
- `id`: ID do quadro alerta (obrigatório)

**Resposta (200 OK):**
```json
{
  "id": "number",
  "texto": "string",
  "dados_extras": "object",
  "titulo": "string",
  "tipo": "string"
}
```

**Respostas:**
- **200 OK**: Status recuperado com sucesso
- **400 Bad Request**: ID não fornecido

## Regras de Negócio

### 1. Processamento de Fornecedores e Operações

#### Fluxo de Cadastro
1. **Identificação do Fornecedor:**
   - Sistema verifica a existência do fornecedor pelo CNPJ/CPF
   - Se não existir, um novo fornecedor é cadastrado
   - Se existir, utiliza o fornecedor encontrado

2. **Criação/Vinculação de Operações:**
   - Para cada registro processado, uma nova operação é criada
   - A operação é automaticamente vinculada ao fornecedor correspondente
   - Múltiplas operações podem ser vinculadas ao mesmo fornecedor

#### Dados do Fornecedor
- **Informações Básicas:**
  - Razão Social
  - Nome Fantasia
  - CNPJ/CPF
  - Email
  - Telefone
  - Endereço completo

- **Informações Bancárias:**
  - Banco
  - Agência
  - Conta
  - Tipo de Chave PIX
  - Chave PIX

#### Dados da Operação
- **Informações do Documento:**
  - Tipo de documento
  - Número do documento
  - Título
  - Data de emissão
  - Data do fluxo
  - Valor face
  - Número de parcelas

- **Informações do Sacado:**
  - CNPJ do sacado
  - Email do sacado
  - Nome do sacado
  - Dados do representante

### 2. Tipos de Upload e Processamento

#### Upload via CSV
1. **Formato do Arquivo:**
   - Arquivo CSV com cabeçalho
   - Codificação esperada: UTF-8
   - Separador padrão: vírgula (,)

2. **Processamento:**
   - Leitura linha a linha
   - Validação dos dados obrigatórios
   - Criação/atualização de fornecedores
   - Criação de operações

#### Upload via JSON
1. **Estrutura do Payload:**
   - Array de objetos contendo dados de fornecedores e operações
   - Cada objeto representa uma operação completa

2. **Processamento:**
   - Validação do schema JSON
   - Processamento em lote
   - Criação/atualização de fornecedores
   - Criação de operações

#### Upload via Formulário
1. **Dados do Formulário:**
   - Interface web para entrada manual
   - Validação em tempo real
   - Processamento individual

2. **Processamento:**
   - Validação dos campos
   - Criação/atualização do fornecedor
   - Criação da operação

### 3. Monitoramento e Status

#### Quadro de Alertas
- Registra o progresso do processamento
- Armazena informações sobre:
  - Quantidade de registros processados
  - Fornecedores criados/atualizados
  - Operações criadas
  - Erros encontrados

#### Status de Processamento
- Em fila
- Processando
- Concluído
- Erro

### 4. Validações e Restrições

#### Validações de Dados
- CNPJ/CPF válido
- Email em formato correto
- Datas em formato válido
- Valores numéricos para campos monetários

#### Restrições de Negócio
- Fornecedor deve ter dados bancários completos
- Operações devem ter documento associado
- Valores não podem ser negativos
- Datas de fluxo devem ser futuras

## Observações Técnicas

1. **Integração com Outros Módulos:**
   - Sistema de Fornecedores
   - Sistema de Operações
   - Sistema de Alertas
   - Sistema de Validação

2. **Persistência:**
   - Transacional
   - Rollback em caso de erro
   - Registro de logs de alteração

3. **Performance:**
   - Processamento assíncrono para grandes volumes
   - Controle de concorrência
   - Cache de fornecedores existentes

## Recomendações de Uso

1. **Para Grandes Volumes:**
   - Preferir upload via CSV
   - Dividir arquivos muito grandes
   - Acompanhar status via quadro de alertas

2. **Para Operações Individuais:**
   - Utilizar o formulário web
   - Verificar feedback imediato
   - Confirmar dados antes do envio


# Documentação do Endpoint de Arquivo Retorno

## Visão Geral
O endpoint `/arquivo_retorno` é responsável por gerar um arquivo CSV contendo informações consolidadas das operações financeiras, permitindo a integração com sistemas externos e controle financeiro.

## Especificação do Endpoint

### Rota
**Endpoint:** `/arquivo_retorno`
**Método:** GET
**Controller:** `fornecedor_nota_route.py`

### Autenticação e Autorização
- Requer autenticação (`@login_required()`)
- Requer uma das seguintes roles:
  - Administrador
  - Parceiro
  - ParceiroAdministrador

### Parâmetros
O endpoint utiliza dados do contexto global:
- `usuario_logado` (g.user_data)
- `tenant_url` (g.tenant_url)

### Respostas

#### Sucesso (200 OK)
Retorna um arquivo CSV com as seguintes características:
- Content-Type: text/csv
- Charset: UTF-8
- Content-Disposition: attachment; filename="arquivo_retorno_{data}.csv"

#### Erro (400 Bad Request)
```json
{
    "msg": "Mensagem de erro específica"
}
```

## Funcionalidade

### Geração do Arquivo
1. **Coleta de Dados**
   - Busca operações financeiras baseadas no tenant atual
   - Filtra dados conforme permissões do usuário
   - Consolida informações relevantes para o retorno

2. **Formatação do CSV**
   - Utiliza a função `gera_retorno_csv` do módulo `arquivo_retorno.py`
   - Processa os dados em formato tabular
   - Aplica formatações específicas para campos monetários e datas

### Estrutura do Arquivo CSV
O arquivo gerado contém as seguintes informações:

#### Cabeçalho
```csv
Data,Título,Fornecedor,CNPJ,Valor,Status,Data Vencimento
```

#### Campos
1. **Data**: Data da operação (formato DD/MM/YYYY)
2. **Título**: Identificador único da operação
3. **Fornecedor**: Razão social do fornecedor
4. **CNPJ**: CNPJ do fornecedor
5. **Valor**: Valor da operação em formato monetário
6. **Status**: Status atual da operação
7. **Data Vencimento**: Data de vencimento (formato DD/MM/YYYY)

### Regras de Negócio

1. **Filtros de Dados**
   - Dados são filtrados pelo tenant atual
   - Apenas operações autorizadas são incluídas
   - Respeita hierarquia de permissões do usuário

2. **Formatação**
   - Valores monetários seguem padrão brasileiro
   - Datas no formato DD/MM/YYYY
   - Encoding UTF-8 para suporte a caracteres especiais

3. **Segurança**
   - Validação de permissões por role
   - Isolamento de dados por tenant
   - Logging de geração de arquivos

### Logs e Monitoramento

1. **Logs de Erro**
```python
current_app.logger.error(f"Erro ao gerar o arquivo de retorno - {mensagem}")
```

2. **Informações Registradas**
   - Timestamp da geração
   - Usuário solicitante
   - Tenant
   - Status da geração
   - Erros encontrados

## Casos de Uso

### 1. Integração com Sistemas Financeiros
- Importação de dados para ERP
- Conciliação financeira
- Controle de fluxo de caixa

### 2. Auditoria e Compliance
- Registro de operações
- Acompanhamento de status
- Histórico de transações

### 3. Relatórios Gerenciais
- Análise de operações
- Controle de vencimentos
- Gestão de fornecedores

## Tratamento de Erros

1. **Erros Comuns**
   - Dados não encontrados
   - Falha na geração do CSV
   - Problemas de permissão

2. **Mensagens de Erro**
   - Específicas e acionáveis
   - Logging detalhado
   - Feedback apropriado ao usuário

## Recomendações de Uso

1. **Performance**
   - Recomendado para execução em horários de baixo uso
   - Considerar paginação para grandes volumes
   - Utilizar filtros quando possível

2. **Manutenção**
   - Monitorar tamanho dos arquivos gerados
   - Verificar logs periodicamente
   - Validar integridade dos dados

## Dependências
- `arquivo_retorno.py`: Módulo de geração do CSV
- `decorators.py`: Autenticação e controle de acesso
- Flask: Framework web
- Logging: Sistema de logs
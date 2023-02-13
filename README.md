# Alpha Store

## Tabela de Conteúdos
<ul>
    <li> Guia para rodar o projeto </li>
    <li> Packages e rotas </li>
</ul>
<br>
<hr>

## Guia Para Rodar o projeto
<p> Esta seção dedica-se a explicar o passo-a-passo necessário para rodar esta aplicação </p>

### Passos Resumidos:
<ol>
    <li>Clone o repositório para uma pasta de trabalho</li>
    <li>No diretório alpha_store/alpha_store procure por config.ini e insira as credenciais de um banco de dados local</li>
    <li> Faça as migrações rodando ``alembic upgrade head`` </li>
    <li> Rode a aplicação utilizando __ini__.py, flask run ou waitress-serve </li>
</ol>

Além disso, foi criado também <a href="https://github.com/JEdmario16/alpha-store/blob/main/playground.ipynb">este notebook</a> que pode ser utilizado para testar as rotas. <br>
Para loadar os dados de products.json no banco de dado, também desenvolvi ``extra.py```. Basta executar:
```bash
python3 extra.py
```

### Passo 1: Requisitos Iniciais
<span>
Para rodar este projeto, é necessário utilizar o gerenciador de pacotes ``poetry``.
Antes de começar, clonde o <a href="https://github.com/JEdmario16/alpha-store">repositório do projeto</a> em uma pasta de trabalho. <br>
Para isto, basta digitar ``git clone`` https://github.com/JEdmario16/alpha-store`` no terminal, o que criará o diretório ``alpha_store`` contendo os arquivos deste projeto.
</span>

### Passo 2: Setup
<span>

Caso seu gerenciador de pacotes seja o poetry, você pode criar e ativar um ambiente virtual digitando ``poetry shell`` e instalar todas as dependências do projeto utilizando ``poetry install``.
No arquivo ``pyproject.toml`` é possível vizualizar todas as dependências que serão instaladas.

Antes de rodar o projeto, precisamos setar algumas configurações iniciais. 
Ao clonar o repositório, você terá o arquivo alpha_store/config.ini, onde deve ser setado toda a configuração do banco de dados.
A seção ``DATABASE`` deverá armazenar as informações sobre o banco de dados principal. Já a seção de ``MOCK_DATABASE`` armazena as credenciais para se concectar ao banco de dados a ser utilizados nos testes. <br>

Caso haja alguma configuração faltante/incorretado db, o sistema de log da aplicação e o traceback do SQLAlchemy irão ser úteis para verificar o que ocorreu.

Nesta aplicação, foi utilizado o alembic para realizar as migrações. Antes de rodar a aplicação pela primeira vez, é necessário digitar no console:
 ``alembic upgrade head`` para criar e persistir os schemas no banco de dados setado em config.ini

<i> Nota: No repositório, também foi passado o histórico de versões do alembic. Isto significa que apenas o comando ``alembic upgrade head`` é necessário para fazer as migrações. No entanto, caso problemas ocorram, talvez seja necessário apagar as versões em migrations/versions/) e rodar ``alembic revision --autogenerate -m "first migration" 
Além disso, em migrations/env é possível passar uma db_uri completa para rodar na aplicação.</i>

<i> Nota: Caso apenas o database principal seja passado, não será possível rodar os testes. Além disso, caso o database de testes seja o mesmo que o principal, a aplicação irá desfazer toda a migração a cada vez que algum teste for executado.</i>
</span>

### Passo 3: Rodando a aplicação
<p> Após realizar os passos acima, é hora de rodar a aplicação. Podemos fazer isso de três maneiras: </p>

#### Modo 1: Rodando em modo de debugging
Para rodar aplicação em modo debug basta executar no terminal ``py __ini__.py`` (você precisa estar dentro de alpha_store/alpha_store)

#### Modo 2: Rodando a aplicação sem um wsgi
Caso tenha problemas com o waitress, você pode também rodar a app utilizando apenas o flask. Para isso, basta executar ``flask run`` no terminal. 

#### Modo 3: Utilizando o waitress
Caso queira utilizar o waitress para rodar a aplicação, basta ir para alpha_store/ e executar a seguinte linha de comando no terminal:
``waitress-serve --listen:127.0.0.1:5000 wsgi:app``

## Rotas da api:

Rotas de Auth package: <br>
Registro de usuários: ```/apis/v1/user/register``` <br>
Login de usuários : ```/apis/v1/user/login```</br>
Oter carrinho: ```/apis/v1/user/cart```<br>
Adicionar produtos no carrinho: ```/apis/v1/user/cart/add-to-cart/<int product_id>``` <br>
Remover produtos do carrinho: ```/apis/v1/user/cart/remove-from-cart/<int product_id>``` <br>
checkout: ```/apis/v1/user/cart/checkout``` <br>
listar pedidos: ```/apis/v1/user/orders``` <br>
Logout: ```/apis/v1/user/logout``` <br>

Rotas de Catalog Package<br>
Obter itens(com filtros): ```/apis/v1/catalog/get_products```<br>

Estas rotas estão na aplicação mas não são requisitos(bonus) <br>

Obter produtos por id: ```/apis/v1/catalog/get_products_by_id/<id product_id>``` <br>
Obter produtos por nome: ```/apis/v1/catalog/get_products_by_name/<str product_name>``` <br>
Gera report de vendas: ```apis/v1/analytics/report```


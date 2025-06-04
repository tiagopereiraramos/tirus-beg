from configs.config import getenv


class Parameters:
    """
    A class to represent the parameters for the application.
    """

    def __init__(
        self,
        cadastro,
        db,
        nome_arquivo=None,
        coda_row_id=None,
        rodar_sat=False,
        hash_processo=None,
        session_id=None,
        data_vencimento=None,  # Adionado dado da execução do processo
    ):
        # Inicializa os dados de cadastro e fatura
        self._initialize_cadastro_params(cadastro)
        # Configurações do ambiente
        self._initialize_environment_params(cadastro, rodar_sat)

        # Variáveis de processo e cron
        self.coda_row_id = coda_row_id if coda_row_id else ""
        self.hash_processo = hash_processo  # Atribui o hash_processo
        self.session_id = session_id if session_id else ""
        self.db = db
        self.is_dev = db.is_dev
        self.nome_arquivo = nome_arquivo if nome_arquivo else ""
        self.data_vencimento = (
            data_vencimento if data_vencimento else ""
        )  # Adionado dado da execução do processo

    def _initialize_cadastro_params(self, cadastro):
        """
        Inicializa os parâmetros de cadastro (como cnpj, razao, etc).
        """
        self.hash_cron_cad = cadastro.hash_cron_cad if cadastro.hash_cron_cad else ""
        self.cnpj = cadastro.cnpj if cadastro.cnpj else ""
        self.razao = cadastro.razao if cadastro.razao else ""
        self.nome_filtro = cadastro.nome_filtro if cadastro.nome_filtro else ""
        self.unidade = cadastro.unidade if cadastro.unidade else ""
        self.operadora = cadastro.operadora if cadastro.operadora else ""
        self.servico = cadastro.servico if cadastro.servico else ""
        self.dados_sat = cadastro.dados_sat if cadastro.dados_sat else ""
        self.filtro = cadastro.filtro if cadastro.filtro else ""
        self.cpf = cadastro.cpf if cadastro.cpf else ""

    def _initialize_environment_params(self, cadastro, rodar_sat):
        """
        Inicializa as variáveis de ambiente (como url, login, senha).
        Se `rodar_sat` for False, usa os dados do `cadastro`.
        """
        if not rodar_sat:
            # Se rodar_sat é False, usamos os valores do cadastro
            self.url = cadastro.url
            self.login = cadastro.login
            self.senha = cadastro.senha
        else:
            # Caso contrário, usamos as variáveis de ambiente
            self.url = getenv("URLSAT")
            self.login = getenv("LOGIN")
            self.senha = getenv("SENHA")

    def __getattr__(self, name):
        """
        Tenta buscar o atributo diretamente no banco de dados.
        """
        if hasattr(self.db, name):
            return getattr(self.db, name)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

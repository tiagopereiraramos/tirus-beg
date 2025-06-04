from typing import Any, Dict, List, Optional
import gspread
import time
from configs.config import getenv
from db.mongo import Database
from google.oauth2.service_account import Credentials
from util.utilities import generate_hash_cad
from util.dataclass import Cadastro
from util.mapeamento import carregar, atualizar_da_planilha, salvar, set_hash


def is_empty_row(row: List[str]) -> bool:
    """Verifica se a linha está vazia."""
    return all(cell.strip() == "" for cell in row)


if __name__ == "__main__":
    # Configure o caminho para o arquivo JSON das credenciais
    credenciais = Credentials.from_service_account_file(
        "app/credentials/automacaoemailbgtele-33c5dca1ebff.json",
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )

    # Autentica com o Google Sheets
    cliente = gspread.authorize(credenciais)

    # Abre a planilha pelo nome
    planilha = cliente.open("DADOS SAT - BGTELECOM")

    # Seleciona a primeira aba da planilha
    aba = planilha.sheet1

    # Lê os dados da aba como uma lista de listas
    dados = aba.get_all_values()

    # Obtém o cabeçalho (primeira linha da planilha)
    cabecalho = dados[0]
    print("Cabeçalho original:", cabecalho)

    # Define os campos que devem ser ignorados
    ignorar = {"OBS", "STATUS", "PATCHDOWNLOAD"}

    # Filtra os campos úteis do cabeçalho
    cabecalho_filtrado = [campo for campo in cabecalho if campo not in ignorar]
    print("Cabeçalho filtrado:", cabecalho_filtrado)

    # Carrega o mapeamento salvo
    carregar()

    # Atualiza o mapeamento com os hashes da planilha
    atualizar_da_planilha(aba, cabecalho)

    # Salva o mapeamento atualizado
    salvar()

    # Obtém os dados restantes
    linhas = dados[1:]

    # Converte as linhas para objetos Cadastro
    cadastros: List[Cadastro] = []
    linhas_para_processar = []  # Armazena os índices das linhas a processar

    for index, linha in enumerate(linhas):
        if is_empty_row(linha):
            continue  # Pula linhas em branco

        # Gera o hash para a linha atual
        hash_existente = generate_hash_cad(
            linha[cabecalho.index("NOME SAT")].strip(),
            linha[cabecalho.index("OPERADORA")].strip(),
            linha[cabecalho.index("SERVIÇO")].strip(),
            linha[cabecalho.index("DADOS SAT")].strip(),
            linha[cabecalho.index("FILTRO")].strip(),
            linha[cabecalho.index("UNIDADE / FILTRO SAT")].strip())

        # Verifica se o hash na planilha é diferente do gerado
        hash_planilha = linha[cabecalho.index("HASH")].strip()

        if hash_planilha != hash_existente:
            linha_idx = index + 2  # Número real da linha na planilha
            print(
                f"Linha {linha_idx}: Hash diferente ou em branco. Processando.")

            registro = dict(zip(cabecalho_filtrado, linha))
            cadastro = Cadastro.from_row(registro)
            if cadastro:
                cadastro.hash_auxiliar = hash_existente
                # Hash da planilha (pode estar vazio)
                cadastro.hash_cron_cad = hash_planilha
                cadastros.append(cadastro)
                # Armazena o índice para processamento
                linhas_para_processar.append(index)

    db = Database()

    try:
        request_counter = 1
        for i, cadastro in enumerate(cadastros):
            # Recupera o índice original da linha
            index = linhas_para_processar[i]
            linha_idx = index + 2  # Número real da linha na planilha

            print(f"Processando linha {linha_idx}")

            # Passando o índice da linha real na planilha
            hash_value = db.insert_cadastro(cadastro, linha_indice=linha_idx)

            if not hash_value.strip() == "":
                # Escreve o hash na coluna HASH da planilha
                aba.update_cell(
                    linha_idx, cabecalho.index("HASH") + 1, hash_value)

                # Atualiza nosso mapeamento com o novo hash
                set_hash(linha_idx, hash_value)
                print(
                    f"Linha {linha_idx}: Atualizado hash para {hash_value}")

                # Salva o mapeamento a cada 10 atualizações para garantir persistência
                if request_counter % 10 == 0:
                    salvar()

                request_counter += 1

            # Pausa a execução a cada 50 requisições
            if request_counter % 50 == 0:
                time.sleep(60)  # Aguarda 60 segundos

        # Salva o mapeamento final
        salvar()

        print("Dados inseridos e hash atualizados com sucesso!")

    except Exception as err:
        print(f"Erro: {err}")
    finally:
        db.close()  # Fechar a conexão com o banco de dados

import datetime

import pandas as pd
import streamlit as st
from services.blob_service import BlobStorageService
from services.credit_card_service import CreditCardValidator
from services.data_base import DatabaseService

# Inicializa os serviços
credit_card_validator = CreditCardValidator()
blob_storage_service = BlobStorageService()
database_service = DatabaseService()

# Menu de navegação
menu_options = {
    "Início": "🏠",
    "Análise de Cartão": "💳",
    "Consulta Banco de Dados": "🔍",
    "Documentação": "📚",
    "Sobre": "ℹ️",
}


# Sidebar com o menu
selected_page = st.sidebar.radio(
    "Menu", list(menu_options.keys()), format_func=lambda x: f"{x} {menu_options[x]}"
)

# Informações do desenvolvedor
st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 Desenvolvedor")
st.sidebar.markdown("**Julio Okuda**")

# Links sociais
st.sidebar.markdown(
    """
    <div class="social-links">
        <a href="https://github.com/Jcnok" target="_blank">
            <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" />
        </a>
        <a href="https://linkedin.com/in/juliookuda" target="_blank">
            <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />
        </a>
    </div>
""",
    unsafe_allow_html=True,
)


# Páginas
if selected_page == "Início":
    st.title("🌟 Simplificando a Validação de Cartões no E-commerce")
    st.markdown(
        """
        Já parou para pensar como algumas plataformas de e-commerce utilizam tecnologias
        avançadas para facilitar compras e prevenir fraudes? Lembra daquele momento mágico
        em que, ao finalizar uma compra, em vez de digitar todos os dados do cartão, você
        pode simplesmente enviar uma foto?
        #### 💡 Nossa Proposta
        Este projeto demonstra exatamente como essa mágica acontece! Utilizando a
        Inteligência Artificial da Azure, implementamos um sistema de validação
        de cartões que torna esse processo não só possível, mas também extremamente
        simples.
        #### 🚀 Como Funciona
        1. Faça upload da imagem do cartão
        2. A IA analisa os dados instantaneamente
        3. Receba a validação em segundos
        4. Dados são armazenados para análises futuras
        #### 🎯 Benefícios
        - Detecção automática das informações sem digitação
        - Interface intuitiva e amigável
        - Armazenamento para análises futuras
        - Consultas facilitadas com exportação para CSV
        #### 🔍 Explorando o Projeto
        Este é um projeto demonstrativo que utiliza tecnologias de ponta da Azure
        para mostrar como implementar validação de cartões de forma eficiente.
        Embora seja uma POC (Prova de Conceito), já inclui os principais elementos
        necessários para um sistema completo:
        - Extração precisa de dados do cartão
        - Validação em tempo real
        - Armazenamento estruturado
        - Interface para análise de dados
        #### 🎯 Objetivo
        Demonstrar na prática como as tecnologias modernas podem ser aplicadas
        para criar soluções que melhoram significativamente a experiência do
        usuário em transações financeiras.
        """
    )

elif selected_page == "Análise de Cartão":
    st.title("💳 Análise de Cartão")
    uploaded_file = st.file_uploader(
        "Carregue a imagem do cartão", type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:
        # Exibe imagem carregada
        st.image(uploaded_file, caption="Imagem do Cartão", use_column_width=True)
        if st.button("💳Analisar Cartão"):
            with st.spinner("Processando..."):
                # Upload para Blob Storage
                file_name = uploaded_file.name
                file = uploaded_file.getvalue()
                blob_url = blob_storage_service.upload_blob(file, file_name)
            if blob_url:
                # Detecta informações do cartão
                card_info = credit_card_validator.detect_credit_card_info_from_url(
                    blob_url
                )
                if card_info:
                    # Validação simplificada
                    st.write("Informações do Cartão:")
                    st.write(card_info)
                    validation_result = credit_card_validator.validate_card_info(
                        card_info
                    )
                    if validation_result["is_valid"]:
                        st.success("✅ Cartão Válido")
                        existing_card = database_service.get_card_by_number(
                            card_info["card_number"]
                        )
                        if existing_card:
                            st.info(
                                f"Cartão já existe no banco de dados. ID: {existing_card['id']}"
                            )
                        else:
                            card_info["is_valid"] = validation_result[
                                "is_valid"
                            ]  # Converter para string para o banco de dados
                            card_info["processed_at"] = (
                                datetime.datetime.now().isoformat()
                            )
                            database_service.insert_card(card_info)
                            st.success("Cartão inserido no banco de dados!")
                    else:
                        st.error("❌ Cartão Inválido")
                        st.error("Não foi possível analisar o cartão.")
            else:
                st.error("Erro ao carregar imagem para o Blob Storage.")

elif selected_page == "Consulta Banco de Dados":
    st.title("🔍 Consulta Banco de Dados")
    query = st.text_input("Insira a query SQL (apenas SELECT):")

    if st.button("Executar Query"):
        try:
            results = database_service.execute_custom_query(query)
            if results:
                df = pd.DataFrame(results)
                st.dataframe(df)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV", csv, file_name="credit_cards.csv", mime="text/csv"
                )
            else:
                st.info("Nenhum resultado encontrado.")
        except ValueError as e:
            st.error(e)
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")

elif selected_page == "Documentação":
    st.title("📚 Documentação")
    st.markdown(
        """
    # Documentação do Credit Card Analyzer

    ## Visão Geral

    Este aplicativo utiliza a API do Azure Document Intelligence para extrair informações de cartões de crédito a partir de imagens.  Os dados extraídos são então validados e persistidos em um banco de dados SQLite.

    ##  Funcionalidades Principais

    * **Upload de Imagem:** Permite ao usuário carregar uma imagem de um cartão de crédito.
    * **Análise de Imagem:** Usa a API do Azure Document Intelligence para detectar e extrair informações como número do cartão, data de validade, nome do titular e nome do banco.
    * **Validação de Cartão:** Realiza uma validação básica do número e data de validade do cartão.
    * **Armazenamento de Dados:** Armazena as informações do cartão (incluindo o resultado da validação) em um banco de dados SQLite.
    * **Consulta de Dados:** Permite consultar os dados armazenados no banco de dados utilizando consultas SQL.
    * **Exportação de Dados:** Permite exportar os resultados das consultas para um arquivo CSV.

    ##  Arquitetura

    O aplicativo segue uma arquitetura de três camadas:

    1. **Frontend (Streamlit):** Interface do usuário para interação com o usuário.
    2. **Backend (Python):** Lógica de negócio, incluindo a interação com os serviços da Azure e o banco de dados.
    3. **Azure Services:** Azure Document Intelligence e Azure Blob Storage.

    ##  Tecnologias Utilizadas

    * **Streamlit:** Framework Python para criar aplicações web.
    * **Python:** Linguagem de programação.
    * **Azure Document Intelligence:** Serviço da Azure para extração de informações de documentos.
    * **Azure Blob Storage:** Serviço da Azure para armazenamento de objetos de dados binários.
    * **SQLite:** Sistema de gerenciamento de banco de dados relacional.
    """
    )

elif selected_page == "Sobre":
    st.title("ℹ️ Sobre")
    st.markdown(
        """
    ### 🎯 Projeto Credit Card Analyzer

    Este projeto é uma Prova de Conceito (POC) desenvolvida como parte do
    [Bootcamp Microsoft Certification Challenge #1 - AI 102](https://www.dio.me/bootcamp/microsoft-ai-102). O objetivo é demonstrar a aplicação
    prática de conceitos modernos de desenvolvimento e integração com
    serviços em nuvem da Azure.

    #### 🛠️ Tecnologias Utilizadas
    - **Frontend**: Streamlit
    - **Backend**: Python
    - **Cloud**: Azure Services
    - **Database**: SQLite
    - **Version Control**: Git

    #### 🌟 Características
    - Interface intuitiva
    - Processamento de imagem e validação
    - Armazenamento em banco de dados
    - Análise e exportação de dados
    - Integração com serviços Azure (Document Intelligence e Blob Storage)

    #### 👨‍💻 Desenvolvimento
    Desenvolvido por **Julio Okuda** como parte do projeto final do bootcamp,
    demonstrando a aplicação prática dos conceitos aprendidos durante o bootcamp.

    #### 📝 Nota
    Este é um projeto educacional e demonstrativo, não devendo ser utilizado
    em ambiente de produção sem as devidas adaptações e medidas de segurança.
    """
    )

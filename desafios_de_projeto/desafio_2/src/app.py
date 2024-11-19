import streamlit as st
from datetime import datetime
#from PIL import Image
#import time
#from pathlib import Path
from services.blob_service import upload_to_blob
from services.credit_card_service import detect_credit_card_info
from services.data_base import DataBase
import pandas as pd

class StreamlitInterface:
    """Classe principal para interface Streamlit."""
    
    def __init__(self):
        """Inicializa a interface com configurações básicas."""
        st.set_page_config(
            page_title="Credit Card Analyzer",
            #page_title_icon="💳",
            layout="wide",
            initial_sidebar_state="expanded"
            )
        self.db = DataBase()
        self._setup_session_state()
        self._apply_custom_css()
        
        
    def _setup_session_state(self):
        """Inicializa variáveis de estado da sessão."""
        if 'page' not in st.session_state:
            st.session_state.page = 'Início'
            
    def _apply_custom_css(self):
        """Aplica estilos CSS customizados."""
        st.markdown("""
            <style>
                .main {
                    padding: 2rem;
                }
                .stButton>button {
                    width: 100%;
                }
                .social-links {
                    display: flex;
                    justify-content: center;
                    gap: 1rem;
                    margin: 1rem 0;
                }
                .card-valid {
                    padding: 1rem;
                    border-radius: 0.5rem;
                    background-color: #c8e6c9;
                    color: #2e7d32;
                }
                .card-invalid {
                    padding: 1rem;
                    border-radius: 0.5rem;
                    background-color: #ffcdd2;
                    color: #c62828;
                }
            </style>
        """, unsafe_allow_html=True)
        
    def show_header(self):
        """Exibe o cabeçalho com navegação e informações do desenvolvedor."""
        st.sidebar.title("🏦 Credit Card Analyzer")
        
        # Menu de navegação
        menu_options = {
            "Início": "🏠",
            "Análise de Cartão": "💳",
            "Consulta Banco de Dados": "🔍",
            "Documentação": "📚",
            "Sobre": "ℹ️"
        }
        
        selected = st.sidebar.radio(
            "Navegação",
            list(menu_options.keys()),
            format_func=lambda x: f"{menu_options[x]} {x}"
        )
        
        # Informações do desenvolvedor
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👨‍💻 Desenvolvedor")
        st.sidebar.markdown("**Julio Okuda**")
        
        # Links sociais
        st.sidebar.markdown("""
            <div class="social-links">
                <a href="https://github.com/Jcnok" target="_blank">
                    <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" />
                </a>
                <a href="https://linkedin.com/in/juliookuda" target="_blank">
                    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />
                </a>
            </div>
        """, unsafe_allow_html=True)
        
        return selected
        
    def home_page(self):
        """Página inicial."""
        st.title("🏦 Credit Card Analyzer")
        
        st.markdown("""
        ### 🌟 Simplificando a Validação de Cartões no E-commerce
        
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
        """)
        
    def analyze_card_page(self):
        """Página de análise de cartões."""
        st.title("💳 Análise de Cartão de Crédito")
        
        uploaded_file = st.file_uploader("Escolha uma imagem do cartão", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file:
            # Exibe imagem carregada
            st.image(uploaded_file, caption="Imagem do Cartão", use_column_width=True)
            
            if st.button("Analisar Cartão"):
                with st.spinner("Processando..."):
                    # Upload para Blob Storage
                    file_name = f"card_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{uploaded_file.name.split('.')[-1]}"
                    blob_url = upload_to_blob(uploaded_file.getvalue(), file_name)
                    
                    if blob_url:
                        # Detecta informações do cartão
                        card_info = detect_credit_card_info(blob_url)
                        
                        if card_info:
                            # Validação simplificada (pode ser expandida)
                            is_valid = bool(card_info.get('card_number'))
                            
                            # Prepara dados para o banco
                            card_data = {
                                **card_info,
                                'is_valid': 'valid' if is_valid else 'invalid',
                                'processed_at': datetime.now().isoformat()
                            }
                            
                            # Insere no banco
                            self.db.insert_card(card_data)
                            
                            # Exibe resultados
                            st.markdown(
                                f"<div class='card-{'valid' if is_valid else 'invalid'}'>"
                                f"Status: {'✅ Cartão Válido' if is_valid else '❌ Cartão Inválido'}"
                                "</div>",
                                unsafe_allow_html=True
                            )
                            
                            st.json(card_info)
                    else:
                        st.error("Erro ao processar o arquivo.")
                        
    def query_database_page(self):
        """Página de consulta ao banco de dados."""
        st.title("🔍 Consulta ao Banco de Dados")
        
        # Opções de filtro
        filter_options = st.multiselect(
            "Selecione os filtros:",
            ["Banco", "Validade", "Data de Processamento"]
        )
        
        # Query base
        query = "SELECT * FROM credit_cards"
        where_clauses = []
        
        # Aplicação dos filtros
        if "Banco" in filter_options:
            bank = st.text_input("Nome do Banco:")
            if bank:
                where_clauses.append(f"bank_name LIKE '%{bank}%'")
                
        if "Validade" in filter_options:
            valid_status = st.selectbox("Status:", ["Todos", "Valid", "Invalid"])
            if valid_status != "Todos":
                where_clauses.append(f"is_valid = '{valid_status.lower()}'")
                
        if "Data de Processamento" in filter_options:
            date_range = st.date_input("Período:", [])
            if len(date_range) == 2:
                where_clauses.append(
                    f"processed_at BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
                )
                
        # Construção da query final
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        # Executa a query e exibe resultados
        try:
            results = self.db.execute_custom_query(query)
            if results:
                df = pd.DataFrame(results)
                st.dataframe(df)
                
                # Export options
                if st.button("Exportar CSV"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        csv,
                        "card_data.csv",
                        "text/csv"
                    )
            else:
                st.info("Nenhum resultado encontrado.")
        except Exception as e:
            st.error(f"Erro na consulta: {e}")
            
    def documentation_page(self):
        """Página de documentação."""
        st.title("📚 Documentação")
        
        st.markdown("""
        ### 📖 Como Usar o Sistema
        
        #### 1. Análise de Cartão
        1. Acesse a página "Análise de Cartão"
        2. Faça upload da imagem do cartão
        3. Clique em "Analisar Cartão"
        4. Aguarde o processamento
        5. Visualize os resultados
        
        #### 2. Consulta ao Banco de Dados
        1. Acesse a página "Consulta Banco de Dados"
        2. Selecione os filtros desejados
        3. Configure os parâmetros
        4. Visualize os resultados
        5. Exporte os dados se necessário
        
        #### 🔧 Tecnologias Utilizadas
        - Python 3.12+
        - Streamlit
        - Azure Document Intelligence
        - Azure Blob Storage
        - SQLite
        
        #### 📋 Requisitos Técnicos
        - Conexão com Internet
        - Navegador 
        - Imagens em formato PNG, JPG ou JPEG
        """)
        
    def about_page(self):
        """Página sobre o projeto."""
        st.title("ℹ️ Sobre")
        
        st.markdown("""
        ### 🎯 Projeto Credit Card Analyzer
        
        Este projeto é uma Prova de Conceito (POC) desenvolvida como parte do 
        Bootcamp Microsoft Certification Challenge #1 - AI 102. O objetivo é demonstrar a aplicação 
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
        """)
        
    def run(self):
        """Executa a aplicação."""
        selected_page = self.show_header()
        
        # Roteamento de páginas
        if selected_page == "Início":
            self.home_page()
        elif selected_page == "Análise de Cartão":
            self.analyze_card_page()
        elif selected_page == "Consulta Banco de Dados":
            self.query_database_page()
        elif selected_page == "Documentação":
            self.documentation_page()
        elif selected_page == "Sobre":
            self.about_page()

if __name__ == "__main__":
    app = StreamlitInterface()
    app.run()
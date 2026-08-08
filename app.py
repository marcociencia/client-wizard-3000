import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Sistema de Cadastro",
    page_icon="📋",
    layout="wide"
)

# --- Função de Conexão com Banco de Dados ---
def get_db_connection():
    """Estabelece conexão com o banco de dados MySQL"""
    try:
        # Usando secrets do Streamlit para dados sensíveis
        connection = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"]
        )
        return connection
    except Error as e:
        st.error(f"❌ Erro ao conectar ao banco de dados: {e}")
        return None

# --- Funções CRUD ---
def create_table():
    """Cria a tabela de clientes se não existir"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                telefone VARCHAR(20),
                endereco TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

def insert_cliente(nome, email, telefone, endereco):
    """Insere um novo cliente no banco de dados"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO clientes (nome, email, telefone, endereco)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (nome, email, telefone, endereco))
            conn.commit()
            st.success("✅ Cliente cadastrado com sucesso!")
            return True
        except Error as e:
            if "Duplicate entry" in str(e):
                st.error("❌ Este email já está cadastrado!")
            else:
                st.error(f"❌ Erro ao cadastrar: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False

def get_all_clientes():
    """Retorna todos os clientes cadastrados"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, email, telefone, endereco, data_cadastro FROM clientes ORDER BY data_cadastro DESC")
            result = cursor.fetchall()
            return result
        except Error as e:
            st.error(f"❌ Erro ao buscar clientes: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    return []

def delete_cliente(cliente_id):
    """Deleta um cliente pelo ID"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
            conn.commit()
            st.success("✅ Cliente deletado com sucesso!")
        except Error as e:
            st.error(f"❌ Erro ao deletar: {e}")
        finally:
            cursor.close()
            conn.close()

# --- Interface Principal ---
def main():
    # Título
    st.title("📋 Sistema de Cadastro de Clientes")
    st.markdown("---")
    
    # Inicializar tabela
    create_table()
    
    # Sidebar com menu
    menu = ["📝 Cadastrar", "👥 Visualizar", "📊 Dashboard"]
    choice = st.sidebar.radio("📌 Navegação", menu)
    
    # --- PÁGINA DE CADASTRO ---
    if choice == "📝 Cadastrar":
        st.header("➕ Novo Cadastro")
        st.markdown("Preencha os dados abaixo para cadastrar um novo cliente:")
        
        with st.form(key="cadastro_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("👤 Nome Completo *", placeholder="Digite o nome completo")
                email = st.text_input("📧 Email *", placeholder="exemplo@email.com")
            
            with col2:
                telefone = st.text_input("📱 Telefone", placeholder="(00) 00000-0000")
                endereco = st.text_area("📍 Endereço", placeholder="Rua, número, bairro, cidade")
            
            submit_button = st.form_submit_button(label="💾 Cadastrar Cliente")
            
            if submit_button:
                if not nome or not email:
                    st.warning("⚠️ Os campos Nome e Email são obrigatórios!")
                else:
                    insert_cliente(nome, email, telefone, endereco)
    
    # --- PÁGINA DE VISUALIZAÇÃO ---
    elif choice == "👥 Visualizar":
        st.header("👥 Clientes Cadastrados")
        
        # Botão para atualizar
        if st.button("🔄 Atualizar Lista"):
            st.rerun()
        
        # Buscar e mostrar dados
        clientes = get_all_clientes()
        
        if clientes:
            # Converter para DataFrame para melhor visualização
            df = pd.DataFrame(clientes, columns=['ID', 'Nome', 'Email', 'Telefone', 'Endereço', 'Data Cadastro'])
            st.dataframe(df, use_container_width=True)
            
            # Métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("📊 Total de Clientes", len(clientes))
            col2.metric("📅 Último Cadastro", clientes[0][5].strftime("%d/%m/%Y") if clientes else "N/A")
            
            # Opção de deletar
            st.markdown("---")
            st.subheader("🗑️ Deletar Cliente")
            with st.form(key="delete_form"):
                cliente_id = st.number_input("ID do Cliente para deletar", min_value=1, step=1)
                delete_btn = st.form_submit_button("🗑️ Deletar Cliente")
                
                if delete_btn:
                    delete_cliente(cliente_id)
                    st.rerun()
        else:
            st.info("ℹ️ Nenhum cliente cadastrado ainda. Volte para a página de cadastro.")
    
    # --- PÁGINA DE DASHBOARD ---
    elif choice == "📊 Dashboard":
        st.header("📊 Dashboard de Clientes")
        
        clientes = get_all_clientes()
        if clientes:
            df = pd.DataFrame(clientes, columns=['ID', 'Nome', 'Email', 'Telefone', 'Endereço', 'Data Cadastro'])
            
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("👥 Total Clientes", len(df))
            col2.metric("📧 Emails Cadastrados", df['Email'].nunique())
            col3.metric("📱 Telefones", df['Telefone'].count())
            
            # Gráfico de cadastros por mês
            st.subheader("📈 Cadastros por Mês")
            df['Mês'] = df['Data Cadastro'].dt.strftime('%B/%Y')
            registros_por_mes = df.groupby('Mês').size().reset_index(name='Quantidade')
            st.bar_chart(registros_por_mes.set_index('Mês'))
            
            # Tabela resumida
            st.subheader("📋 Últimos Cadastros")
            st.dataframe(df.head(10)[['Nome', 'Email', 'Data Cadastro']], use_container_width=True)
        else:
            st.info("ℹ️ Sem dados para exibir no dashboard.")

if __name__ == "__main__":
    main()
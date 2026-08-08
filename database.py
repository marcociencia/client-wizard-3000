import mysql.connector
from mysql.connector import Error
import streamlit as st

def init_connection():
    """Inicializa a conexão com o banco de dados"""
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"]
        )
    except Error as e:
        st.error(f"Erro de conexão: {e}")
        return None

def create_tables():
    """Cria todas as tabelas necessárias"""
    conn = init_connection()
    if conn:
        cursor = conn.cursor()
        
        # Tabela de clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                telefone VARCHAR(20),
                endereco TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_email (email),
                INDEX idx_data (data_cadastro)
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    return False
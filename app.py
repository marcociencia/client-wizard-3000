import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Client Management System",
    page_icon="📋",
    layout="wide"
)

def get_db_connection():
    """Connect to PostgreSQL on Supabase"""
    try:
        # Check if secrets exist
        if "mysql" not in st.secrets:
            st.error("❌ Secrets not configured! Please add your database credentials.")
            return None
            
        connection = psycopg2.connect(
            host=st.secrets["mysql"]["host"],
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"]
        )
        return connection
    except Exception as e:
        st.error(f"❌ Database connection error: {e}")
        st.info("💡 Make sure you have configured the secrets correctly in Streamlit Cloud settings.")
        return None

def create_table():
    """Create clients table if it doesn't exist"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id SERIAL PRIMARY KEY,
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
            return True
        except Exception as e:
            st.error(f"❌ Error creating table: {e}")
            return False
    return False

def insert_cliente(nome, email, telefone, endereco):
    """Insert a new client"""
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
            st.success("✅ Client registered successfully!")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            if "duplicate key" in str(e).lower():
                st.error("❌ This email is already registered!")
            else:
                st.error(f"❌ Error registering client: {e}")
            return False
    return False

def get_all_clientes():
    """Get all clients"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nome, email, telefone, endereco, data_cadastro 
                FROM clientes 
                ORDER BY data_cadastro DESC
            """)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        except Exception as e:
            st.error(f"❌ Error fetching clients: {e}")
            return []
    return []

def main():
    # Check if secrets are configured
    if "mysql" not in st.secrets:
        st.error("⚠️ Database credentials not configured!")
        st.info("Please add your database credentials in: Settings → Secrets on Streamlit Cloud")
        st.code("""
[mysql]
host = "your-supabase-host.supabase.co"
database = "postgres"
user = "postgres"
password = "your-password"
        """)
        return
    
    # Create table
    create_table()
    
    st.title("📋 Client Management System")
    st.markdown("---")
    
    menu = ["📝 Register", "👥 View All", "📊 Dashboard"]
    choice = st.sidebar.radio("📌 Navigation", menu)
    
    if choice == "📝 Register":
        st.header("➕ New Client Registration")
        
        with st.form(key="register_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("👤 Full Name *")
                email = st.text_input("📧 Email *")
            
            with col2:
                telefone = st.text_input("📱 Phone")
                endereco = st.text_area("📍 Address")
            
            submit_button = st.form_submit_button(label="💾 Register Client")
            
            if submit_button:
                if not nome or not email:
                    st.warning("⚠️ Name and Email are required!")
                else:
                    insert_cliente(nome, email, telefone, endereco)
    
    elif choice == "👥 View All":
        st.header("👥 Registered Clients")
        
        if st.button("🔄 Refresh"):
            st.rerun()
        
        clientes = get_all_clientes()
        
        if clientes:
            df = pd.DataFrame(clientes, columns=['ID', 'Name', 'Email', 'Phone', 'Address', 'Registration Date'])
            st.dataframe(df, use_container_width=True)
            st.metric("📊 Total Clients", len(clientes))
        else:
            st.info("ℹ️ No clients registered yet.")
    
    elif choice == "📊 Dashboard":
        st.header("📊 Client Dashboard")
        clientes = get_all_clientes()
        
        if clientes:
            df = pd.DataFrame(clientes, columns=['ID', 'Name', 'Email', 'Phone', 'Address', 'Registration Date'])
            st.metric("👥 Total Clients", len(df))
        else:
            st.info("ℹ️ No data available.")

if __name__ == "__main__":
    main()
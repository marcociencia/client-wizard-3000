import streamlit as st
import psycopg2
from psycopg2 import sql
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Client Management System",
    page_icon="📋",
    layout="wide"
)

# --- Database Connection ---
def get_db_connection():
    """Connect to PostgreSQL on Supabase"""
    try:
        connection = psycopg2.connect(
            host=st.secrets["mysql"]["host"],
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"]
        )
        return connection
    except Exception as e:
        st.error(f"❌ Database connection error: {e}")
        return None

# --- Create Table ---
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

# --- CRUD Functions ---
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
            return True
        except Exception as e:
            if "duplicate key" in str(e).lower():
                st.error("❌ This email is already registered!")
            else:
                st.error(f"❌ Error registering client: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
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
            return result
        except Exception as e:
            st.error(f"❌ Error fetching clients: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    return []

def delete_cliente(cliente_id):
    """Delete a client by ID"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
            conn.commit()
            st.success("✅ Client deleted successfully!")
            return True
        except Exception as e:
            st.error(f"❌ Error deleting client: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False

# --- Main Interface ---
def main():
    # Initialize table
    create_table()
    
    # Title
    st.title("📋 Client Management System")
    st.markdown("---")
    
    # Sidebar menu
    menu = ["📝 Register", "👥 View All", "📊 Dashboard"]
    choice = st.sidebar.radio("📌 Navigation", menu)
    
    # --- REGISTER PAGE ---
    if choice == "📝 Register":
        st.header("➕ New Client Registration")
        st.markdown("Fill in the details below to register a new client:")
        
        with st.form(key="register_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("👤 Full Name *", placeholder="Enter full name")
                email = st.text_input("📧 Email *", placeholder="example@email.com")
            
            with col2:
                telefone = st.text_input("📱 Phone", placeholder="(00) 00000-0000")
                endereco = st.text_area("📍 Address", placeholder="Street, number, neighborhood, city")
            
            submit_button = st.form_submit_button(label="💾 Register Client")
            
            if submit_button:
                if not nome or not email:
                    st.warning("⚠️ Name and Email are required fields!")
                else:
                    insert_cliente(nome, email, telefone, endereco)
    
    # --- VIEW PAGE ---
    elif choice == "👥 View All":
        st.header("👥 Registered Clients")
        
        if st.button("🔄 Refresh List"):
            st.rerun()
        
        clientes = get_all_clientes()
        
        if clientes:
            df = pd.DataFrame(clientes, columns=['ID', 'Name', 'Email', 'Phone', 'Address', 'Registration Date'])
            st.dataframe(df, use_container_width=True)
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("📊 Total Clients", len(clientes))
            if clientes:
                col2.metric("📅 Latest Registration", clientes[0][5].strftime("%d/%m/%Y") if clientes[5] else "N/A")
            
            # Delete section
            st.markdown("---")
            st.subheader("🗑️ Delete Client")
            with st.form(key="delete_form"):
                cliente_id = st.number_input("Client ID to delete", min_value=1, step=1)
                delete_btn = st.form_submit_button("🗑️ Delete Client")
                
                if delete_btn:
                    delete_cliente(cliente_id)
                    st.rerun()
        else:
            st.info("ℹ️ No clients registered yet. Go to the Registration page.")
    
    # --- DASHBOARD PAGE ---
    elif choice == "📊 Dashboard":
        st.header("📊 Client Dashboard")
        
        clientes = get_all_clientes()
        
        if clientes:
            df = pd.DataFrame(clientes, columns=['ID', 'Name', 'Email', 'Phone', 'Address', 'Registration Date'])
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("👥 Total Clients", len(df))
            col2.metric("📧 Emails Registered", df['Email'].nunique())
            col3.metric("📱 Phone Numbers", df['Phone'].count())
            
            # Monthly registrations chart
            st.subheader("📈 Registrations by Month")
            df['Month'] = df['Registration Date'].dt.strftime('%B %Y')
            registrations_by_month = df.groupby('Month').size().reset_index(name='Count')
            st.bar_chart(registrations_by_month.set_index('Month'))
            
            # Recent registrations
            st.subheader("📋 Recent Registrations")
            st.dataframe(df.head(10)[['Name', 'Email', 'Registration Date']], use_container_width=True)
        else:
            st.info("ℹ️ No data available for the dashboard.")

if __name__ == "__main__":
    main()
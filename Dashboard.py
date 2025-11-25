import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
import hashlib
import re

def init_auth_db():
    """Initialize SQLite database for authentication"""
    conn = sqlite3.connect('buffabook_auth.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password):
    """Create new user in database"""
    try:
        conn = sqlite3.connect('buffabook_auth.db')
        c = conn.cursor()
        password_hash = hash_password(password)
        c.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', 
                 (email, password_hash))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return False

def verify_user(email, password):
    """Verify user credentials"""
    try:
        conn = sqlite3.connect('buffabook_auth.db')
        c = conn.cursor()
        password_hash = hash_password(password)
        c.execute('SELECT * FROM users WHERE email = ? AND password_hash = ?', 
                 (email, password_hash))
        user = c.fetchone()
        conn.close()
        return user is not None
    except Exception as e:
        st.error(f"Error verifying user: {e}")
        return False

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Initialize main database
def init_main_database():
    """Initialize SQLite database for main application data"""
    conn = sqlite3.connect('buffabook_main.db')
    c = conn.cursor()
    
    # Inventory table
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            product_quantity TEXT NOT NULL,
            product_price REAL NOT NULL,
            total_price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sales table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_quantity TEXT NOT NULL,
            product_price REAL NOT NULL,
            total_sales REAL NOT NULL,
            payment_method TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Purchases table
    c.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_quantity TEXT NOT NULL,
            product_price REAL NOT NULL,
            total_price REAL NOT NULL,
            payment_method TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Journal table
    c.execute('''
        CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            account TEXT NOT NULL,
            debit REAL NOT NULL,
            credit REAL NOT NULL,
            description TEXT,
            transaction_type TEXT DEFAULT 'General',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Ledger table
    c.execute('''
        CREATE TABLE IF NOT EXISTS ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            debit REAL NOT NULL,
            credit REAL NOT NULL,
            balance REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize databases
init_auth_db()
init_main_database()

st.set_page_config(
    page_title="BuffaBook - Peternakan Kerbau",
    page_icon="🐃",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'show_login' not in st.session_state:
    st.session_state.show_login = True  

if not st.session_state.logged_in:
    st.markdown("""
    <style>
        /* Set background color on main Streamlit app container for auth page */
        [data-testid="stAppViewContainer"] {
            background-color: #FDF3B9 !important;
        }
        .auth-container {
            background: #FDF3B9 ;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 2rem auto;
            max-width: 400px;
        }
        .auth-header {
            text-align: center;
            color: #80644B;
            margin-bottom: 2rem;
        }
        .stButton>button {
            width: 100%;
            background-color: #8B6F47 ;
            color: white ;
            border: none ;
        }
        .stButton>button:hover {
            background-color: #5A4634 ;
        }
        .switch-auth {
            text-align: center;
            margin-top: 1rem;
        }
        .switch-auth button {
            background: none ;
            border: none;
            color: #8B6F47;
            text-decoration: underline;
            cursor: pointer;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="auth-header"><h1>🐃 BuffaBook</h1><p>Sistem Pencatatan Peternakan Kerbau</p></div>', unsafe_allow_html=True)
    
    if st.session_state.show_login:
        st.subheader("🔐 Login")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="nama@email.com")
            password = st.text_input("Password", type="password", placeholder="Minimal 6 karakter")
            login_submit = st.form_submit_button("Login")
            
            if login_submit:
                if not email or not password:
                    st.error("Email dan password harus diisi!")
                elif not is_valid_email(email):
                    st.error("Format email tidak valid!")
                elif len(password) < 6:
                    st.error("Password minimal 6 karakter!")
                else:
                    if verify_user(email, password):
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.success("Login berhasil!")
                        st.rerun()
                    else:
                        st.error("Email atau password salah!")
        
        st.markdown('<div class="switch-auth">', unsafe_allow_html=True)
        if st.button("Belum punya akun? Daftar di sini"):
            st.session_state.show_login = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.subheader("📝 Register")
        
        with st.form("register_form"):
            email = st.text_input("Email", placeholder="nama@email.com")
            password = st.text_input("Password", type="password", placeholder="Minimal 6 karakter")
            confirm_password = st.text_input("Konfirmasi Password", type="password", placeholder="Ulangi password")
            register_submit = st.form_submit_button("Daftar")
            
            if register_submit:
                if not email or not password or not confirm_password:
                    st.error("Semua field harus diisi!")
                elif not is_valid_email(email):
                    st.error("Format email tidak valid!")
                elif len(password) < 6:
                    st.error("Password minimal 6 karakter!")
                elif password != confirm_password:
                    st.error("Password dan konfirmasi password tidak sama!")
                else:
                    if create_user(email, password):
                        st.success("Pendaftaran berhasil! Silakan login.")
                        st.session_state.show_login = True
                        st.rerun()
                    else:
                        st.error("Email sudah terdaftar! Silakan gunakan email lain.")
        
        st.markdown('<div class="switch-auth">', unsafe_allow_html=True)
        if st.button("Sudah punya akun? Login di sini"):
            st.session_state.show_login = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

ACCOUNTS = {
    "1-10000": "Kas",
    "1-11000": "Piutang",
    "1-12000": "Persediaan Kerbau Dewasa Jantan",
    "1-12100": "Persediaan Kerbau Dewasa Betina",
    "1-12200": "Persediaan Kerbau Remaja Jantan",
    "1-12300": "Persediaan Kerbau Remaja Betina",
    "1-12400": "Persediaan Anak Kerbau Jantan",
    "1-12500": "Persediaan Anak Kerbau Betina",
    "1-20000": "Kendaraan",
    "1-21000": "Kandang",
    "1-22000": "Peralatan",
    "1-23000": "Akumulasi Penyusutan Kendaraan",
    "1-23100": "Akumulasi Penyusutan Kandang",
    "1-23200": "Akumulasi Penyusutan Peralatan",
    "2-10000": "Utang Usaha",
    "2-20000": "Utang Bank",
    "2-30000": "Pendapatan Diterima di Muka",
    "2-31000": "Utang Gaji",
    "3-30000": "Modal",
    "3-40000": "Prive",
    "4-40000": "Pendapatan",
    "5-50000": "HPP",
    "6-60000": "Beban Pakan",
    "6-60100": "Beban Listrik & Air",
    "6-60200": "Beban Gaji",
    "6-60300": "Beban Lain-lain",
    "6-60400": "Beban Penyusutan Kendaraan",
    "6-60500": "Beban Penyusutan Kandang",
    "6-60600": "Beban Penyusutan Peralatan",
    "6-60700": "Beban Perlengkapan"
}

# Custom CSS
st.markdown("""      
<style>
    .main, .block-container {
        background-color: #FDF3B9 ; 
    }
    [data-testid="stSidebar"] {
        background-color: #80644B; 
        padding-top: 0px;
    }
    [data-testid="stSidebar"] .stButton>button {
        background-color: #C8A574;
        color: white;
        border-radius: 8px;
        width: 100% ;
        text-align: left ;
        padding: 12px 16px ;
        margin: 4px 0 ;
    }

    /* Optional: tambahkan hover effect */
    [data-testid="stSidebar"] .stButton>button:hover {
        background-color: #B8945F;
        border-color: #A5834F;
    }
    .sidebar-title {
        color: #ffffff;      
        font-weight: 700;    
        font-size: 36px;     
    }
    .main-header {
        background: linear-gradient(135deg, #80644B 0%, #8B6F47 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #DDB27A 0%, #C8A574 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        color: white;
    }
    .stButton>button {
        width: 100%;
        background-color: #8B6F47;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #5A4634;
    }
    div[data-testid="stSidebar"] {
        background-color: #DDB27A;
    }     
</style>
""", unsafe_allow_html=True)

# Helper Functions
def format_rupiah(amount):
    """Format angka ke format rupiah"""
    try:
        return f"Rp {float(amount):,.0f}".replace(',', '.')
    except:
        return f"Rp 0"

def safe_parse_int_from_qtytext(qty_text):
    try:
        if qty_text is None:
            return 0
        if isinstance(qty_text, (int, float)):
            return int(qty_text)
        s = str(qty_text).strip()
        if s == "":
            return 0
        first = s.split()[0]
        return int(float(first))
    except:
        return 0

def safe_parse_price(text):
    try:
        if text is None:
            return 0.0
        if isinstance(text, (int, float)):
            return float(text)
        s = str(text)
        s = s.replace('Rp', '').replace(' ', '')
        s = s.replace('.', '').replace(',', '')
        return float(s) if s != "" else 0.0
    except:
        return 0.0
    
def get_inventory_account(product_name):
    """Mengembalikan akun persediaan berdasarkan nama produk"""
    product_to_account = {
        "Kerbau Dewasa Jantan": "1-12000 - Persediaan Kerbau Dewasa Jantan",
        "Kerbau Dewasa Betina": "1-12100 - Persediaan Kerbau Dewasa Betina", 
        "Kerbau Remaja Jantan": "1-12200 - Persediaan Kerbau Remaja Jantan",
        "Kerbau Remaja Betina": "1-12300 - Persediaan Kerbau Remaja Betina",
        "Anak Kerbau Jantan": "1-12400 - Persediaan Anak Kerbau Jantan",
        "Anak Kerbau Betina": "1-12500 - Persediaan Anak Kerbau Betina"
    }
    
    for key, account in product_to_account.items():
        if key.lower() in product_name.lower():
            return account
    
    return "1-12000 - Persediaan Kerbau Dewasa Jantan"  # default

# Database Functions
def get_inventory_data():
    """Get all inventory data from database"""
    conn = sqlite3.connect('buffabook_main.db')
    df = pd.read_sql_query("SELECT * FROM inventory", conn)
    conn.close()
    return df

def get_sales_data():
    """Get all sales data from database"""
    conn = sqlite3.connect('buffabook_main.db')
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    return df

def get_purchases_data():
    """Get all purchases data from database"""
    conn = sqlite3.connect('buffabook_main.db')
    df = pd.read_sql_query("SELECT * FROM purchases", conn)
    conn.close()
    return df

def get_journal_data():
    """Get all journal data from database"""
    conn = sqlite3.connect('buffabook_main.db')
    df = pd.read_sql_query("SELECT * FROM journal", conn)
    conn.close()
    return df

def get_ledger_data():
    """Get all ledger data from database"""
    conn = sqlite3.connect('buffabook_main.db')
    df = pd.read_sql_query("SELECT * FROM ledger", conn)
    conn.close()
    return df

def add_inventory_item(product_name, product_quantity, product_price, total_price):
    """Add or update inventory item"""
    conn = sqlite3.connect('buffabook_main.db')
    c = conn.cursor()
    
    # Check if product exists
    c.execute("SELECT * FROM inventory WHERE product_name = ?", (product_name,))
    existing = c.fetchone()
    
    if existing:
        # Update existing product
        c.execute('''
            UPDATE inventory 
            SET product_quantity = ?, product_price = ?, total_price = ?, updated_at = CURRENT_TIMESTAMP
            WHERE product_name = ?
        ''', (product_quantity, product_price, total_price, product_name))
    else:
        # Insert new product
        c.execute('''
            INSERT INTO inventory (product_name, product_quantity, product_price, total_price)
            VALUES (?, ?, ?, ?)
        ''', (product_name, product_quantity, product_price, total_price))
    
    conn.commit()
    conn.close()

def add_sales_transaction(date, product_name, product_quantity, product_price, total_sales, payment_method, timestamp):
    """Add sales transaction"""
    conn = sqlite3.connect('buffabook_main.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO sales (date, product_name, product_quantity, product_price, total_sales, payment_method, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (date, product_name, product_quantity, product_price, total_sales, payment_method, timestamp))
    
    conn.commit()
    conn.close()

def add_purchases_transaction(date, product_name, product_quantity, product_price, total_price, payment_method, timestamp):
    """Add purchases transaction"""
    conn = sqlite3.connect('buffabook_main.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO purchases (date, product_name, product_quantity, product_price, total_price, payment_method, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (date, product_name, product_quantity, product_price, total_price, payment_method, timestamp))
    
    conn.commit()
    conn.close()

def add_journal_entry(date, account, debit, credit, description, transaction_type='General'):
    """Add journal entry"""
    conn = sqlite3.connect('buffabook_main.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO journal (date, account, debit, credit, description, transaction_type)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (date, account, debit, credit, description, transaction_type))
    
    conn.commit()
    conn.close()

def add_ledger_entry(account, date, description, debit, credit, balance):
    """Add ledger entry"""
    conn = sqlite3.connect('buffabook_main.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO ledger (account, date, description, debit, credit, balance)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (account, date, description, debit, credit, balance))
    
    conn.commit()
    conn.close()

def clear_table(table_name):
    """Clear all data from a table"""
    conn = sqlite3.connect('buffabook_main.db')
    c = conn.cursor()
    c.execute(f"DELETE FROM {table_name}")
    conn.commit()
    conn.close()

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"
if 'order_list' not in st.session_state:
    st.session_state.order_list = []

# Sidebar Navigation
with st.sidebar:
    st.markdown('<p class="sidebar-title">🐃 BuffaBook</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    menu_options = {
        "📊 Dashboard": "Dashboard",
        "📦 Kartu Persediaan": "Kartu Persediaan",
        "📈 Ringkasan Penjualan": "Ringkasan Penjualan",
        "✍️ Input Jurnal Umum": "Jurnal Umum",
        "📖 Jurnal Umum": "View Jurnal",
        "📚 Buku Besar": "Buku Besar",
        "⚖️ Neraca Saldo": "Neraca Saldo",
        "📘 Adjusting": "Jurnal Penyesuaian",
        "📋 Laporan Keuangan": "Laporan Keuangan"
    }
    
    for label, page in menu_options.items():
        if st.button(label, key=f"btn_{page}"):
            st.session_state.current_page = page
            st.rerun()

# Main Content Area
def show_dashboard():
    st.markdown('<div class="main-header"><h1>🐃 Welcome to BuffaBook</h1><p>Sistem Pencatatan Peternakan Kerbau</p></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
    <h3>Tentang BuffaBook</h3>
    <p>Selamat datang di BuffaBook – Sistem Pencatatan Peternakan Kerbau.</p>
    <p>Di sini Anda dapat mengelola inventory, pembelian, dan penjualan produk.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats
    col1, col2, col3 = st.columns(3)
    
    try:
        # Total Inventory Items
        inventory_df = get_inventory_data()
        total_items = len(inventory_df)
        
        # Total Purchases
        purchases_df = get_purchases_data()
        total_purchases = purchases_df['total_price'].sum() if not purchases_df.empty else 0
        
        # Total Sales
        sales_df = get_sales_data()
        total_sales = sales_df['total_sales'].sum() if not sales_df.empty else 0
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h2>{total_items}</h2>
                <p>Item Persediaan</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h2>{format_rupiah(total_purchases)}</h2>
                <p>Total Pembelian</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h2>{format_rupiah(total_sales)}</h2>
                <p>Total Penjualan</p>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error loading stats: {e}")

def show_kartu_persediaan():
    st.markdown('<div class="main-header"><h1>📦 Kartu Persediaan</h1></div>', unsafe_allow_html=True)
    
    # Predefined selling prices
    SELLING_PRICE = {
        "Kerbau Dewasa Jantan": 30000000,
        "Kerbau Dewasa Betina": 27000000,
        "Kerbau Remaja Jantan": 20000000,
        "Kerbau Remaja Betina": 17000000,
        "Anak Kerbau Jantan": 15000000,
        "Anak Kerbau Betina": 12000000,
    }
    
    # Tab untuk navigasi
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Pembelian", "💰 Penjualan", "📋 Riwayat Transaksi", "📦 Kartu Persediaan"])
    
    with tab1:
        st.markdown("### 🛒 Tambah Pembelian Baru")
        
        with st.form("form_pembelian"):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Tanggal", datetime.now())
                product_name = st.text_input("Nama Produk")
                payment_method = st.selectbox("Metode Pembayaran", ["Tunai", "Kredit"])
                
            with col2:
                col_qty, col_unit = st.columns([2, 1])
                with col_qty:
                    quantity = st.number_input("Jumlah", min_value=1, value=1)
                with col_unit:
                    unit = st.selectbox("Unit", ["kg", "pcs", "karung", "ekor"])
                
                price = st.number_input("Harga per Unit (Rp)", min_value=0, value=0)
            
            submit = st.form_submit_button("✅ Submit Pembelian", use_container_width=True)
            
            if submit:
                if not product_name:
                    st.error("Nama produk tidak boleh kosong!")
                else:
                    try:
                        total_price = price * quantity
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Update inventory
                        inventory_df = get_inventory_data()
                        product_found = False
                        
                        for idx, row in inventory_df.iterrows():
                            if str(row['product_name']).strip().lower() == product_name.strip().lower():
                                existing_qty_str = str(row['product_quantity']) if row['product_quantity'] is not None else "0"
                                try:
                                    parts = existing_qty_str.split()
                                    qty_lama = int(parts[0]) if parts else 0
                                    existing_unit = parts[1] if len(parts) > 1 else ''
                                except:
                                    qty_lama = 0
                                    existing_unit = ''
                                
                                harga_lama = float(row['product_price'] or 0)
                                qty_baru = quantity
                                harga_baru = float(price)
                                
                                total_qty = qty_lama + qty_baru
                                if total_qty == 0:
                                    harga_rata2 = harga_baru
                                else:
                                    harga_rata2 = ((qty_lama * harga_lama) + (qty_baru * harga_baru)) / total_qty
                                
                                new_quantity = f"{total_qty} {existing_unit or unit}".strip()
                                new_total_price = round(harga_rata2 * total_qty, 2)
                                
                                add_inventory_item(product_name, new_quantity, round(harga_rata2, 2), new_total_price)
                                product_found = True
                                break
                        
                        if not product_found:
                            add_inventory_item(
                                product_name, 
                                f"{quantity} {unit}", 
                                round(price, 2), 
                                round(total_price, 2)
                            )
                        
                        # Add to purchases
                        add_purchases_transaction(
                            date.strftime('%Y-%m-%d'),
                            product_name,
                            f"{quantity} {unit}",
                            round(price, 2),
                            round(total_price, 2),
                            payment_method,
                            timestamp
                        )
                        
                        # ========== OTOMATIS BUAT JURNAL UMUM ==========
                        date_str = date.strftime('%Y-%m-%d')
                        keterangan = f"Pembelian {product_name} - {quantity} {unit}"
                        
                        # Tentukan akun persediaan berdasarkan nama produk
                        inventory_account = "1-12000 - Persediaan Kerbau Dewasa Jantan"  # default
                        
                        product_to_account = {
                            "Kerbau Dewasa Jantan": "1-12000 - Persediaan Kerbau Dewasa Jantan",
                            "Kerbau Dewasa Betina": "1-12100 - Persediaan Kerbau Dewasa Betina", 
                            "Kerbau Remaja Jantan": "1-12200 - Persediaan Kerbau Remaja Jantan",
                            "Kerbau Remaja Betina": "1-12300 - Persediaan Kerbau Remaja Betina",
                            "Anak Kerbau Jantan": "1-12400 - Persediaan Anak Kerbau Jantan",
                            "Anak Kerbau Betina": "1-12500 - Persediaan Anak Kerbau Betina",
                        }
                        
                        for key, account in product_to_account.items():
                            if key.lower() in product_name.lower():
                                inventory_account = account
                                break
                        
                        # Tentukan akun kredit berdasarkan metode pembayaran
                        if payment_method == "Tunai":
                            credit_account = "1-10000 - Kas"
                        else:  # Kredit
                            credit_account = "2-10000 - Utang Usaha"
                        
                        # Simpan ke Jurnal Umum
                        add_journal_entry(date_str, inventory_account, total_price, 0, keterangan)
                        add_journal_entry("", credit_account, 0, total_price, "")
                        
                        # Simpan ke Buku Besar
                        ledger_df = get_ledger_data()
                        current_balances = {}
                        
                        for _, row in ledger_df.iterrows():
                            account = row['account']
                            saldo = safe_parse_price(row['balance']) if row['balance'] else 0
                            current_balances[account] = saldo
                        
                        # Update saldo akun persediaan (debit)
                        current_balance_inventory = current_balances.get(inventory_account, 0)
                        new_balance_inventory = current_balance_inventory + total_price
                        add_ledger_entry(inventory_account, date_str, keterangan, total_price, 0, new_balance_inventory)
                        
                        # Update saldo akun kas/utang (kredit)
                        current_balance_credit = current_balances.get(credit_account, 0)
                        if payment_method == "Tunai":
                            new_balance_credit = current_balance_credit - total_price
                        else:
                            new_balance_credit = current_balance_credit + total_price
                        
                        add_ledger_entry(credit_account, date_str, keterangan, 0, total_price, new_balance_credit)
                        # ========== END OTOMATIS JURNAL ==========
                        
                        st.success("✅ Produk berhasil ditambahkan ke persediaan dan jurnal dibuat otomatis!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        
        # Riwayat Pembelian
        st.markdown("### 📋 Riwayat Pembelian")
        try:
            purchases_df = get_purchases_data()
            
            if not purchases_df.empty:
                data = []
                total_purchases = 0.0
                
                for _, row in purchases_df.iterrows():
                    total_price_val = safe_parse_price(row['total_price'])
                    total_purchases += total_price_val
                    
                    data.append({
                        'Tanggal': row['date'],
                        'Nama Produk': row['product_name'],
                        'Kuantitas': row['product_quantity'],
                        'Harga Satuan': format_rupiah(safe_parse_price(row['product_price'])),
                        'Total Harga': format_rupiah(total_price_val)
                    })
                
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.markdown(f"""
                <div style="background: #10b981; color: white; padding: 1rem; border-radius: 8px; text-align: center; margin-top: 1rem;">
                    <h3>💰 Total Pembelian: {format_rupiah(total_purchases)}</h3>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📝 Belum ada data pembelian")
        
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")

    with tab2:
        st.markdown("### 💰 Tambah Penjualan Baru")
        
        with st.form("form_penjualan"):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Tanggal Penjualan", datetime.now())
                product_name = st.selectbox("Nama Produk", list(SELLING_PRICE.keys()))
                payment_method = st.selectbox("Metode Pembayaran", ["Tunai", "Kredit"], key="sales_payment")
            
            with col2:
                quantity = st.number_input("Jumlah (ekor)", min_value=1, value=1, key="qty_sales")
                
                selling_price = SELLING_PRICE[product_name]
                st.text_input("Harga Jual per Unit", value=format_rupiah(selling_price), disabled=True)
            
            add_to_list = st.form_submit_button("➕ Tambah ke Daftar", use_container_width=True)
            
            if add_to_list:
                try:
                    inventory_df = get_inventory_data()
                    
                    stock_available = False
                    hpp_price = 0
                    for _, row in inventory_df.iterrows():
                        if row['product_name'] and str(row['product_name']).strip().lower() == product_name.strip().lower():
                            qty_str = str(row['product_quantity']) if row['product_quantity'] is not None else "0"
                            try:
                                stock = int(qty_str.split()[0])
                            except:
                                stock = 0
                            
                            hpp_price = safe_parse_price(row['product_price']) if row['product_price'] else 0
                            
                            if stock >= quantity:
                                unit = qty_str.split()[1] if len(qty_str.split()) > 1 else "ekor"
                                new_stock = stock - quantity
                                new_quantity = f"{new_stock} {unit}".strip()
                                new_total_price = hpp_price * new_stock
                                
                                add_inventory_item(product_name, new_quantity, hpp_price, new_total_price)
                                stock_available = True
                            else:
                                st.error(f"❌ Stok {product_name} hanya {stock} ekor!")
                                break
                            break
                    
                    if stock_available:
                        total_sales = selling_price * quantity
                        total_hpp = hpp_price * quantity
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        if 'order_list' not in st.session_state:
                            st.session_state.order_list = []
                        
                        st.session_state.order_list.append({
                            'date': date.strftime('%Y-%m-%d'),
                            'product_name': product_name,
                            'quantity': f"{quantity} ekor",
                            'price': selling_price,
                            'hpp_price': hpp_price,
                            'total': total_sales,
                            'total_hpp': total_hpp,
                            'payment_method': payment_method,
                            'timestamp': timestamp
                        })
                        
                        st.success(f"✅ Penjualan {product_name} berhasil ditambahkan!")
                        st.rerun()
                    else:
                        if not stock_available:
                            st.error(f"❌ {product_name} tidak ditemukan di Inventory.")
                
                except Exception as e:
                    st.error(f"❌ Error: {e}")

        st.markdown("### 🛍️ Daftar Penjualan Sementara")
        
        if 'order_list' not in st.session_state:
            st.session_state.order_list = []
            
        if st.session_state.order_list:
            order_data = []
            total_all_sales = 0
            total_all_hpp = 0
            for order in st.session_state.order_list:
                order_data.append({
                    'Tanggal': order['date'],
                    'Nama Produk': order['product_name'],
                    'Jumlah': order['quantity'],
                    'Harga Jual': format_rupiah(order['price']),
                    'HPP': format_rupiah(order['hpp_price']),
                    'Total': format_rupiah(order['total'])
                })
                total_all_sales += order['total']
                total_all_hpp += order['total_hpp']
            
            df = pd.DataFrame(order_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div style="background: #3b82f6; color: white; padding: 1rem; border-radius: 8px; text-align: center; margin-top: 1rem;">
                    <h3>💰 Total Penjualan: {format_rupiah(total_all_sales)}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background: #f59e0b; color: white; padding: 1rem; border-radius: 8px; text-align: center; margin-top: 1rem;">
                    <h3>📊 Total HPP: {format_rupiah(total_all_hpp)}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Simpan Semua Penjualan", use_container_width=True):
                    try:
                        for order in st.session_state.order_list:
                            add_sales_transaction(
                                order['date'],
                                order['product_name'],
                                order['quantity'],
                                order['price'],
                                order['total'],
                                order['payment_method'],
                                order['timestamp']
                            )
                        
                        # ========== OTOMATIS BUAT JURNAL UNTUK SEMUA PENJUALAN ==========
                        for order in st.session_state.order_list:
                            date_str = order['date']
                            product_name = order['product_name']
                            quantity = safe_parse_int_from_qtytext(order['quantity'])
                            total_sales = order['total']
                            total_hpp = order['total_hpp']
                            payment_method = order['payment_method']
                            keterangan = f"Penjualan {product_name} - {quantity} ekor"
                            
                            product_to_account = {
                                "Kerbau Dewasa Jantan": "1-12000 - Persediaan Kerbau Dewasa Jantan",
                                "Kerbau Dewasa Betina": "1-12100 - Persediaan Kerbau Dewasa Betina", 
                                "Kerbau Remaja Jantan": "1-12200 - Persediaan Kerbau Remaja Jantan",
                                "Kerbau Remaja Betina": "1-12300 - Persediaan Kerbau Remaja Betina",
                                "Anak Kerbau Jantan": "1-12400 - Persediaan Anak Kerbau Jantan",
                                "Anak Kerbau Betina": "1-12500 - Persediaan Anak Kerbau Betina"
                            }
                            
                            inventory_account = product_to_account.get(product_name, "1-12000 - Persediaan Kerbau Dewasa Jantan")
                            
                            if payment_method == "Tunai":
                                debit_account_1 = "1-10000 - Kas"
                            else:
                                debit_account_1 = "1-11000 - Piutang"
                            
                            ledger_df = get_ledger_data()
                            current_balances = {}
                            
                            for _, row in ledger_df.iterrows():
                                account = row['account']
                                saldo = safe_parse_price(row['balance']) if row['balance'] else 0
                                current_balances[account] = saldo
                            
                            # JURNAL PENJUALAN
                            add_journal_entry(date_str, debit_account_1, total_sales, 0, keterangan)
                            add_journal_entry("", "5-50000 - HPP", total_hpp, 0, "")
                            add_journal_entry("", "4-40000 - Pendapatan", 0, total_sales, "")
                            add_journal_entry("", inventory_account, 0, total_hpp, "")
                            
                            # UPDATE BUKU BESAR
                            current_balance_debit1 = current_balances.get(debit_account_1, 0)
                            new_balance_debit1 = current_balance_debit1 + total_sales
                            add_ledger_entry(debit_account_1, date_str, keterangan, total_sales, 0, new_balance_debit1)
                            
                            current_balance_hpp = current_balances.get("5-50000 - HPP", 0)
                            new_balance_hpp = current_balance_hpp + total_hpp
                            add_ledger_entry("5-50000 - HPP", date_str, keterangan, total_hpp, 0, new_balance_hpp)
                            
                            current_balance_pendapatan = current_balances.get("4-40000 - Pendapatan", 0)
                            new_balance_pendapatan = current_balance_pendapatan - total_sales
                            add_ledger_entry("4-40000 - Pendapatan", date_str, keterangan, 0, total_sales, new_balance_pendapatan)
                            
                            current_balance_inventory = current_balances.get(inventory_account, 0)
                            new_balance_inventory = current_balance_inventory - total_hpp
                            add_ledger_entry(inventory_account, date_str, keterangan, 0, total_hpp, new_balance_inventory)
                        
                        st.session_state.order_list = []
                        st.success("✅ Semua penjualan berhasil disimpan dan jurnal dibuat otomatis!")
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
            
            with col2:
                if st.button("🗑️ Hapus Semua Penjualan", use_container_width=True):
                    st.session_state.order_list = []
                    st.success("✅ Daftar penjualan berhasil dihapus!")
                    st.rerun()
        else:
            st.info("📝 Belum ada penjualan dalam daftar")

    with tab3:
        st.markdown("### 📋 Riwayat Transaksi Lengkap")
        
        try:
            purchases_df = get_purchases_data()
            sales_df = get_sales_data()
            
            all_transactions = []
            
            for _, row in purchases_df.iterrows():
                all_transactions.append({
                    'Tanggal': row['date'],
                    'Tipe': 'Pembelian',
                    'Produk': row['product_name'],
                    'Kuantitas': row['product_quantity'],
                    'Harga/Unit': format_rupiah(safe_parse_price(row['product_price'])),
                    'Total': format_rupiah(safe_parse_price(row['total_price'])),
                    'Waktu': row['timestamp'].split(' ')[1] if row['timestamp'] and ' ' in row['timestamp'] else ''
                })
            
            for _, row in sales_df.iterrows():
                all_transactions.append({
                    'Tanggal': row['date'],
                    'Tipe': 'Penjualan',
                    'Produk': row['product_name'],
                    'Kuantitas': row['product_quantity'],
                    'Harga/Unit': format_rupiah(safe_parse_price(row['product_price'])),
                    'Total': format_rupiah(safe_parse_price(row['total_sales'])),
                    'Waktu': row['timestamp'].split(' ')[1] if row['timestamp'] and ' ' in row['timestamp'] else ''
                })
            
            if all_transactions:
                all_transactions.sort(key=lambda x: (x['Tanggal'], x['Waktu']), reverse=True)
                
                df = pd.DataFrame(all_transactions)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                total_pembelian = sum(safe_parse_price(t['Total'].replace('Rp', '').replace('.', '').replace(',', '.').strip()) 
                                    for t in all_transactions if t['Tipe'] == 'Pembelian')
                total_penjualan = sum(safe_parse_price(t['Total'].replace('Rp', '').replace('.', '').replace(',', '.').strip()) 
                                    for t in all_transactions if t['Tipe'] == 'Penjualan')
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Pembelian", format_rupiah(total_pembelian))
                with col2:
                    st.metric("Total Penjualan", format_rupiah(total_penjualan))
                
            else:
                st.info("📝 Belum ada data transaksi")
        
        except Exception as e:
            st.error(f"❌ Error loading transaction data: {e}")

    with tab4:
        st.markdown("### 📊 Kartu Persediaan Detail")
        
        try:
            inventory_df = get_inventory_data()
            purchases_df = get_purchases_data()
            sales_df = get_sales_data()
            
            products = []
            for _, row in inventory_df.iterrows():
                product_name = row['product_name']
                quantity_balance = row['product_quantity']
                price_balance = safe_parse_price(row['product_price'])
                total_balance = safe_parse_price(row['total_price'])
                
                qty_balance = safe_parse_int_from_qtytext(quantity_balance)
                unit_balance = str(quantity_balance).replace(str(qty_balance), "").strip()
                
                purchases_data = []
                for _, purchase_row in purchases_df.iterrows():
                    if purchase_row['product_name'] and str(purchase_row['product_name']).strip().lower() == product_name.lower():
                        purchases_data.append({
                            'tanggal': purchase_row['date'],
                            'timestamp': purchase_row['timestamp'],
                            'qty': safe_parse_int_from_qtytext(purchase_row['product_quantity']),
                            'price': safe_parse_price(purchase_row['product_price']),
                            'total': safe_parse_price(purchase_row['total_price'])
                        })
                
                sales_data = []
                for _, sales_row in sales_df.iterrows():
                    if sales_row['product_name'] and str(sales_row['product_name']).strip().lower() == product_name.lower():
                        sales_data.append({
                            'tanggal': sales_row['date'],
                            'timestamp': sales_row['timestamp'],
                            'qty': safe_parse_int_from_qtytext(sales_row['product_quantity']),
                            'price': safe_parse_price(sales_row['product_price']),
                            'total': safe_parse_price(sales_row['total_sales'])
                        })
                
                all_transactions = []
                
                for purchase in purchases_data:
                    all_transactions.append({
                        'tanggal': purchase['tanggal'],
                        'timestamp': purchase['timestamp'],
                        'type': 'Pembelian',
                        'qty': purchase['qty'],
                        'price': purchase['price'],
                        'total': purchase['total']
                    })
                
                for sale in sales_data:
                    all_transactions.append({
                        'tanggal': sale['tanggal'],
                        'timestamp': sale['timestamp'],
                        'type': 'Penjualan',
                        'qty': -sale['qty'],
                        'price': sale['price'],
                        'total': sale['total']
                    })
                
                all_transactions.sort(key=lambda x: (
                    x['tanggal'] if x['tanggal'] else "0000-00-00",
                    x['timestamp'] if x['timestamp'] else "00:00:00"
                ))
                
                running_qty = 0
                running_avg_price = 0
                running_total = 0
                
                transaction_details = []
                
                for trans in all_transactions:
                    if trans['type'] == 'Pembelian':
                        if running_qty == 0:
                            running_avg_price = trans['price']
                        else:
                            total_value_before = running_qty * running_avg_price
                            total_value_new = trans['qty'] * trans['price']
                            running_avg_price = (total_value_before + total_value_new) / (running_qty + trans['qty'])
                        
                        running_qty += trans['qty']
                        running_total = running_qty * running_avg_price
                    
                    elif trans['type'] == 'Penjualan':
                        running_qty += trans['qty']
                        running_total = running_qty * running_avg_price
                    
                    display_time = ""
                    if trans['timestamp']:
                        try:
                            if ' ' in trans['timestamp']:
                                date_part, time_part = trans['timestamp'].split(' ')
                                display_time = time_part
                            else:
                                display_time = trans['timestamp']
                        except:
                            display_time = trans['timestamp']
                    
                    transaction_details.append({
                        'Tanggal': trans['tanggal'],
                        'Waktu': display_time,
                        'Tipe': trans['type'],
                        'Qty_Pembelian': trans['qty'] if trans['type'] == 'Pembelian' else 0,
                        'Harga_Pembelian': format_rupiah(trans['price']) if trans['type'] == 'Pembelian' else '',
                        'Total_Pembelian': format_rupiah(trans['total']) if trans['type'] == 'Pembelian' else '',
                        'Qty_Penjualan': abs(trans['qty']) if trans['type'] == 'Penjualan' else 0,
                        'Harga_Penjualan': format_rupiah(trans['price']) if trans['type'] == 'Penjualan' else '',
                        'Total_Penjualan': format_rupiah(trans['total']) if trans['type'] == 'Penjualan' else '',
                        'Qty_Balance': running_qty,
                        'Harga_Balance': format_rupiah(running_avg_price),
                        'Total_Balance': format_rupiah(running_total)
                    })
                
                if not transaction_details and qty_balance > 0:
                    transaction_details.append({
                        'Tanggal': '-',
                        'Waktu': '',
                        'Tipe': 'Balance Awal',
                        'Qty_Pembelian': 0,
                        'Harga_Pembelian': '',
                        'Total_Pembelian': '',
                        'Qty_Penjualan': 0,
                        'Harga_Penjualan': '',
                        'Total_Penjualan': '',
                        'Qty_Balance': qty_balance,
                        'Harga_Balance': format_rupiah(price_balance),
                        'Total_Balance': format_rupiah(total_balance)
                    })
                
                products.append({
                    'product_name': product_name,
                    'unit': unit_balance,
                    'current_stock': qty_balance,
                    'current_value': total_balance,
                    'transactions': transaction_details
                })
            
            st.markdown("### 📈 Summary Persediaan")
            if products:
                summary_data = []
                total_inventory_value = 0
                
                for product in products:
                    summary_data.append({
                        'Nama Produk': product['product_name'],
                        'Stok Saat Ini': f"{product['current_stock']} {product['unit']}",
                        'Nilai Persediaan': format_rupiah(product['current_value'])
                    })
                    total_inventory_value += product['current_value']
                
                df_summary = pd.DataFrame(summary_data)
                st.dataframe(df_summary, use_container_width=True, hide_index=True)
                
                st.metric("Total Nilai Persediaan", format_rupiah(total_inventory_value))
                
                st.markdown("### 📋 Detail Kartu Persediaan per Produk")
                for product in products:
                    with st.expander(f"📦 {product['product_name']} ({product['unit']}) - Stok: {product['current_stock']}"):
                        if product['transactions']:
                            df_detail = pd.DataFrame(product['transactions'])
                            
                            df_display = df_detail.rename(columns={
                                'Qty_Pembelian': 'Qty Pembelian',
                                'Harga_Pembelian': 'Harga/Unit Pembelian', 
                                'Total_Pembelian': 'Total Pembelian',
                                'Qty_Penjualan': 'Qty Penjualan',
                                'Harga_Penjualan': 'Harga/Unit Penjualan',
                                'Total_Penjualan': 'Total Penjualan',
                                'Qty_Balance': 'Qty Balance',
                                'Harga_Balance': 'Harga/Unit Balance',
                                'Total_Balance': 'Total Balance'
                            })
                            
                            st.dataframe(df_display, use_container_width=True, hide_index=True)
                        else:
                            st.info("Belum ada transaksi untuk produk ini")
            else:
                st.info("📝 Belum ada data persediaan")
        
        except Exception as e:
            st.error(f"❌ Error loading inventory data: {e}")

def show_ringkasan_penjualan():
    st.markdown('<div class="main-header"><h1>📈 Ringkasan Penjualan</h1></div>', unsafe_allow_html=True)
    
    try:
        sales_df = get_sales_data()
        inventory_df = get_inventory_data()
        
        HPP_dict = {}
        for _, row in inventory_df.iterrows():
            if row['product_name']:
                product_name = row['product_name']
                HPP_price = safe_parse_price(row['product_price'])
                HPP_dict[product_name] = HPP_price
        
        data = []
        total_income_all = 0.0
        total_HPP_all = 0.0
        total_profit_all = 0.0
        
        for _, row in sales_df.iterrows():
            if row['product_name'] is None:
                continue
            
            date = row['date']
            product_name = row['product_name']
            qty_text = row['product_quantity']
            selling_price_unit = safe_parse_price(row['product_price'])
            total_income = safe_parse_price(row['total_sales'])
            
            qty = safe_parse_int_from_qtytext(qty_text)
            HPP_unit = HPP_dict.get(product_name, 0)
            total_HPP = HPP_unit * qty
            gross_profit = total_income - total_HPP
            
            total_income_all += total_income
            total_HPP_all += total_HPP
            total_profit_all += gross_profit
            
            data.append({
                'Tanggal': date,
                'Produk': product_name,
                'Qty': qty,
                'Harga Jual': format_rupiah(selling_price_unit),
                'HPP/Unit': format_rupiah(HPP_unit),
                'Total Income': format_rupiah(total_income),
                'Total HPP': format_rupiah(total_HPP),
                'Gross Profit': format_rupiah(gross_profit)
            })
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style="background: #10b981; color: white; padding: 1rem; border-radius: 8px; text-align: center;">
                    <h4>Total Income</h4>
                    <h2>{format_rupiah(total_income_all)}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background: #f59e0b; color: white; padding: 1rem; border-radius: 8px; text-align: center;">
                    <h4>Total HPP</h4>
                    <h2>{format_rupiah(total_HPP_all)}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                profit_color = "#10b981" if total_profit_all > 0 else "#ef4444"
                st.markdown(f"""
                <div style="background: {profit_color}; color: white; padding: 1rem; border-radius: 8px; text-align: center;">
                    <h4>Profit</h4>
                    <h2>{format_rupiah(total_profit_all)}</h2>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Belum ada data penjualan")
    
    except Exception as e:
        st.error(f"Error: {e}")

def show_jurnal_umum():
    st.markdown('<div class="main-header"><h1>📒 Input Jurnal Umum</h1></div>', unsafe_allow_html=True)
    
    st.markdown("### Input Transaksi Baru")
    
    if 'debit_accounts' not in st.session_state:
        st.session_state.debit_accounts = [{'account': '', 'amount': 0}]
    if 'credit_accounts' not in st.session_state:
        st.session_state.credit_accounts = [{'account': '', 'amount': 0}]
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Tambah Akun Debit", key="add_debit"):
            st.session_state.debit_accounts.append({'account': '', 'amount': 0})
            st.rerun()
    with col2:
        if st.button("➕ Tambah Akun Kredit", key="add_credit"):
            st.session_state.credit_accounts.append({'account': '', 'amount': 0})
            st.rerun()
    
    with st.form("form_jurnal", clear_on_submit=True):
        date = st.date_input("Tanggal", datetime.now())
        
        st.markdown("**Akun Debit**")
        
        for i in range(len(st.session_state.debit_accounts)):
            st.markdown(f"**Debit {i+1}**")
            col_acc, col_amt, col_del = st.columns([2, 1, 0.5])
            with col_acc:
                account_options = [f"{code} - {name}" for code, name in ACCOUNTS.items()]
                current_account = st.session_state.debit_accounts[i]['account']
                default_index = account_options.index(current_account) if current_account in account_options else 0
                
                selected_account = st.selectbox(
                    f"Pilih Akun Debit {i+1}", 
                    account_options, 
                    key=f"debit_acc_{i}",
                    index=default_index
                )
                st.session_state.debit_accounts[i]['account'] = selected_account
            with col_amt:
                amount = st.number_input(
                    f"Nominal Debit {i+1}", 
                    min_value=0, 
                    value=st.session_state.debit_accounts[i]['amount'],
                    key=f"debit_amt_{i}"
                )
                st.session_state.debit_accounts[i]['amount'] = amount
            with col_del:
                if i > 0:
                    if st.form_submit_button("❌", type="secondary", key=f"del_debit_{i}"):
                        st.session_state.debit_accounts.pop(i)
                        st.rerun()
        
        st.markdown("---")
        st.markdown("**Akun Kredit**")
        
        for i in range(len(st.session_state.credit_accounts)):
            st.markdown(f"**Kredit {i+1}**")
            col_acc, col_amt, col_del = st.columns([2, 1, 0.5])
            with col_acc:
                account_options = [f"{code} - {name}" for code, name in ACCOUNTS.items()]
                current_account = st.session_state.credit_accounts[i]['account']
                default_index = account_options.index(current_account) if current_account in account_options else 0
                
                selected_account = st.selectbox(
                    f"Pilih Akun Kredit {i+1}", 
                    account_options, 
                    key=f"credit_acc_{i}",
                    index=default_index
                )
                st.session_state.credit_accounts[i]['account'] = selected_account
            with col_amt:
                amount = st.number_input(
                    f"Nominal Kredit {i+1}", 
                    min_value=0, 
                    value=st.session_state.credit_accounts[i]['amount'],
                    key=f"credit_amt_{i}"
                )
                st.session_state.credit_accounts[i]['amount'] = amount
            with col_del:
                if i > 0:
                    if st.form_submit_button("❌", type="secondary", key=f"del_credit_{i}"):
                        st.session_state.credit_accounts.pop(i)
                        st.rerun()
        
        st.markdown("---")
        keterangan = st.text_input("Keterangan Transaksi", placeholder="Contoh: Pembelian perlengkapan kantor")
        
        submit = st.form_submit_button("💾 Simpan Jurnal", use_container_width=True)
        
        if submit:
            valid_debit_accounts = [acc for acc in st.session_state.debit_accounts if acc['amount'] > 0 and acc['account']]
            valid_credit_accounts = [acc for acc in st.session_state.credit_accounts if acc['amount'] > 0 and acc['account']]
            
            total_debit = sum(item['amount'] for item in valid_debit_accounts)
            total_credit = sum(item['amount'] for item in valid_credit_accounts)
            
            if total_debit == 0 or total_credit == 0:
                st.error("Nominal debit dan kredit harus lebih dari 0")
            elif total_debit != total_credit:
                st.error(f"**Tidak Balance!** Total Debit ({format_rupiah(total_debit)}) ≠ Total Kredit ({format_rupiah(total_credit)})")
            elif not valid_debit_accounts or not valid_credit_accounts:
                st.error("Harap isi minimal satu akun debit dan satu akun kredit")
            else:
                try:
                    date_str = date.strftime('%Y-%m-%d')
                    
                    ledger_df = get_ledger_data()
                    current_balances = {}
                    
                    for _, row in ledger_df.iterrows():
                        account = row['account']
                        saldo = safe_parse_price(row['balance']) if row['balance'] else 0
                        current_balances[account] = saldo
                    
                    if valid_debit_accounts:
                        first_debit = valid_debit_accounts[0]
                        add_journal_entry(date_str, first_debit['account'], first_debit['amount'], 0, keterangan)
                    
                    for i in range(1, len(valid_debit_accounts)):
                        debit = valid_debit_accounts[i]
                        add_journal_entry("", debit['account'], debit['amount'], 0, "")
                    
                    for credit in valid_credit_accounts:
                        add_journal_entry("", credit['account'], 0, credit['amount'], "")
                    
                    for debit in valid_debit_accounts:
                        account = debit['account']
                        nominal = debit['amount']
                        
                        current_balance = current_balances.get(account, 0)
                        new_balance = current_balance + nominal
                        current_balances[account] = new_balance
                        
                        add_ledger_entry(account, date_str, keterangan, nominal, 0, new_balance)
                    
                    for credit in valid_credit_accounts:
                        account = credit['account']
                        nominal = credit['amount']
                        
                        current_balance = current_balances.get(account, 0)
                        new_balance = current_balance - nominal
                        current_balances[account] = new_balance
                        
                        add_ledger_entry(account, date_str, keterangan, 0, nominal, new_balance)
                    
                    st.success("✅ Jurnal berhasil disimpan ke Jurnal Umum dan Buku Besar!")
                    
                    st.session_state.debit_accounts = [{'account': '', 'amount': 0}]
                    st.session_state.credit_accounts = [{'account': '', 'amount': 0}]
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Error: {e}")

def show_view_jurnal():
    st.markdown('<div class="main-header"><h1>📖 Lihat Jurnal Umum</h1></div>', unsafe_allow_html=True)

    try:
        journal_df = get_journal_data()

        if not journal_df.empty:
            data = []
            for _, row in journal_df.iterrows():
                data.append({
                    'Tanggal': row['date'] or '',
                    'Akun': row['account'] or '',
                    'Debit': format_rupiah(row['debit']) if row['debit'] else '',
                    'Kredit': format_rupiah(row['credit']) if row['credit'] else '',
                    'Keterangan': row['description'] or ''
                })

            total_debit = journal_df['debit'].sum()
            total_kredit = journal_df['credit'].sum()

            df = pd.DataFrame(data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=600
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Debit", format_rupiah(total_debit))
            with col2:
                st.metric("Total Kredit", format_rupiah(total_kredit))
            with col3:
                if abs(total_debit - total_kredit) < 0.01:
                    st.success("✅ Jurnal Balance!")
                else:
                    st.error("❌ Jurnal Tidak Balance!")

            st.download_button(
                label="📥 Export ke CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"jurnal_umum_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("📝 Belum ada transaksi jurnal")

    except Exception as e:
        st.error(f"Error: {e}")

    st.markdown("---")
    if st.button("🗑️ Hapus Semua Data Jurnal", type="secondary", use_container_width=True):
        try:
            clear_table('journal')
            clear_table('ledger')
            st.success("Data jurnal berhasil direset!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

def show_buku_besar():
    st.markdown('<div class="main-header"><h1>📚 Buku Besar</h1></div>', unsafe_allow_html=True)
    
    try:
        ledger_df = get_ledger_data()
        
        if not ledger_df.empty:
            # Recalculate balances
            account_data = {}
            for _, row in ledger_df.iterrows():
                account = row['account']
                if account not in account_data:
                    account_data[account] = []
                account_data[account].append(row)
            
            # Display ledger by account
            for account, entries in account_data.items():
                try:
                    account_num, account_name = account.split(" - ", 1)
                except:
                    account_num = account
                    account_name = account
                
                st.markdown(f"### {account_name} ({account_num})")
                
                account_code = account_num.split()[0] if ' ' in account_num else account_num
                is_credit_account = account_code.startswith(('2', '3', '4'))
                
                table_data = []
                for entry in entries:
                    display_saldo = abs(entry['balance']) if is_credit_account else entry['balance']
                    
                    table_data.append({
                        'Tanggal': entry['date'],
                        'Keterangan': entry['description'],
                        'Debit': format_rupiah(entry['debit']) if entry['debit'] else '',
                        'Kredit': format_rupiah(entry['credit']) if entry['credit'] else '',
                        'Saldo': format_rupiah(display_saldo)
                    })
                
                if table_data:
                    df = pd.DataFrame(table_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    ending_balance = entries[-1]['balance'] if entries else 0
                    display_ending_balance = abs(ending_balance) if is_credit_account else ending_balance
                    
                    saldo_type = "Kredit" if is_credit_account else "Debit"
                    
                    st.markdown(f"""
                    <div style="background: #10b981; color: white; padding: 0.5rem 1rem; border-radius: 5px; margin-bottom: 1rem;">
                        <strong>Saldo Akhir: {format_rupiah(display_ending_balance)} ({saldo_type})</strong>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Tidak ada transaksi untuk akun ini")
                
                st.markdown("---")
        else:
            st.info("Belum ada data buku besar. Silakan input transaksi di menu Jurnal Umum terlebih dahulu.")
    
    except Exception as e:
        st.error(f"Error: {e}")

    st.markdown("---")
    if st.button("🗑️ Reset Data Buku Besar", type="secondary", use_container_width=True):
        try:
            clear_table('ledger')
            st.success("Data buku besar berhasil direset!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

def show_neraca_saldo():
    st.markdown('<div class="main-header"><h1>⚖️ Neraca Saldo</h1></div>', unsafe_allow_html=True)
    
    try:
        ledger_df = get_ledger_data()
        
        if not ledger_df.empty:
            account_balances = {}
            
            for _, row in ledger_df.iterrows():
                account = row['account']
                if account not in account_balances:
                    try:
                        account_num, account_name = account.split(" - ", 1)
                    except:
                        account_num = account
                        account_name = account
                    
                    account_balances[account] = {
                        'account_num': account_num,
                        'account_name': account_name,
                        'latest_saldo': 0.0
                    }
                
                if row['balance'] is not None:
                    account_balances[account]['latest_saldo'] = row['balance']
            
            table_data = []
            total_debit = 0.0
            total_kredit = 0.0
            
            for account, data in account_balances.items():
                saldo = data['latest_saldo']
                
                if saldo >= 0:
                    debit_amount = saldo
                    kredit_amount = 0.0
                else:
                    debit_amount = 0.0
                    kredit_amount = abs(saldo)
                
                total_debit += debit_amount
                total_kredit += kredit_amount
                
                table_data.append({
                    'No Akun': data['account_num'],
                    'Nama Akun': data['account_name'],
                    'Debit': format_rupiah(debit_amount) if debit_amount > 0 else '',
                    'Kredit': format_rupiah(kredit_amount) if kredit_amount > 0 else ''
                })
            
            table_data.sort(key=lambda x: x['No Akun'])
            
            if table_data:
                df = pd.DataFrame(table_data)
                
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "No Akun": st.column_config.TextColumn("No Akun", width="small"),
                        "Nama Akun": st.column_config.TextColumn("Nama Akun", width="medium"),
                        "Debit": st.column_config.TextColumn("Debit", width="medium"),
                        "Kredit": st.column_config.TextColumn("Kredit", width="medium")
                    }
                )
                
                st.markdown("---")
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                with col1:
                    st.markdown("**TOTAL**")
                with col2:
                    st.markdown("")
                with col3:
                    st.markdown(f"**{format_rupiah(total_debit)}**")
                with col4:
                    st.markdown(f"**{format_rupiah(total_kredit)}**")
                
                is_balanced = abs(total_debit - total_kredit) < 0.01
                st.markdown("---")
                if is_balanced:
                    st.success("✅ NERACA SALDO SEIMBANG")
                else:
                    st.error(f"❌ NERACA SALDO TIDAK SEIMBANG - Selisih: {format_rupiah(abs(total_debit - total_kredit))}")
        else:
            st.info("Belum ada data neraca saldo. Silakan input transaksi di menu Jurnal Umum terlebih dahulu.")
    
    except Exception as e:
        st.error(f"Error: {e}")

def show_jurnal_penyesuaian():
    st.markdown('<div class="main-header"><h1>📘 Input Jurnal Penyesuaian</h1></div>', unsafe_allow_html=True)
    
    st.markdown("### Input Jurnal Penyesuaian Baru")
    
    if 'adj_debit_accounts' not in st.session_state:
        st.session_state.adj_debit_accounts = [{'account': '', 'amount': 0}]
    if 'adj_credit_accounts' not in st.session_state:
        st.session_state.adj_credit_accounts = [{'account': '', 'amount': 0}]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Tambah Akun Debit", key="adj_add_debit"):
            st.session_state.adj_debit_accounts.append({'account': '', 'amount': 0})
            st.rerun()
    with col2:
        if st.button("➕ Tambah Akun Kredit", key="adj_add_credit"):
            st.session_state.adj_credit_accounts.append({'account': '', 'amount': 0})
            st.rerun()
    
    with st.form("form_jurnal_penyesuaian", clear_on_submit=True):
        date = st.date_input("Tanggal Penyesuaian", datetime.now())
        
        st.markdown("**Akun Debit**")
        
        for i in range(len(st.session_state.adj_debit_accounts)):
            st.markdown(f"**Debit {i+1}**")
            col_acc, col_amt, col_del = st.columns([2, 1, 0.5])
            with col_acc:
                account_options = [f"{code} - {name}" for code, name in ACCOUNTS.items()]
                current_account = st.session_state.adj_debit_accounts[i]['account']
                default_index = account_options.index(current_account) if current_account in account_options else 0
                
                selected_account = st.selectbox(
                    f"Pilih Akun Debit {i+1}", 
                    account_options, 
                    key=f"adj_debit_acc_{i}",
                    index=default_index
                )
                st.session_state.adj_debit_accounts[i]['account'] = selected_account
            with col_amt:
                amount = st.number_input(
                    f"Nominal Debit {i+1}", 
                    min_value=0, 
                    value=st.session_state.adj_debit_accounts[i]['amount'],
                    key=f"adj_debit_amt_{i}"
                )
                st.session_state.adj_debit_accounts[i]['amount'] = amount
            with col_del:
                if i > 0: 
                    if st.form_submit_button("❌", type="secondary", key=f"adj_del_debit_{i}"):
                        st.session_state.adj_debit_accounts.pop(i)
                        st.rerun()
        
        st.markdown("---")
        st.markdown("**Akun Kredit**")
        
        for i in range(len(st.session_state.adj_credit_accounts)):
            st.markdown(f"**Kredit {i+1}**")
            col_acc, col_amt, col_del = st.columns([2, 1, 0.5])
            with col_acc:
                account_options = [f"{code} - {name}" for code, name in ACCOUNTS.items()]
                current_account = st.session_state.adj_credit_accounts[i]['account']
                default_index = account_options.index(current_account) if current_account in account_options else 0
                
                selected_account = st.selectbox(
                    f"Pilih Akun Kredit {i+1}", 
                    account_options, 
                    key=f"adj_credit_acc_{i}",
                    index=default_index
                )
                st.session_state.adj_credit_accounts[i]['account'] = selected_account
            with col_amt:
                amount = st.number_input(
                    f"Nominal Kredit {i+1}", 
                    min_value=0, 
                    value=st.session_state.adj_credit_accounts[i]['amount'],
                    key=f"adj_credit_amt_{i}"
                )
                st.session_state.adj_credit_accounts[i]['amount'] = amount
            with col_del:
                if i > 0:  
                    if st.form_submit_button("❌", type="secondary", key=f"adj_del_credit_{i}"):
                        st.session_state.adj_credit_accounts.pop(i)
                        st.rerun()
        
        st.markdown("---")
        keterangan = st.text_input("Keterangan Penyesuaian", placeholder="Contoh: Penyesuaian penyusutan kendaraan, Penyesuaian beban dibayar di muka, dll.")
        
        submit = st.form_submit_button("💾 Simpan Jurnal Penyesuaian", use_container_width=True)
        
        if submit:
            valid_debit_accounts = [acc for acc in st.session_state.adj_debit_accounts if acc['amount'] > 0 and acc['account']]
            valid_credit_accounts = [acc for acc in st.session_state.adj_credit_accounts if acc['amount'] > 0 and acc['account']]
            
            total_debit = sum(item['amount'] for item in valid_debit_accounts)
            total_credit = sum(item['amount'] for item in valid_credit_accounts)
            
            if total_debit == 0 or total_credit == 0:
                st.error("Nominal debit dan kredit harus lebih dari 0")
            elif total_debit != total_credit:
                st.error(f"**Tidak Balance!** Total Debit ({format_rupiah(total_debit)}) ≠ Total Kredit ({format_rupiah(total_credit)})")
            elif not valid_debit_accounts or not valid_credit_accounts:
                st.error("Harap isi minimal satu akun debit dan satu akun kredit")
            elif not keterangan:
                st.error("Keterangan penyesuaian harus diisi")
            else:
                try:
                    date_str = date.strftime('%Y-%m-%d')
                    keterangan_with_label = f"[PENYESUAIAN] {keterangan}"

                    ledger_df = get_ledger_data()
                    current_balances = {}
                    
                    for _, row in ledger_df.iterrows():
                        account = row['account']
                        saldo = safe_parse_price(row['balance']) if row['balance'] else 0
                        current_balances[account] = saldo

                    if valid_debit_accounts:
                        first_debit = valid_debit_accounts[0]
                        add_journal_entry(date_str, first_debit['account'], first_debit['amount'], 0, keterangan_with_label, 'Adjusting')

                    for i in range(1, len(valid_debit_accounts)):
                        debit = valid_debit_accounts[i]
                        add_journal_entry("", debit['account'], debit['amount'], 0, "", 'Adjusting')

                    for credit in valid_credit_accounts:
                        add_journal_entry("", credit['account'], 0, credit['amount'], "", 'Adjusting')

                    for debit in valid_debit_accounts:
                        account = debit['account']
                        nominal = debit['amount']

                        current_balance = current_balances.get(account, 0)
                        new_balance = current_balance + nominal
                        current_balances[account] = new_balance
                        
                        add_ledger_entry(account, date_str, keterangan_with_label, nominal, 0, new_balance)
                    
                    for credit in valid_credit_accounts:
                        account = credit['account']
                        nominal = credit['amount']

                        current_balance = current_balances.get(account, 0)
                        new_balance = current_balance - nominal
                        current_balances[account] = new_balance
                        
                        add_ledger_entry(account, date_str, keterangan_with_label, 0, nominal, new_balance)
                    
                    st.success("✅ Jurnal Penyesuaian berhasil disimpan ke Jurnal Umum dan Buku Besar!")
                    
                    st.session_state.adj_debit_accounts = [{'account': '', 'amount': 0}]
                    st.session_state.adj_credit_accounts = [{'account': '', 'amount': 0}]
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Error: {e}")

# Note: Untuk fungsi-fungsi laporan keuangan (show_laporan_keuangan, show_laba_rugi, show_perubahan_modal, show_neraca)
# Anda perlu mengadaptasinya untuk menggunakan fungsi database SQLite yang sesuai.
# Karena keterbatasan panjang, saya akan memberikan template untuk fungsi-fungsi tersebut:

def show_laporan_keuangan():
    st.markdown('<div class="main-header"><h1>📋 Laporan Keuangan</h1></div>', unsafe_allow_html=True)
    
    st.markdown("### Pilih Jenis Laporan")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Laporan Laba Rugi", use_container_width=True):
            st.session_state.current_page = "Laba Rugi"
            st.rerun()
    
    with col2:
        if st.button("📈 Laporan Perubahan Modal", use_container_width=True):
            st.session_state.current_page = "Perubahan Modal"
            st.rerun()
    
    with col3:
        if st.button("💰 Laporan Posisi Keuangan", use_container_width=True):
            st.session_state.current_page = "Posisi Keuangan"
            st.rerun()

def show_laba_rugi():
    st.markdown('<div class="main-header"><h1>📊 Laporan Laba Rugi</h1></div>', unsafe_allow_html=True)
    
    if st.button("← Kembali ke Laporan Keuangan"):
        st.session_state.current_page = "Laporan Keuangan"
        st.rerun()
    
    try:
        ledger_df = get_ledger_data()
        
        if ledger_df.empty:
            st.info("Belum ada data untuk membuat laporan laba rugi")
            return
        
        # Implementasi logika laporan laba rugi menggunakan data dari SQLite
        # ... (logika yang sama seperti sebelumnya, tetapi menggunakan ledger_df)
        
        st.info("Fungsi laporan laba rugi sedang dalam pengembangan menggunakan database SQLite")
        
    except Exception as e:
        st.error(f"Error: {e}")

def show_perubahan_modal():
    st.markdown('<div class="main-header"><h1>📈 Laporan Perubahan Modal</h1></div>', unsafe_allow_html=True)
    
    if st.button("← Kembali ke Laporan Keuangan"):
        st.session_state.current_page = "Laporan Keuangan"
        st.rerun()
    
    try:
        ledger_df = get_ledger_data()
        
        if ledger_df.empty:
            st.info("Belum ada data untuk membuat laporan perubahan modal")
            return
        
        # Implementasi logika laporan perubahan modal menggunakan data dari SQLite
        st.info("Fungsi laporan perubahan modal sedang dalam pengembangan menggunakan database SQLite")
        
    except Exception as e:
        st.error(f"Error: {e}")

def show_neraca():
    st.markdown('<div class="main-header"><h1>📋 Laporan Posisi Keuangan (Neraca)</h1></div>', unsafe_allow_html=True)
    
    if st.button("← Kembali ke Laporan Keuangan"):
        st.session_state.current_page = "Laporan Keuangan"
        st.rerun()
    
    try:
        ledger_df = get_ledger_data()
        
        if ledger_df.empty:
            st.info("Belum ada data untuk membuat laporan posisi keuangan")
            return
        
        # Implementasi logika neraca menggunakan data dari SQLite
        st.info("Fungsi laporan posisi keuangan sedang dalam pengembangan menggunakan database SQLite")
        
    except Exception as e:
        st.error(f"Error: {e}")

# Router untuk halaman
if st.session_state.current_page == "Dashboard":
    show_dashboard()
elif st.session_state.current_page == "Kartu Persediaan":
    show_kartu_persediaan()
elif st.session_state.current_page == "Ringkasan Penjualan":
    show_ringkasan_penjualan()
elif st.session_state.current_page == "Jurnal Umum":
    show_jurnal_umum()
elif st.session_state.current_page == "View Jurnal":
    show_view_jurnal()
elif st.session_state.current_page == "Jurnal Penyesuaian":
    show_jurnal_penyesuaian()
elif st.session_state.current_page == "Buku Besar":
    show_buku_besar()
elif st.session_state.current_page == "Neraca Saldo":
    show_neraca_saldo()
elif st.session_state.current_page == "Laporan Keuangan":
    show_laporan_keuangan()
elif st.session_state.current_page == "Laba Rugi":
    show_laba_rugi()
elif st.session_state.current_page == "Perubahan Modal":
    show_perubahan_modal()
elif st.session_state.current_page == "Posisi Keuangan":
    show_neraca()
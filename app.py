"""
MateShop — Aplicacion Streamlit + PostgreSQL
============================================
Frontend: Streamlit
Backend:  PostgreSQL (psycopg2)

Ejecutar:
    streamlit run app.py
"""
import base64 #MAXI
import os
import streamlit as st
import psycopg2
import psycopg2.extras 
from psycopg2 import OperationalError, errors
from dotenv import load_dotenv
from datetime import datetime, timedelta
import hashlib
import hmac
import html
import uuid



load_dotenv()
#os.environ["DB_HOST"] = "localhost"
#os.environ["DB_PORT"] = "5432"
#os.environ["DB_NAME"] = "mateshop"
#os.environ["DB_USER"] = "postgres"
#os.environ["DB_PASSWORD"] = "fELIPEALIAGA2008"
#---------------------
#FUNCIONES DE UTILIDAD PARA IMAGENES MAXI
#---------------------
def get_base64_favicon(path):
    if not os.path.exists(path):
        path = "images/logo_mate.jpeg"  # imagen por defecto

    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def get_base64(img_file):
    with open(img_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

# HEADER + HERO
def header_hero(image_file):

    img = get_base64(image_file)

    header_html = f"""
    <style>

    /* Quitar márgenes laterales */
    .block-container {{
        padding-top: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
        max-width: 100%;
    }}

    /* Barra superior */
    .top-bar {{
        background-color: #4b5d00;
        height: 60px;
        display: flex;
        align-items: center;
        padding-left: 40px;
    }}

    /* Texto logo */
    .logo-text {{
        color: white;
        font-size: 28px;
        font-weight: bold;
        font-style: italic;
        font-family: sans-serif;
    }}

    /* Hero */
    .hero {{
        background-image: url("data:image/png;base64,{img}");
        height: 497px;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    </style>

    <div class="top-bar">
        <div class="logo-text">
            MATIOLI
        </div>
    </div>

    <div class="hero"></div>
    """

    st.markdown(header_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONFIGURACION DE PaGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MateShop",
    page_icon="/images/logo_mate.jpeg",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS PERSONALIZADO
# ─────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap');

            
    
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
    }
    
    .metric-card {
        background: #F5F0E8;
        border: 1px solid rgba(107,79,42,0.15);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
    }
    .metric-card .num  { font-family: 'Playfair Display', serif; font-size: 2rem; color: #2A1A08; }
    .metric-card .label{ font-size: 0.78rem; color: #7A6347; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

    .product-card {
        background: white;
        border: 1px solid rgba(107,79,42,0.12);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: box-shadow 0.2s;
    }
    .product-card:hover { box-shadow: 0 4px 20px rgba(42,26,8,0.1); }

    .tag {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .tag-premium  { background: #6B4F2A; color: white; }
    .tag-popular  { background: #7A9E45; color: white; }
    .tag-clasico  { background: #EDE5D0; color: #6B4F2A; border: 1px solid rgba(107,79,42,0.2); }
    .tag-edicion  { background: #B85C28; color: white; }
    .tag-accesorio{ background: #B8C9A3; color: #2A1A08; }

    .stock-ok   { color: #3D6B3A; font-weight: 500; }
    .stock-low  { color: #B85C28; font-weight: 500; }
    .stock-out  { color: #999;    font-weight: 500; }

    .alert-success { background:#EAF3DE; border:1px solid #B8C9A3; border-radius:8px; padding:0.8rem 1rem; color:#3D6B3A; }
    .alert-error   { background:#FAECE7; border:1px solid #F5C4B3; border-radius:8px; padding:0.8rem 1rem; color:#B85C28; }
    .alert-info    { background:#E6F1FB; border:1px solid #B5D4F4; border-radius:8px; padding:0.8rem 1rem; color:#185FA5; }

    .section-label {
        font-size: 0.72rem; letter-spacing: 2.5px;
        text-transform: uppercase; color: #B85C28;
        margin-bottom: 0.4rem;
    }

    div[data-testid="stSidebarContent"] {
        background: #2A1A08;
        padding-top: 1rem;
    }
    div[data-testid="stSidebarContent"] * { color: white !important; }
    div[data-testid="stSidebarContent"] .stRadio label { color: rgba(255,255,255,0.85) !important; }

    .stButton > button {
        background: #3D6B3A;
        color: white;
        border: none;
        border-radius: 8px;
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
        transition: background 0.2s;
    }
    .stButton > button:hover { background: #6B4F2A; border: none; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    
    /* TARJETA PROMOCIONAL */
    
    .promo-card {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(0,0,0,0.08);
        transition: 0.2s;
        margin-bottom: 25px;
    }
    
    .promo-card:hover {
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    /* IMAGEN GRANDE */
    
    .promo-image {
        width: 100%;
        height: 260px;
        overflow: hidden;
        background: #f5f0e8;
    }
    
    .promo-image img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    /* CONTENIDO */
    
    .promo-content {
        padding: 15px;
    }
    
    /* TAG */
    
    .promo-tag {
        font-size: 12px;
        text-transform: uppercase;
        color: #B85C28;
        margin-bottom: 6px;
    }
    
    /* TITULO */
    
    .promo-title {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    /* DESCRIPCION */
    
    .promo-description {
        font-size: 13px;
        color: #777;
        margin-bottom: 10px;
    }
    
    /* PRECIO */
    
    .promo-price {
        font-size: 22px;
        font-weight: bold;
        color: #2A1A08;
    }
    
    /* STOCK */
    
    .promo-stock {
        margin-top: 5px;
    }

    .detail-shell {
        padding: 1.5rem 2rem 2.5rem;
        background: #FBF8F2;
    }

    .detail-topline {
        color: #7A6347;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }

    .detail-photo {
        background: #F5F0E8;
        border: 1px solid rgba(107,79,42,0.12);
        border-radius: 10px;
        min-height: 520px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }

    .detail-photo img {
        max-width: 100%;
        max-height: 480px;
        object-fit: contain;
        border-radius: 8px;
    }

    .detail-info h1 {
        color: #2A1A08;
        font-size: 2rem;
        line-height: 1.15;
        margin: 0 0 0.75rem;
    }

    .detail-description {
        color: #5C4A34;
        font-size: 1rem;
        line-height: 1.6;
        margin-top: 1rem;
    }

    .detail-paybox {
        background: white;
        border: 1px solid rgba(107,79,42,0.18);
        border-radius: 10px;
        padding: 1.4rem;
        box-shadow: 0 10px 30px rgba(42,26,8,0.08);
    }

    .pay-label {
        color: #7A6347;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.2rem;
    }

    .pay-price {
        color: #2A1A08;
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .pay-note {
        color: #3D6B3A;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    .pay-section {
        border-top: 1px solid rgba(107,79,42,0.14);
        padding-top: 1rem;
        margin-top: 1rem;
        color: #2A1A08;
    }

    .pay-method {
        background: #F5F0E8;
        border: 1px solid rgba(107,79,42,0.16);
        border-radius: 8px;
        padding: 0.7rem 0.9rem;
        margin-top: 0.5rem;
        color: #2A1A08;
    }

    .detail-back {
        margin-bottom: 1rem;
    }
    
    </style>
    """, unsafe_allow_html=True)

 #maxi

# ─────────────────────────────────────────────
# CONEXION A BASE DE DATOS
# ─────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def get_connection():
    """
    Crea un pool de conexion a PostgreSQL.
    Lee credenciales desde variables de entorno (.env).
    """
    try:
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            conn = psycopg2.connect(
                database_url,
                sslmode=os.getenv("DB_SSLMODE", "require"),
                connect_timeout=5,
            )
            conn.autocommit = False
            return conn

        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "mateshop"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            sslmode=os.getenv("DB_SSLMODE", "prefer"),
            connect_timeout=5,
        )
        conn.autocommit = False
        return conn
    except OperationalError as e:
        st.error(f"❌ No se pudo conectar a PostgreSQL: {e}")
        st.info("Verifica que PostgreSQL este corriendo y que el archivo .env este configurado.")
        return None


def get_cursor():
    """Devuelve un cursor con DictCursor para resultados como diccionarios."""
    conn = get_connection()
    if conn is None:
        return None
    try:
        if conn.closed:
            st.cache_resource.clear()
            conn = get_connection()
        return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    except Exception:
        st.cache_resource.clear()
        return None


def commit():
    conn = get_connection()
    if conn:
        conn.commit()


def rollback():
    conn = get_connection()
    if conn:
        conn.rollback()


# ─────────────────────────────────────────────
# UTILIDADES DE SEGURIDAD
# ─────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash SHA-256 con sal desde variable de entorno."""
    salt = os.getenv("SECRET_SALT", "mateshop_salt_2025")
    return hmac.new(salt.encode(), password.encode(), hashlib.sha256).hexdigest()


# ─────────────────────────────────────────────
# OPERACIONES DE BASE DE DATOS — PRODUCTOS
# ─────────────────────────────────────────────

def db_get_products(search: str = "", tag: str = "todos") -> list:
    cur = get_cursor()
    if cur is None:
        return []
    try:
        query = """
            SELECT id, name, description, price, stock, tag, image_url, updated_at
            FROM products
            WHERE 1=1
        """
        params = []
        if search:
            query += " AND (LOWER(name) LIKE %s OR LOWER(description) LIKE %s)"
            params += [f"%{search.lower()}%", f"%{search.lower()}%"]
        if tag and tag != "todos":
            query += " AND tag = %s"
            params.append(tag)
        query += " ORDER BY id"
        cur.execute(query, params)
        return cur.fetchall()
    except Exception as e:
        rollback()
        st.error(f"Error al obtener productos: {e}")
        return []


def db_get_product(product_id: int) -> dict:
    cur = get_cursor()
    if cur is None:
        return {}
    try:
        cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        return cur.fetchone() or {}
    except Exception as e:
        rollback()
        return {}


def db_insert_product(name, description, price, stock, tag, image_url):
    cur = get_cursor()
    if cur is None:
        return False
    try:
        cur.execute("""
            INSERT INTO products
            (name, description, price, stock, tag, image_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, description, price, stock, tag, image_url))
        commit()
        return True
    except Exception as e:
        rollback()
        st.error(f"Error al insertar producto: {e}")
        return False


def db_update_product(product_id,name,description,price,stock,tag,image_url):
    cur = get_cursor()
    if cur is None:
        return False
    try:
        cur.execute("""
            UPDATE products
            SET name=%s, description=%s, price=%s, stock=%s, tag=%s, image_url=%s, updated_at=NOW()
            WHERE id=%s
        """, (name, description, price, stock, tag, product_id))
        commit()
        return True
    except Exception as e:
        rollback()
        st.error(f"Error al actualizar producto: {e}")
        return False


def db_delete_product(product_id) -> bool:
    cur = get_cursor()
    if cur is None:
        return False
    try:
        cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
        commit()
        return True
    except Exception as e:
        rollback()
        st.error(f"Error al eliminar producto: {e}")
        return False


def db_update_stock(product_id, delta: int) -> bool:
    """Incrementa o decrementa stock con validacion de no-negatividad."""
    cur = get_cursor()
    if cur is None:
        return False
    try:
        cur.execute("""
            UPDATE products
            SET stock = GREATEST(0, stock + %s), updated_at = NOW()
            WHERE id = %s
        """, (delta, product_id))
        commit()
        return True
    except Exception as e:
        rollback()
        st.error(f"Error al actualizar stock: {e}")
        return False


# ─────────────────────────────────────────────
# OPERACIONES DE BASE DE DATOS — PEDIDOS / FACTURAS
# ─────────────────────────────────────────────

def db_create_order(user_id: int, cart: dict, shipping_data: dict, payment_data: dict) -> tuple[bool, str, str]:
    cur = get_cursor()
    if cur is None:
        return False, "", "Sin conexion a la base de datos."
    try:
        invoice_number = f"MAT-{datetime.now().strftime('%Y%m%d%H%M%S%f')}-{user_id}"
        total = sum(float(item["price"]) * int(item["qty"]) for item in cart.values())

        cur.execute("""
            INSERT INTO orders (
                invoice_number, user_id, total, shipping_name, shipping_phone,
                shipping_email, shipping_city, shipping_address, shipping_postal_code,
                shipping_notes, card_holder, card_last4, card_expiration
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            invoice_number, user_id, total,
            shipping_data["name"], shipping_data["phone"], shipping_data["email"],
            shipping_data["city"], shipping_data["address"], shipping_data["postal_code"],
            shipping_data.get("notes", ""),
            payment_data["card_holder"], payment_data["card_last4"], payment_data["card_expiration"],
        ))
        order_id = cur.fetchone()["id"]

        for product_id, item in cart.items():
            qty = int(item["qty"])
            price = float(item["price"])
            subtotal = price * qty

            cur.execute("""
                UPDATE products
                SET stock = stock - %s, updated_at = NOW()
                WHERE id = %s AND stock >= %s
            """, (qty, product_id, qty))
            if cur.rowcount == 0:
                raise ValueError(f"No hay stock suficiente para {item['name']}.")

            cur.execute("""
                INSERT INTO order_items (order_id, product_id, product_name, unit_price, quantity, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (order_id, product_id, item["name"], price, qty, subtotal))

        commit()
        return True, invoice_number, "Pedido guardado correctamente."
    except Exception as e:
        rollback()
        return False, "", f"Error al guardar el pedido: {e}"


def db_get_user_orders(user_id: int) -> list:
    cur = get_cursor()
    if cur is None:
        return []
    try:
        cur.execute("""
            SELECT id, invoice_number, total, status, shipping_name, shipping_phone,
                   shipping_email, shipping_city, shipping_address, shipping_postal_code,
                   shipping_notes, card_holder, card_last4, card_expiration, created_at
            FROM orders
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        return cur.fetchall()
    except Exception as e:
        rollback()
        st.error(f"Error al obtener facturas: {e}")
        return []


def db_get_order_items(order_id: int) -> list:
    cur = get_cursor()
    if cur is None:
        return []
    try:
        cur.execute("""
            SELECT product_name, unit_price, quantity, subtotal
            FROM order_items
            WHERE order_id = %s
            ORDER BY id
        """, (order_id,))
        return cur.fetchall()
    except Exception as e:
        rollback()
        st.error(f"Error al obtener detalle de factura: {e}")
        return []


# ─────────────────────────────────────────────
# OPERACIONES DE BASE DE DATOS — USUARIOS
# ─────────────────────────────────────────────

def db_register_user(email, password, full_name) -> tuple[bool, str]:
    cur = get_cursor()
    if cur is None:
        return False, "Sin conexion a la base de datos."
    try:
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return False, "El email ya esta registrado."
        pw_hash = hash_password(password)
        cur.execute("""
            INSERT INTO users (email, password_hash, full_name)
            VALUES (%s, %s, %s)
        """, (email, pw_hash, full_name))
        commit()
        return True, "Cuenta creada exitosamente."
    except Exception as e:
        rollback()
        return False, f"Error al registrar: {e}"


def db_login_user(email, password) -> dict | None:
    cur = get_cursor()
    if cur is None:
        return None
    try:
        pw_hash = hash_password(password)
        cur.execute("""
            SELECT id, email, full_name, role
            FROM users
            WHERE email = %s AND password_hash = %s
        """, (email, pw_hash))
        return cur.fetchone()
    except Exception as e:
        rollback()
        return None


def db_get_users() -> list:
    cur = get_cursor()
    if cur is None:
        return []
    try:
        cur.execute("SELECT id, email, full_name, role, created_at FROM users ORDER BY created_at DESC")
        return cur.fetchall()
    except Exception as e:
        rollback()
        return []


def db_get_stats() -> dict:
    cur = get_cursor()
    if cur is None:
        return {}
    try:
        cur.execute("""
            SELECT
                COUNT(*) AS total_products,
                SUM(stock) AS total_stock,
                COUNT(*) FILTER (WHERE stock = 0) AS sin_stock,
                COUNT(*) FILTER (WHERE stock > 0 AND stock <= 5) AS stock_bajo,
                ROUND(AVG(price), 0) AS precio_promedio
            FROM products
        """)
        stats = dict(cur.fetchone())
        cur.execute("SELECT COUNT(*) AS total_users FROM users")
        stats["total_users"] = cur.fetchone()["total_users"]
        return stats
    except Exception as e:
        rollback()
        return {}


# ─────────────────────────────────────────────
# ESTADO DE SESION
# ─────────────────────────────────────────────

def init_session():
    defaults = {
        "user": None,
        "page": "catalogo",
        "cart": {},
        "edit_product_id": None,
        "selected_product_id": None,
        "payment_confirmed": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()


# ─────────────────────────────────────────────
# HELPERS DE UI
# ─────────────────────────────────────────────

TAG_OPTIONS = ["clasico", "premium", "popular", "edicion limitada", "accesorios"]
TAG_IMAGES = {
    "clasico": "images/fcb.jpeg",
    "premium": "images/logo_mate.jpeg",
    "popular": "images/logo_mate.jpeg",              #MAXI
    "edicion limitada": "images/logo_mate.jpeg",
    "accesorios": "images/logo_mate.jpeg"
}

def stock_label(stock):
    if stock == 0:
        return '<span class="stock-out">Sin stock</span>'
    if stock <= 5:
        return f'<span class="stock-low">¡ultimos {stock}!</span>'
    return f'<span class="stock-ok">En stock: {stock}</span>'


def alert(msg, kind="info"):
    st.markdown(f'<div class="alert-{kind}">{msg}</div>', unsafe_allow_html=True)


def money(value):
    return f"${float(value):,.0f}"


def delivery_date():
    return (datetime.now() + timedelta(days=3)).strftime("%d/%m/%Y")


def add_product_to_cart(product, qty):
    cart = st.session_state.cart
    pid = product["id"]
    current_qty = cart.get(pid, {}).get("qty", 0)
    next_qty = min(product["stock"], current_qty + qty)
    cart[pid] = {
        "name": product["name"],
        "price": float(product["price"]),
        "qty": next_qty,
        "stock": product["stock"],
        "description": product.get("description") or "",
        "image_url": product.get("image_url"),
    }
    st.session_state.cart = cart


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.markdown("""
    <style>
    /* 1. Oculta el fondo blanco y la línea de la barra superior */
    header[data-testid="stHeader"] {
        background: rgba(0,0,0,0);
        border-bottom: none;
    }

    /* 2. Oculta específicamente el botón de Deploy y el menú de hamburguesa */
    .stAppDeployButton, #MainMenu {
        visibility: hidden;
    }
    
    /* 3. Asegura que el botón del sidebar siga visible y funcional */
    button[data-testid="stSidebarCollapseIcon"] {
        visibility: visible;
    }
    </style>
    """, unsafe_allow_html=True)
with st.sidebar:
    st.markdown("## 🧉 Matioli")
    st.markdown("---")

    if st.session_state.user:
        u = st.session_state.user
        st.markdown(f"**{u['full_name']}**")
        st.markdown(f"*{u['role'].capitalize()}*")
        st.markdown("---")

        pages = ["catalogo", "carrito", "facturas"]
        labels = ["Catalogo", f"Carrito ({len(st.session_state.cart)})", "Facturas"]
        if u["role"] == "admin":
            pages  += ["admin_productos", "admin_usuarios", "admin_stats"]
            labels += ["Gestion de productos", "Usuarios", "Estadisticas"]
        if st.session_state.page == "producto_detalle" and st.session_state.selected_product_id:
            pages += ["producto_detalle"]
            labels += ["Detalle producto"]

        nav_index = pages.index(st.session_state.page) if st.session_state.page in pages else 0
        choice = st.radio("Navegacion", labels, index=nav_index, label_visibility="collapsed")
        st.session_state.page = pages[labels.index(choice)]

        st.markdown("---")
        if st.button("Cerrar sesion", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "catalogo"
            st.session_state.cart = {}
            st.rerun()
    else:
        st.markdown("Navegacion")
        pages = ["catalogo", "login"]
        labels = ["Catalogo", "Iniciar sesion / Registrarse"]
        if st.session_state.page == "producto_detalle" and st.session_state.selected_product_id:
            pages += ["producto_detalle"]
            labels += ["Detalle producto"]
        nav_index = pages.index(st.session_state.page) if st.session_state.page in pages else 0
        choice = st.radio("", labels, index=nav_index, label_visibility="collapsed")
        st.session_state.page = pages[labels.index(choice)]


# ─────────────────────────────────────────────
# PaGINA: CATALOGO
# ─────────────────────────────────────────────

if st.session_state.page == "catalogo":
    header_hero("images/Gemini_Generated_Image_xkgypxxkgypxxkgy.png")
    col_search, col_tag = st.columns([3, 1])
    with col_search:
        search = st.text_input("", placeholder="Buscar productos...", label_visibility="collapsed")
    with col_tag:
        tag_filter = st.selectbox("", ["todos"] + TAG_OPTIONS, label_visibility="collapsed")

    products = db_get_products(search, tag_filter)

    if not products:
        alert("No se encontraron productos con esos filtros.", "info")
    else:
        st.markdown(f"<p style='color:#7A6347;font-size:0.85rem;margin-bottom:1rem'>{len(products)} producto(s) encontrado(s)</p>", unsafe_allow_html=True)
        cols = st.columns(4)
        for i, p in enumerate(products):
            with cols[i % 4]:
                icon_path = p.get("image_url") or "images/mate_madera.png"
                icon_base64 = get_base64_favicon(icon_path)#MAXI
                st.markdown(f"""
<div class="promo-card">
    <div class="promo-image">
        <img src="data:image/jpeg;base64,{icon_base64}">
    </div>
    <div class="promo-content">
        <div class="promo-tag">
            {p['tag']}
        </div>
        <div class="promo-title">
            {p['name']}
        </div>
        <div class="promo-description">
            {p['description'] or ''}
        </div>
        <div class="promo-price">
            ${p['price']:,.0f}
        </div>
        <div class="promo-stock">
            {stock_label(p['stock'])}
        </div>
    </div>
</div>
                    """, unsafe_allow_html=True)

                if st.button("Ver producto", key=f"view_{p['id']}", use_container_width=True):
                    st.session_state.selected_product_id = p["id"]
                    st.session_state.payment_confirmed = False
                    st.session_state.page = "producto_detalle"
                    st.rerun()

                if st.session_state.user and p["stock"] > 0:
                    qty = st.number_input(
                        "Cantidad", min_value=1, max_value=p["stock"],
                        value=1, key=f"qty_{p['id']}", label_visibility="collapsed"
                    )
                    if st.button("Agregar al carrito", key=f"add_{p['id']}", use_container_width=True):
                        add_product_to_cart(p, qty)
                        st.success(f"✓ {p['name']} agregado")
                        st.rerun()
                elif not st.session_state.user:
                    st.caption("Inicia sesion para comprar")


# ─────────────────────────────────────────────
# PAGINA: CARRITO
# ─────────────────────────────────────────────

elif st.session_state.page == "producto_detalle":
    product_id = st.session_state.selected_product_id

    if st.button("Volver al catalogo", key="back_to_catalog", use_container_width=False):
        st.session_state.page = "catalogo"
        st.session_state.payment_confirmed = False
        st.rerun()

    if not product_id:
        alert("Selecciona un producto desde el catalogo.", "info")
        st.stop()

    product = db_get_product(product_id)
    if not product:
        alert("No se pudo cargar el producto seleccionado.", "error")
        st.stop()

    image_path = product.get("image_url") or "images/mate_madera.png"
    image_base64 = get_base64_favicon(image_path)
    name = html.escape(str(product.get("name") or "Producto"))
    description = html.escape(str(product.get("description") or "Sin descripcion disponible."))
    tag = html.escape(str(product.get("tag") or "catalogo"))
    price = float(product.get("price") or 0)
    stock = int(product.get("stock") or 0)
    six_payments = price / 6 if price else 0

    st.markdown('<div class="detail-shell">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="detail-topline">Matioli | {tag} | Stock disponible: {stock}</div>',
        unsafe_allow_html=True
    )

    detail_col, pay_col = st.columns([1.65, 0.85], gap="large")

    with detail_col:
        st.markdown(f"""
        <div class="detail-photo">
            <img src="data:image/jpeg;base64,{image_base64}" alt="{name}">
        </div>
        <div class="detail-info">
            <div class="section-label">{tag}</div>
            <h1>{name}</h1>
            <div class="detail-description">{description}</div>
        </div>
        """, unsafe_allow_html=True)

    with pay_col:
        st.markdown(f"""
        <div class="detail-paybox">
            <div class="pay-label">Importe</div>
            <div class="pay-price">{money(price)}</div>
            <div class="pay-note">En 6 cuotas de {money(six_payments)}</div>
            <div class="pay-section">
                <strong>Fecha de entrega aproximada</strong><br>
                Llega el {delivery_date()}
            </div>
            <div class="pay-section">
                <strong>Metodos de pago</strong>
                <div class="pay-method">Tarjeta de credito o debito</div>
                <div class="pay-method">Transferencia bancaria</div>
                <div class="pay-method">Efectivo al retirar</div>
            </div>
            <div class="pay-section">
                <strong>{'Stock disponible' if stock > 0 else 'Sin stock disponible'}</strong><br>
                Compra simulada, sin cobro real.
            </div>
        </div>
        """, unsafe_allow_html=True)

        qty = st.number_input(
            "Cantidad",
            min_value=1,
            max_value=max(stock, 1),
            value=1,
            disabled=stock == 0,
            key=f"detail_qty_{product_id}"
        )
        payment_method = st.radio(
            "Metodo elegido",
            ["Tarjeta", "Transferencia", "Efectivo al retirar"],
            key=f"payment_method_{product_id}"
        )

        pay_disabled = stock == 0
        if st.button("Pagar ahora", key=f"pay_now_{product_id}", use_container_width=True, disabled=pay_disabled):
            st.session_state.payment_confirmed = True
            alert(f"Pago simulado aprobado con {payment_method}. Total: {money(price * qty)}", "success")

        if st.button("Agregar al carrito", key=f"detail_add_{product_id}", use_container_width=True, disabled=pay_disabled):
            add_product_to_cart(product, qty)
            alert(f"Producto agregado al carrito: {name}", "success")

        if st.session_state.payment_confirmed:
            alert("Operacion simulada correctamente. No se realizo ningun cobro real.", "info")

    st.markdown('</div>', unsafe_allow_html=True)


elif st.session_state.page == "carrito":
    st.markdown('<div class="section-label">Tu compra</div>', unsafe_allow_html=True)
    st.title("Carrito")
    if st.session_state.order_success:
        alert(st.session_state.order_success, "success")
        st.session_state.order_success = ""

    cart = st.session_state.cart
    if not cart:
        alert("Tu carrito esta vacio. ¡Explora el catalogo!", "info")
    else:
        total = 0
        for pid, item in list(cart.items()):
            if item["stock"] <= 0:
                del st.session_state.cart[pid]
                alert(f"{item['name']} ya no tiene stock y se quito del carrito.", "info")
                st.rerun()
            c1, c2, c3, c4 = st.columns([4, 1, 2, 1])
            with c1:
                st.write(f"**{item['name']}**")
            with c2:
                item["qty"] = min(item["qty"], item["stock"])
                new_qty = st.number_input("", min_value=1, max_value=item["stock"],
                                          value=item["qty"], key=f"cart_qty_{pid}", label_visibility="collapsed")
                cart[pid]["qty"] = new_qty
            with c3:
                subtotal = item["price"] * new_qty
                st.write(f"${subtotal:,.0f}")
                total += subtotal
            with c4:
                if st.button("✕", key=f"remove_{pid}"):
                    del st.session_state.cart[pid]
                    st.rerun()

        st.markdown("---")
        st.markdown(f"### Total: **${total:,.0f}**")

        st.markdown("### Datos de envio y pago")
        with st.form("checkout_form"):
            st.markdown("#### Envio")
            col_a, col_b = st.columns(2)
            with col_a:
                shipping_name = st.text_input("Nombre y apellido", value=st.session_state.user.get("full_name", ""))
                shipping_phone = st.text_input("Telefono")
                shipping_city = st.text_input("Ciudad")
            with col_b:
                shipping_email = st.text_input("Email", value=st.session_state.user.get("email", ""))
                shipping_address = st.text_input("Direccion")
                shipping_postal_code = st.text_input("Codigo postal")

            shipping_notes = st.text_area("Indicaciones para la entrega", placeholder="Piso, departamento, horario preferido...")

            st.markdown("#### Tarjeta")
            col_c, col_d = st.columns(2)
            with col_c:
                card_name = st.text_input("Titular de la tarjeta")
                card_number = st.text_input("Numero de tarjeta", placeholder="0000 0000 0000 0000")
            with col_d:
                card_expiration = st.text_input("Vencimiento", placeholder="MM/AA")
                card_security_code = st.text_input("Codigo de seguridad", type="password", placeholder="CVV")

            submitted_checkout = st.form_submit_button("Confirmar pedido", use_container_width=True)

        if submitted_checkout:
            required_fields = [
                shipping_name, shipping_phone, shipping_email, shipping_city,
                shipping_address, shipping_postal_code, card_name, card_number,
                card_expiration, card_security_code,
            ]
            if not all(str(field).strip() for field in required_fields):
                alert("Completa los datos de envio y tarjeta para confirmar el pedido.", "error")
            else:
                card_digits = "".join(ch for ch in card_number if ch.isdigit())
                if len(card_digits) < 4:
                    alert("Ingresa al menos los ultimos 4 digitos de la tarjeta.", "error")
                else:
                    shipping_data = {
                        "name": shipping_name.strip(),
                        "phone": shipping_phone.strip(),
                        "email": shipping_email.strip(),
                        "city": shipping_city.strip(),
                        "address": shipping_address.strip(),
                        "postal_code": shipping_postal_code.strip(),
                        "notes": shipping_notes.strip(),
                    }
                    payment_data = {
                        "card_holder": card_name.strip(),
                        "card_last4": card_digits[-4:],
                        "card_expiration": card_expiration.strip(),
                    }
                    ok, invoice_number, msg = db_create_order(
                        st.session_state.user["id"],
                        cart,
                        shipping_data,
                        payment_data,
                    )
                    if ok:
                        clear_cart_and_show_success(f"Pedido confirmado. Factura {invoice_number} guardada.")
                    else:
                        alert(msg, "error")

# ─────────────────────────────────────────────
# PAGINA: FACTURAS
# ─────────────────────────────────────────────

elif st.session_state.page == "facturas":
    st.markdown('<div class="section-label">Historial</div>', unsafe_allow_html=True)
    st.title("Facturas")

    orders = db_get_user_orders(st.session_state.user["id"])
    if not orders:
        alert("Todavia no tenes facturas guardadas.", "info")
    else:
        for order in orders:
            created_at = str(order["created_at"])[:16] if order["created_at"] else ""
            with st.expander(f"{order['invoice_number']} - ${order['total']:,.0f} - {created_at}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Total", f"${order['total']:,.0f}")
                c2.metric("Estado", order["status"].capitalize())
                c3.metric("Tarjeta", f"**** {order['card_last4']}")

                st.markdown("#### Datos de envio")
                st.write(f"**Nombre:** {order['shipping_name']}")
                st.write(f"**Contacto:** {order['shipping_phone']} - {order['shipping_email']}")
                st.write(f"**Direccion:** {order['shipping_address']}, {order['shipping_city']} ({order['shipping_postal_code']})")
                if order["shipping_notes"]:
                    st.write(f"**Indicaciones:** {order['shipping_notes']}")

                st.markdown("#### Productos")
                items = db_get_order_items(order["id"])
                for item in items:
                    p1, p2, p3, p4 = st.columns([4, 1, 1, 1])
                    p1.write(item["product_name"])
                    p2.write(f"x{item['quantity']}")
                    p3.write(f"${item['unit_price']:,.0f}")
                    p4.write(f"${item['subtotal']:,.0f}")


# ─────────────────────────────────────────────
# PAGINA: LOGIN / REGISTRO
# ─────────────────────────────────────────────

elif st.session_state.page == "login":
    st.markdown('<div class="section-label">Acceso</div>', unsafe_allow_html=True)
    st.title("Iniciar sesion")

    tab_login, tab_register = st.tabs(["Iniciar sesion", "Crear cuenta"])

    with tab_login:
        with st.form("form_login"):
            email    = st.text_input("Email", placeholder="tu@email.com")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Ingresar", use_container_width=True)
        if submitted:
            if not email or not password:
                alert("Completa todos los campos.", "error")
            else:
                user = db_login_user(email, password)
                if user:
                    st.session_state.user = dict(user)
                    st.session_state.page = "catalogo"
                    st.rerun()
                else:
                    alert("Credenciales incorrectas.", "error")

        st.markdown("---")

    with tab_register:
        with st.form("form_register"):
            full_name = st.text_input("Nombre completo")
            email_r   = st.text_input("Email")
            pass_r    = st.text_input("Contraseña (minimo 6 caracteres)", type="password")
            pass_r2   = st.text_input("Repetir contraseña", type="password")
            submitted_r = st.form_submit_button("Crear cuenta", use_container_width=True)
        if submitted_r:
            if not all([full_name, email_r, pass_r, pass_r2]):
                alert("Completa todos los campos.", "error")
            elif pass_r != pass_r2:
                alert("Las contraseñas no coinciden.", "error")
            elif len(pass_r) < 6:
                alert("La contraseña debe tener al menos 6 caracteres.", "error")
            else:
                ok, msg = db_register_user(email_r, pass_r, full_name)
                if ok:
                    alert(f"✓ {msg} Ahora podes iniciar sesion.", "success")
                else:
                    alert(msg, "error")


# ─────────────────────────────────────────────
# PAGINA ADMIN: GESTION DE PRODUCTOS
# ─────────────────────────────────────────────

elif st.session_state.page == "admin_productos":
    if not st.session_state.user or st.session_state.user["role"] != "admin":
        alert("Acceso denegado.", "error")
        st.stop()

    st.markdown('<div class="section-label">Panel de administracion</div>', unsafe_allow_html=True)
    st.title("Gestion de productos")

    tab_list, tab_add, tab_edit, tab_stock = st.tabs(["Lista", "Nuevo producto", "Editar", "Ajustar stock"])

    # ── Lista de productos ──
    with tab_list:
        products = db_get_products()
        if products:
            for p in products:
                c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
                c1.write(f"**{p['name']}**  \n*{p['tag']}*")
                c2.write(f"${p['price']:,.0f}")
                c3.markdown(stock_label(p["stock"]), unsafe_allow_html=True)
                if c4.button("Editar", key=f"edit_{p['id']}"):
                    st.session_state.edit_product_id = p["id"]
                    st.rerun()
                if c5.button("Eliminar", key=f"del_{p['id']}"):
                    if db_delete_product(p["id"]):
                        st.success("Producto eliminado.")
                        st.rerun()
                st.divider()
        else:
            alert("No hay productos cargados.", "info")

    # ── Nuevo producto ──
    with tab_add:

        with st.form("form_new_product"):

            name = st.text_input("Nombre del producto")

            desc = st.text_area("Descripcion")

            price = st.number_input(
                "Precio ($)",
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )

            stock = st.number_input(
                "Stock inicial",
                min_value=0,
                step=1
            )

            tag = st.selectbox(
                "Categoria",
                TAG_OPTIONS
            )

            image_file = st.file_uploader(
                "Imagen del producto",
                type=["png", "jpg", "jpeg"]
            )

            ok = st.form_submit_button(
                "Agregar producto",
                use_container_width=True
            )

        if ok:

            image_path = None

            if image_file is not None:

                extension = image_file.name.split(".")[-1]

                filename = f"{uuid.uuid4()}.{extension}"

                image_path = os.path.join(
                    "images",
                    filename
                )

                with open(image_path, "wb") as f:
                    f.write(image_file.getbuffer())

            if not name:

                alert(
                    "El nombre es obligatorio.",
                    "error"
                )

            elif db_insert_product(
                name,
                desc,
                price,
                stock,
                tag,
                image_path
            ):

                alert(
                    f"✓ Producto '{name}' agregado correctamente.",
                    "success"
                )

                st.rerun()
    # ── Editar producto ──
    with tab_edit:
        products = db_get_products()
        product_names = {p["id"]: f"{p['name']} (#{p['id']})" for p in products}
        if not product_names:
            alert("No hay productos.", "info")
        else:
            default_id = st.session_state.edit_product_id
            options = list(product_names.keys())
            idx = options.index(default_id) if default_id in options else 0
            selected_id = st.selectbox("Seleccionar producto", options,
                                       format_func=lambda x: product_names[x], index=idx)
            p = db_get_product(selected_id)
            if p:
                with st.form("form_edit_product"):
                    name_e  = st.text_input("Nombre", value=p["name"])
                    desc_e  = st.text_area("Descripcion", value=p["description"] or "")
                    price_e = st.number_input("Precio", value=float(p["price"]), step=100.0, format="%.2f")
                    stock_e = st.number_input("Stock", value=int(p["stock"]), step=1)
                    tag_e   = st.selectbox("Categoria", TAG_OPTIONS,
                                           index=TAG_OPTIONS.index(p["tag"]) if p["tag"] in TAG_OPTIONS else 0)
                    save = st.form_submit_button("Guardar cambios", use_container_width=True)
                if save:
                    if db_update_product(selected_id, name_e, desc_e, price_e, stock_e, tag_e):
                        alert("✓ Producto actualizado correctamente.", "success")
                        st.session_state.edit_product_id = None
                        st.rerun()

    # ── Ajuste rapido de stock ──
    with tab_stock:
        products = db_get_products()
        st.markdown("Ajusta el stock de cualquier producto rapidamente:")
        for p in products:
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            c1.markdown(stock_label(p["stock"]), unsafe_allow_html=True)
            c1.caption(p["name"])
            delta = c2.number_input("", value=0, step=1, key=f"delta_{p['id']}", label_visibility="collapsed")
            if c3.button("Aplicar", key=f"apply_{p['id']}"):
                if db_update_stock(p["id"], delta):
                    st.rerun()
            c4.write(f"→ {max(0, p['stock'] + delta)}")
            st.divider()


# ─────────────────────────────────────────────
# PaGINA ADMIN: USUARIOS
# ─────────────────────────────────────────────

elif st.session_state.page == "admin_usuarios":
    if not st.session_state.user or st.session_state.user["role"] != "admin":
        alert("Acceso denegado.", "error")
        st.stop()

    st.markdown('<div class="section-label">Panel de administracion</div>', unsafe_allow_html=True)
    st.title("Usuarios registrados")

    users = db_get_users()
    if users:
        for u in users:
            c1, c2, c3, c4 = st.columns([3, 2, 1, 2])
            c1.write(f"**{u['full_name']}**  \n{u['email']}")
            c2.caption(str(u["created_at"])[:16] if u["created_at"] else "")
            role_color = "#3D6B3A" if u["role"] == "admin" else "#7A6347"
            c3.markdown(f"<span style='color:{role_color};font-weight:500'>{u['role']}</span>", unsafe_allow_html=True)
            st.divider()
    else:
        alert("No hay usuarios registrados.", "info")


# ─────────────────────────────────────────────
# PaGINA ADMIN: ESTADiSTICAS
# ─────────────────────────────────────────────

elif st.session_state.page == "admin_stats":
    if not st.session_state.user or st.session_state.user["role"] != "admin":
        alert("Acceso denegado.", "error")
        st.stop()

    st.markdown('<div class="section-label">Panel de administracion</div>', unsafe_allow_html=True)
    st.title("Estadisticas")

    stats = db_get_stats()
    if stats:
        c1, c2, c3, c4, c5 = st.columns(5)
        for col, num, label in [
            (c1, stats.get("total_products", 0), "Productos"),
            (c2, stats.get("total_stock", 0), "Unidades en stock"),
            (c3, stats.get("sin_stock", 0), "Sin stock"),
            (c4, stats.get("stock_bajo", 0), "Stock bajo (≤5)"),
            (c5, stats.get("total_users", 0), "Usuarios"),
        ]:
            col.markdown(f"""
            <div class="metric-card">
                <div class="num">{num}</div>
                <div class="label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("#### Distribucion por categoria")
            cur = get_cursor()
            if cur:
                cur.execute("SELECT tag, COUNT(*) as qty, SUM(stock) as total_stock FROM products GROUP BY tag")
                rows = cur.fetchall()
                if rows:
                    import pandas as pd
                    df = pd.DataFrame(rows)
                    st.dataframe(df.rename(columns={"tag": "Categoria", "qty": "Productos", "total_stock": "Stock total"}),
                                 use_container_width=True, hide_index=True)

        with c_right:
            st.markdown("#### Precio promedio")
            st.metric("Precio promedio", f"${stats.get('precio_promedio', 0):,.0f}")
            st.markdown(f"**{stats.get('sin_stock', 0)}** producto(s) sin stock")
            st.markdown(f"**{stats.get('stock_bajo', 0)}** producto(s) con stock bajo (≤ 5 unidades)")
    else:
        alert("No se pudieron cargar las estadisticas.", "error")

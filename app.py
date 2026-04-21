"""
MateShop — Aplicacion Streamlit + PostgreSQL
============================================
Frontend: Streamlit
Backend:  PostgreSQL (psycopg2)

Ejecutar:
    streamlit run app.py
"""

import os
import streamlit as st
import psycopg2
import psycopg2.extras
from psycopg2 import OperationalError, errors
from dotenv import load_dotenv
from datetime import datetime
import hashlib
import hmac

load_dotenv()
#os.environ["DB_HOST"] = "localhost"
#os.environ["DB_PORT"] = "5432"
#os.environ["DB_NAME"] = "mateshop"
#os.environ["DB_USER"] = "postgres"
#os.environ["DB_PASSWORD"] = "fELIPEALIAGA2008"


# ─────────────────────────────────────────────
# CONFIGURACION DE PaGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MateShop",
    page_icon="🧉",
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
    .main-header {
        background: linear-gradient(135deg, #2A1A08 0%, #3D6B3A 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 { color: white !important; font-size: 2.4rem; margin-bottom: 0.3rem; }
    .main-header p  { color: rgba(255,255,255,0.7); font-size: 1rem; margin: 0; }

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
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "mateshop"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
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
            SELECT id, name, description, price, stock, tag, updated_at
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


def db_insert_product(name, description, price, stock, tag) -> bool:
    cur = get_cursor()
    if cur is None:
        return False
    try:
        cur.execute("""
            INSERT INTO products (name, description, price, stock, tag)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, description, price, stock, tag))
        commit()
        return True
    except Exception as e:
        rollback()
        st.error(f"Error al insertar producto: {e}")
        return False


def db_update_product(product_id, name, description, price, stock, tag) -> bool:
    cur = get_cursor()
    if cur is None:
        return False
    try:
        cur.execute("""
            UPDATE products
            SET name=%s, description=%s, price=%s, stock=%s, tag=%s, updated_at=NOW()
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
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()


# ─────────────────────────────────────────────
# HELPERS DE UI
# ─────────────────────────────────────────────

TAG_OPTIONS = ["clasico", "premium", "popular", "edicion limitada", "accesorios"]
TAG_ICONS   = {"clasico": "🧉", "premium": "🌿", "popular": "☕", "edicion limitada": "🎨", "accesorios": "🔧"}

def stock_label(stock):
    if stock == 0:
        return '<span class="stock-out">Sin stock</span>'
    if stock <= 5:
        return f'<span class="stock-low">¡ultimos {stock}!</span>'
    return f'<span class="stock-ok">En stock: {stock}</span>'


def alert(msg, kind="info"):
    st.markdown(f'<div class="alert-{kind}">{msg}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🧉 MateShop")
    st.markdown("---")

    if st.session_state.user:
        u = st.session_state.user
        st.markdown(f"**{u['full_name']}**")
        st.markdown(f"*{u['role'].capitalize()}*")
        st.markdown("---")

        pages = ["catalogo", "carrito"]
        labels = ["Catalogo", f"Carrito ({len(st.session_state.cart)})"]
        if u["role"] == "admin":
            pages  += ["admin_productos", "admin_usuarios", "admin_stats"]
            labels += ["Gestion de productos", "Usuarios", "Estadisticas"]

        choice = st.radio("Navegacion", labels, label_visibility="collapsed")
        st.session_state.page = pages[labels.index(choice)]

        st.markdown("---")
        if st.button("Cerrar sesion", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "catalogo"
            st.session_state.cart = {}
            st.rerun()
    else:
        st.markdown("Navegacion")
        choice = st.radio("", ["Catalogo", "Iniciar sesion / Registrarse"], label_visibility="collapsed")
        st.session_state.page = "catalogo" if choice == "Catalogo" else "login"


# ─────────────────────────────────────────────
# PaGINA: CATALOGO
# ─────────────────────────────────────────────

if st.session_state.page == "catalogo":
    
    st.markdown("""
    <div class="main-header">
        <h1>🧉 MateShop</h1>
        <p>La mejor seleccion de mates artesanales — Cordoba, Argentina</p>
    </div>
    """, unsafe_allow_html=True)

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
        cols = st.columns(3)
        for i, p in enumerate(products):
            with cols[i % 3]:
                icon = TAG_ICONS.get(p["tag"], "📦")
                st.markdown(f"""
                <div class="product-card">
                    <div style="font-size:2.5rem;text-align:center;padding:1rem 0;background:#F5F0E8;border-radius:8px;margin-bottom:1rem">{icon}</div>
                    <div class="section-label">{p['tag']}</div>
                    <h3 style="font-size:1.1rem;margin:0 0 0.4rem">{p['name']}</h3>
                    <p style="font-size:0.82rem;color:#7A6347;line-height:1.5;margin-bottom:0.8rem">{p['description'] or ''}</p>
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <span style="font-size:1.3rem;font-weight:500;color:#2A1A08">${p['price']:,.0f}</span>
                        {stock_label(p['stock'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.user and p["stock"] > 0:
                    qty = st.number_input(
                        "Cantidad", min_value=1, max_value=p["stock"],
                        value=1, key=f"qty_{p['id']}", label_visibility="collapsed"
                    )
                    if st.button("Agregar al carrito", key=f"add_{p['id']}", use_container_width=True):
                        cart = st.session_state.cart
                        cart[p["id"]] = {
                            "name": p["name"],
                            "price": float(p["price"]),
                            "qty": cart.get(p["id"], {}).get("qty", 0) + qty,
                            "stock": p["stock"],
                        }
                        st.session_state.cart = cart
                        st.success(f"✓ {p['name']} agregado")
                        st.rerun()
                elif not st.session_state.user:
                    st.caption("Inicia sesion para comprar")


# ─────────────────────────────────────────────
# PAGINA: CARRITO
# ─────────────────────────────────────────────

elif st.session_state.page == "carrito":
    st.markdown('<div class="section-label">Tu compra</div>', unsafe_allow_html=True)
    st.title("Carrito")

    cart = st.session_state.cart
    if not cart:
        alert("Tu carrito esta vacio. ¡Explora el catalogo!", "info")
    else:
        total = 0
        for pid, item in list(cart.items()):
            c1, c2, c3, c4 = st.columns([4, 1, 2, 1])
            with c1:
                st.write(f"**{item['name']}**")
            with c2:
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

        if st.button("Confirmar pedido", use_container_width=True):
            # Aqui iria la logica de pedidos (tabla orders)
            alert("✓ Pedido confirmado. ¡Gracias por tu compra!", "success")
            st.session_state.cart = {}
            st.rerun()


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
            name  = st.text_input("Nombre del producto")
            desc  = st.text_area("Descripcion")
            price = st.number_input("Precio ($)", min_value=0.0, step=100.0, format="%.2f")
            stock = st.number_input("Stock inicial", min_value=0, step=1)
            tag   = st.selectbox("Categoria", TAG_OPTIONS)
            ok    = st.form_submit_button("Agregar producto", use_container_width=True)
        if ok:
            if not name:
                alert("El nombre es obligatorio.", "error")
            elif db_insert_product(name, desc, price, stock, tag):
                alert(f"✓ Producto '{name}' agregado correctamente.", "success")
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

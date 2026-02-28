import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Laboratorio de Electromagnetismo - Fuerzas y Campos")
st.write("Visualización de la interacción entre 3 átomos (cargas puntuales).")

st.sidebar.header("Configuración de Átomos")

def input_atom(n, default_x, default_y, default_q):
    st.sidebar.subheader(f"Átomo {n}")
    x = st.sidebar.slider(f"Posición X_{n}", -5.0, 5.0, float(default_x), step=0.5)
    y = st.sidebar.slider(f"Posición Y_{n}", -5.0, 5.0, float(default_y), step=0.5)
    q = st.sidebar.number_input(f"Carga q_{n} (μC)", value=float(default_q), step=1.0, key=f"q{n}")
    return np.array([x, y]), q

p1, q1 = input_atom(1, -2.0, 0.0, 1.0)
p2, q2 = input_atom(2, 2.0, 0.0, -1.0)
p3, q3 = input_atom(3, 0.0, 2.0, 1.0)

# --- CÁLCULO DEL CAMPO ELÉCTRICO ---
x_grid = np.linspace(-6, 6, 60)
y_grid = np.linspace(-6, 6, 60)
X, Y = np.meshgrid(x_grid, y_grid)

def calc_campo_E(q, pos, X, Y):
    rx = X - pos[0]
    ry = Y - pos[1]
    r_mag = np.sqrt(rx**2 + ry**2)
    r_mag[r_mag < 0.1] = 0.1 
    Ex = q * rx / r_mag**3
    Ey = q * ry / r_mag**3
    return Ex, Ey

Ex_total = sum(calc_campo_E(q, p, X, Y)[0] for q, p in zip([q1, q2, q3], [p1, p2, p3]))
Ey_total = sum(calc_campo_E(q, p, X, Y)[1] for q, p in zip([q1, q2, q3], [p1, p2, p3]))

# --- VISUALIZACIÓN Y FUERZAS ENTRE PARES ---
st.sidebar.markdown("---")
mostrar_campo = st.sidebar.checkbox("Mostrar líneas de Campo Eléctrico", value=True)
mostrar_fuerzas = st.sidebar.checkbox("Mostrar vectores de Fuerza entre pares", value=True)

fig, ax = plt.subplots(figsize=(8, 8))
fig.patch.set_alpha(0.0) # Hace transparente el fondo de la figura externa
ax.set_facecolor('none') # Hace transparente el fondo del plano cartesiano
ax.set_xlim(-6, 6)
ax.set_ylim(-6, 6)
ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.5)

# 1. Dibujar el Campo Eléctrico
if mostrar_campo:
    intensidad = np.log(np.sqrt(Ex_total**2 + Ey_total**2))
    ax.streamplot(X, Y, Ex_total, Ey_total, color=intensidad, 
                  linewidth=1.2, cmap='plasma', density=1.5, arrowstyle='->', zorder=1)

# Función para calcular y dibujar la fuerza de un átomo sobre otro
def dibujar_fuerza_par(p_origen, q_origen, p_destino, q_destino, nombre, color):
    r_vec = p_destino - p_origen
    r_mag = np.linalg.norm(r_vec)
    if r_mag < 0.2 or q_origen == 0 or q_destino == 0:
        return
    
    # F = q1*q2 / r^2 
    F_mag = (q_origen * q_destino) / (r_mag**2)
    F_vec = F_mag * (r_vec / r_mag)
    largo_real = np.linalg.norm(F_vec)
    
    if largo_real > 0:
        dir_vec = F_vec / largo_real
        
        # AJUSTES VISUALES CRÍTICOS:
        # 1. Empujar el inicio de la flecha fuera del átomo (0.5 unidades de distancia)
        # 2. Obligar a la flecha a tener un largo mínimo visible (0.5) y un tope (3.5)
        offset = 0.5
        largo_visual = min(max(largo_real * 30.0, 0.5), 3.5) 
        
        inicio = p_destino + dir_vec * offset
        fin = inicio + dir_vec * largo_visual
        
        # Dibujar flecha
        ax.annotate('', xy=fin, xytext=inicio,
                    arrowprops=dict(facecolor=color, edgecolor=color, arrowstyle='-|>', lw=2.5, mutation_scale=20),
                    zorder=4)
        # Etiqueta de la fuerza
        ax.text(fin[0] + dir_vec[0]*0.2, fin[1] + dir_vec[1]*0.2, 
                nombre, color=color, fontsize=12, fontweight='bold', zorder=7)

# 2. Dibujar Fuerzas
if mostrar_fuerzas:
    # Usando el Cian de Makerbox para un par de fuerzas
    dibujar_fuerza_par(p2, q2, p1, q1, "F21", '#00aeef') 
    dibujar_fuerza_par(p3, q3, p1, q1, "F31", '#00aeef')
    
    # Usando el Morado de Makerbox para otro par
    dibujar_fuerza_par(p1, q1, p2, q2, "F12", '#46247a') 
    dibujar_fuerza_par(p3, q3, p2, q2, "F32", '#46247a')
    
    # Un naranja brillante para contraste en el tercer par
    dibujar_fuerza_par(p1, q1, p3, q3, "F13", '#f37021') 
    dibujar_fuerza_par(p2, q2, p3, q3, "F23", '#f37021')

# 3. Dibujar los Átomos
colores = ['red' if q > 0 else 'blue' if q < 0 else 'gray' for q in [q1, q2, q3]]
for p, q, c, label in zip([p1, p2, p3], [q1, q2, q3], colores, ['1', '2', '3']):
    ax.scatter(p[0], p[1], s=900, color=c, zorder=5, edgecolors='black')
    signo = "+" if q > 0 else ""
    texto = f"{signo}{q}μC" if q != 0 else "0μC"
    ax.text(p[0], p[1], texto, ha='center', va='center', color='white', fontweight='bold', zorder=6, fontsize=10)
    ax.text(p[0]+0.4, p[1]+0.4, f"A{label}", fontsize=12, fontweight='bold', zorder=6)

plt.title("Interacción y Campo Eléctrico Resultante", fontsize=14)
st.pyplot(fig)


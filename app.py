import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Laboratorio de Electromagnetismo - Fuerzas y Campos")
st.write("Visualización de la interacción entre 3 átomos (cargas puntuales).")

st.sidebar.header("Configuración de Átomos")

def input_atom(n, default_x, default_y, default_q):
    st.sidebar.subheader(f"Átomo {n}")
    x = st.sidebar.slider(f"Posición X_{n}", -5.0, 5.0, default_x, step=0.5)
    y = st.sidebar.slider(f"Posición Y_{n}", -5.0, 5.0, default_y, step=0.5)
    q = st.sidebar.number_input(f"Carga q_{n} (μC)", value=default_q, step=1.0, key=f"q{n}")
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

# --- CÁLCULO DE FUERZAS (Ley de Coulomb) ---
def calc_fuerza(q_target, pos_target, q_source, pos_source):
    r_vec = pos_target - pos_source
    r_mag = np.linalg.norm(r_vec)
    if r_mag < 0.1 or q_target == 0 or q_source == 0: 
        return np.array([0.0, 0.0])
    # F = k * q1 * q2 / r^2 (k omitida para escala visual)
    F_mag = (q_target * q_source) / (r_mag**2)
    return F_mag * (r_vec / r_mag)

F1 = calc_fuerza(q1, p1, q2, p2) + calc_fuerza(q1, p1, q3, p3)
F2 = calc_fuerza(q2, p2, q1, p1) + calc_fuerza(q2, p2, q3, p3)
F3 = calc_fuerza(q3, p3, q1, p1) + calc_fuerza(q3, p3, q2, p2)

# --- VISUALIZACIÓN ---
st.sidebar.markdown("---")
mostrar_campo = st.sidebar.checkbox("Mostrar líneas de Campo Eléctrico", value=True)
mostrar_fuerzas = st.sidebar.checkbox("Mostrar vectores de Fuerza Resultante", value=True)

fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(-6, 6)
ax.set_ylim(-6, 6)
ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.5)

if mostrar_campo:
    intensidad = np.log(np.sqrt(Ex_total**2 + Ey_total**2))
    ax.streamplot(X, Y, Ex_total, Ey_total, color=intensidad, 
                  linewidth=1.2, cmap='plasma', density=1.5, arrowstyle='->', zorder=1)

colores = ['red' if q > 0 else 'blue' if q < 0 else 'gray' for q in [q1, q2, q3]]

for p, q, c, label, F in zip([p1, p2, p3], [q1, q2, q3], colores, ['1', '2', '3'], [F1, F2, F3]):
    # Dibujar el átomo más grande
    ax.scatter(p[0], p[1], s=900, color=c, zorder=5, edgecolors='black')
    
    # Texto de polaridad y carga en el centro
    signo = "+" if q > 0 else ""
    texto = f"{signo}{q}μC" if q != 0 else "0μC"
    ax.text(p[0], p[1], texto, ha='center', va='center', color='white', fontweight='bold', zorder=6, fontsize=10)
    ax.text(p[0]+0.4, p[1]+0.4, f"A{label}", fontsize=12, fontweight='bold', zorder=6)

    # Dibujar vector de fuerza neta
    if mostrar_fuerzas and np.linalg.norm(F) > 0:
        ax.quiver(p[0], p[1], F[0], F[1], color='black', scale=15, width=0.015, zorder=4)

plt.title("Interacción y Campo Eléctrico Resultante", fontsize=14)
st.pyplot(fig)
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 3D grid
x = np.linspace(-8, 8, 140)
y = np.linspace(-8, 8, 140)
X, Y = np.meshgrid(x, y)

frames = 64
# Faseovergang fra bølge (tension lav) til partikel (tension høj)
tension_vals = np.linspace(0.7, 7, frames)

def field(X, Y, tension):
    # Bølge: stor udbredelse, lav tension
    freq = 1.4
    envelope = np.exp(-((X**2 + Y**2)/(15 - 2*tension)))
    wave = np.sin(freq*X + 0.7*freq*Y)
    spectral = wave * envelope * (1 - tension/8)
    # Partikel: lille udbredelse, høj tension
    solid = np.exp(-((X**2 + Y**2)/(0.6 + 6.8/tension)))
    # Glidende overgang
    return (1 - tension/8)*spectral + (tension/8)*solid

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
ax.set_zlim(-1.3, 1.3)
ax.set_axis_off()

# Start plot
Z = field(X, Y, tension_vals[0])
surf = [ax.plot_surface(X, Y, Z, cmap='plasma', linewidth=0, antialiased=False)]

def update(frame):
    ax.collections.clear()
    Z = field(X, Y, tension_vals[frame])
    surf[0] = ax.plot_surface(X, Y, Z, cmap='plasma', linewidth=0, antialiased=False)
    ax.set_title('Faseovergang: Felt (Bølge) $\rightarrow$ Stof (Partikel)', fontsize=15)
    return surf

ani = FuncAnimation(fig, update, frames=frames, blit=False, interval=75)
plt.show()

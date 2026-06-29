"""
simulate_observation_and_collaps.py

Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...
Ultra-Realistic Stencil-Based Flashlight Simulation
with Mouse Look (rotation only), Locked to Center,
Invisible Floor, and Frame Capture to GIF upon Escape.

Shapes supported: sphere, cube, pyramid, cylinder, icosahedron, torus
— rendered with dynamic lighting, environment‑mapped reflections, and self‑rotation.

New Features:
-------------
1) Press ESC to end simulation.
2) Every frame, capture the OpenGL framebuffer to build a GIF.
3) Always save a static PNG of the final frame ("flashlight_final.png").
4) Upon exit, generate "flashlight_field_mapping.png" with:
   - Yellow circle: observation radius
   - Red crosses: unobserved (potential) objects
   - Geometric markers:
       • White outlines: collapsed but not yet observed
       • Colored outlines: collapsed & observed
   - Legend showing each collapsed instance with its symbol & whether observed.
   - Little eye icon at center for observer location.
5) Flashlight cone now uses stencil buffering, always centered in view.
6) Default flashlight radius increased to 350 pixels.
7) Spotlight cone angle expanded and light intensity boosted.
8) Projection & view matrices are reset each frame so the cone follows mouse look.
9) True view‑dependent reflections via sphere‑map environment mapping,
   with graceful fallback if the map file isn’t found.
10) Observer fixed at center: all WASD movement disabled; only mouse rotation.
11) **Collapse logic “c”** is now derived from the pixel radius **and** your 45° FOV,
    now extended to account for object size (bounding‑sphere test).
"""

import os
import sys
import math
import random

import numpy as np
import pygame
from pygame.locals import *
import imageio
from OpenGL.GL import *
from OpenGL.GLU import *
import matplotlib.pyplot as plt

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir  = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from observation_and_collapse import observation_and_collapse

# ------------------------------------------------------------------
# Convergence plotting (Appendix W)
# ------------------------------------------------------------------
def generate_state_convergence(
    num_samples: int = 5000,
    t: float = 1.0,
    omega_range: tuple = (0.1, 10.0),
    save_path: str = "state_convergence_example.png"
):
    """
    Simulate and plot convergence of
        K_n = (1/n) * sum_{i=1}^n sin(f_i) * cos(g_i),
    where f_i = ω_i t + φ_i, g_i = ω_i t + ψ_i,
    ω_i ∼ Uniform(omega_range), φ_i, ψ_i ∼ Uniform(0,2π).

    Args:
        num_samples: number of samples to draw.
        t: observation time parameter.
        omega_range: frequency sampling range.
        save_path: file name for the saved plot.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    omega = np.random.uniform(omega_range[0], omega_range[1], size=num_samples)
    phi   = np.random.uniform(0, 2*np.pi, size=num_samples)
    psi   = np.random.uniform(0, 2*np.pi, size=num_samples)

    f = omega * t + phi
    g = omega * t + psi
    s = np.sin(f) * np.cos(g)

    K_vals = np.cumsum(s) / (np.arange(num_samples) + 1)

    plt.figure()
    plt.plot(np.arange(1, num_samples+1), K_vals)
    plt.xlabel('n')
    plt.ylabel(r"$K_n = \frac{1}{n}\sum_{i=1}^n \sin(f_i)\cos(g_i)$")
    plt.title('Convergence of Observation-Driven Collapse')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(current_dir, save_path), dpi=300)
    plt.close()
    print(f"Saved convergence plot: {save_path}")

def draw_cube(size):
    hs = size / 2
    glBegin(GL_QUADS)
    for normal, verts in (
        ((1,0,0),  [(hs,-hs,-hs),(hs,-hs,hs),(hs,hs,hs),(hs,hs,-hs)]),
        ((-1,0,0), [(-hs,-hs,hs),(-hs,-hs,-hs),(-hs,hs,-hs),(-hs,hs,hs)]),
        ((0,1,0),  [(-hs,hs,-hs),(hs,hs,-hs),(hs,hs,hs),(-hs,hs,hs)]),
        ((0,-1,0), [(-hs,-hs,hs),(hs,-hs,hs),(hs,-hs,-hs),(-hs,-hs,-hs)]),
        ((0,0,1),  [(-hs,-hs,hs),(-hs,hs,hs),(hs,hs,hs),(hs,-hs,hs)]),
        ((0,0,-1), [(hs,-hs,-hs),(hs,hs,-hs),(-hs,hs,-hs),(-hs,-hs,-hs)])
    ):
        glNormal3f(*normal)
        for v in verts:
            glVertex3f(*v)
    glEnd()

def draw_pyramid(size):
    hs, h = size/2, size
    glBegin(GL_QUADS)
    glNormal3f(0, -1, 0)
    for v in [(-hs,0,-hs),(hs,0,-hs),(hs,0,hs),(-hs,0,hs)]:
        glVertex3f(*v)
    glEnd()
    glBegin(GL_TRIANGLES)
    for a, b, c in [
        ((-hs,0,-hs),(hs,0,-hs),(0,h,0)),
        ((hs,0,-hs),(hs,0,hs),(0,h,0)),
        ((hs,0,hs),(-hs,0,hs),(0,h,0)),
        ((-hs,0,hs),(-hs,0,-hs),(0,h,0)),
    ]:
        ux, uy, uz = b[0]-a[0], b[1]-a[1], b[2]-a[2]
        vx, vy, vz = c[0]-a[0], c[1]-a[1], c[2]-a[2]
        nx, ny, nz = np.cross((ux,uy,uz),(vx,vy,vz))
        glNormal3f(nx, ny, nz)
        for v in (a,b,c):
            glVertex3f(*v)
    glEnd()

def draw_torus(r_major, r_minor, slices=24, loops=16):
    for i in range(slices):
        a0, a1 = 2*math.pi*i/slices, 2*math.pi*(i+1)/slices
        glBegin(GL_QUAD_STRIP)
        for j in range(loops+1):
            b = 2*math.pi*j/loops
            for a in (a0, a1):
                x = (r_major + r_minor*math.cos(b))*math.cos(a)
                y = (r_major + r_minor*math.cos(b))*math.sin(a)
                z = r_minor*math.sin(b)
                nx = math.cos(b)*math.cos(a)
                ny = math.cos(b)*math.sin(a)
                nz = math.sin(b)
                glNormal3f(nx, ny, nz)
                glVertex3f(x, y, z)
        glEnd()

def draw_circle_2d(x, y, radius, segments=64):
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(segments+1):
        theta = 2.0 * math.pi * i / segments
        glVertex2f(x + radius * math.cos(theta),
                   y + radius * math.sin(theta))
    glEnd()


class ObservationSimulation:
    def __init__(self, num_objects=10):
        # camera rotation only
        self.pitch, self.yaw       = 0.0, 0.0
        self.mouse_sens            = 0.2

        # flashlight
        self.flashlight_on         = False
        self.flashlight_radius     = 350
        self.spot_cutoff           = 0.0

        # window
        self.screen_width, self.screen_height = 800, 600

        # collapse & observation tracking
        self.observation_function = observation_and_collapse()
        self.collapsed           = set()
        self.observed            = set() 

        # objects
        self.shape_types = ['sphere','cube','pyramid','cylinder','icosahedron','torus']
        self.objects     = self.generate_objects()

        # envmap texture ID (or None)
        self.envmap_tex  = None
        self.gif_writer  = None

    def generate_objects(self):
        objs = []
        for _ in range(10):
            while True:
                x = random.uniform(-20,20)
                y = random.uniform(0.5,3.0)
                z = random.uniform(-20,20)
                d = math.sqrt(x*x + (y-1.5)**2 + (z+5)**2)
                if 8 <= d <= 15:
                    objs.append({
                        'pos'      : (x,y,z),
                        'size'     : random.uniform(0.5,2),
                        'color'    : (random.random(),random.random(),random.random()),
                        'shape'    : random.choice(self.shape_types),
                        'rot'      : random.uniform(0,360),
                        'axis'     : np.random.normal(size=3),
                        'rot_speed': random.uniform(10,60)
                    })
                    break
        return objs

    def load_envmap(self, filename):
        for base in (current_dir, parent_dir):
            full = os.path.join(base, filename)
            if os.path.isfile(full):
                try:
                    surf = pygame.image.load(full)
                except pygame.error:
                    return None
                data = pygame.image.tostring(surf, "RGB", True)
                w, h = surf.get_size()
                tex = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, tex)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0,
                             GL_RGB, GL_UNSIGNED_BYTE, data)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                return tex
        print(f"Warning: '{filename}' not found—reflections disabled.")
        return None

    def init_gl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.2,0.2,0.2,1])
        glClearColor(0,0,0,1)

        # load envmap
        self.envmap_tex = self.load_envmap('envmap.jpg')
        if self.envmap_tex:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.envmap_tex)
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
            glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
            glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
            glEnable(GL_TEXTURE_GEN_S)
            glEnable(GL_TEXTURE_GEN_T)

    def mouse_look(self):
        dx, dy = pygame.mouse.get_rel()
        self.yaw   += dx * self.mouse_sens
        self.pitch -= dy * self.mouse_sens
        self.pitch = max(min(self.pitch, 89.9), -89.9)

    def update_spotlight(self):
        # Recompute spot_cutoff from pixel radius + 45° FOV
        half_fovy = math.radians(45.0 / 2.0)
        focal_pix = self.screen_height / (2.0 * math.tan(half_fovy))
        self.spot_cutoff = math.degrees(math.atan(self.flashlight_radius / focal_pix))

        glEnable(GL_LIGHT0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glLightfv(GL_LIGHT0, GL_POSITION, [0,0,0,1])
        pr, yr = math.radians(self.pitch), math.radians(self.yaw)
        dx = math.cos(pr)*math.sin(yr)
        dy = math.sin(pr)
        dz = -math.cos(pr)*math.cos(yr)
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, [dx,dy,dz])
        glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, self.spot_cutoff)
        glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 32)
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1,1,1,1])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.5,1.5,1.5,1])
        glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.05,0.05,0.05,1])
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION,   0.0)
        glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION,0.0)

        glPopMatrix()

    def update_objects(self):
        for o in self.objects:
            x,y,z = o['pos']
            o['pos'] = (
                x + random.uniform(-0.01,0.01),
                y + random.uniform(-0.01,0.01),
                z + random.uniform(-0.01,0.01)
            )
            o['rot'] = (o['rot'] + o['rot_speed']*(1/60)) % 360

    def draw_objects(self):
        pr, yr = math.radians(self.pitch), math.radians(self.yaw)
        beam = np.array([
            math.cos(pr)*math.sin(yr),
            math.sin(pr),
            -math.cos(pr)*math.cos(yr)
        ])

        for idx, o in enumerate(self.objects):
            x,y,z = o['pos']
            v = np.array((x, y-1.5, z))  # camera at (0,1.5,0)
            d = np.linalg.norm(v)
            if self.flashlight_on and d > 0:
                # angle between beam axis and object center
                ang = math.degrees(math.acos(np.dot(beam, v/d)))
                # account for object's bounding radius
                bound_ang = 0.0
                if o['size'] < d:
                    bound_ang = math.degrees(math.asin(o['size'] / d))
                else:
                    bound_ang = 90.0
                # collapse & observe if any part enters cone
                if ang <= self.spot_cutoff + bound_ang:
                    self.collapsed.add(idx)
                    self.observed.add(idx)

            # set material & draw
            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (*o['color'],1))
            glMaterialfv(GL_FRONT, GL_SPECULAR, [1,1,1,1])
            glMaterialf(GL_FRONT, GL_SHININESS, 50)

            glPushMatrix()
            glTranslatef(x,y,z)
            ax = o['axis']/np.linalg.norm(o['axis'])
            glRotatef(o['rot'], *ax)
            s, sh = o['size'], o['shape']
            if   sh=='sphere':      gluSphere(gluNewQuadric(), s,   32,32)
            elif sh=='cube':        draw_cube(s)
            elif sh=='pyramid':     draw_pyramid(s)
            elif sh=='cylinder':
                q = gluNewQuadric()
                gluCylinder(q, s, s, s*2, 16,16)
            elif sh=='icosahedron':
                gluSphere(gluNewQuadric(), s,    8, 8)
            elif sh=='torus':       draw_torus(s, s/3)
            glPopMatrix()

    def capture_frame(self):
        data = glReadPixels(
            0, 0, self.screen_width, self.screen_height,
            GL_RGB, GL_UNSIGNED_BYTE
        )
        img = np.frombuffer(data, dtype=np.uint8)\
                 .reshape(self.screen_height, self.screen_width, 3)
        return np.flip(img, 0)

    def run_simulation(self):
        gif_path = os.path.join(current_dir, "simulation_record.gif")
        png_path = os.path.join(current_dir, "flashlight_final.png")
        map_path = os.path.join(current_dir, "flashlight_field_mapping.png")

        pygame.init()
        pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 8)
        pygame.display.set_mode((self.screen_width,self.screen_height),
                                DOUBLEBUF|OPENGL)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.screen_width/self.screen_height, 0.1, 50)
        glMatrixMode(GL_MODELVIEW)

        self.init_gl()
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        clock, running = pygame.time.Clock(), True
        self.gif_writer = imageio.get_writer(gif_path, mode='I', fps=20)

        while running:
            for e in pygame.event.get():
                if e.type == QUIT:
                    running = False
                elif e.type == KEYDOWN:
                    if e.key == K_ESCAPE:
                        running = False
                    elif e.key == K_f:
                        self.flashlight_on = not self.flashlight_on
                        print("Flashlight ON" if self.flashlight_on else "Flashlight OFF")
                    elif (e.mod & KMOD_CTRL) and e.key in (K_EQUALS, K_KP_PLUS):
                        self.flashlight_radius += 20
                    elif (e.mod & KMOD_CTRL) and e.key in (K_MINUS, K_KP_MINUS):
                        self.flashlight_radius = max(20, self.flashlight_radius - 20)

            self.mouse_look()

            glClear(GL_COLOR_BUFFER_BIT |
                    GL_DEPTH_BUFFER_BIT |
                    GL_STENCIL_BUFFER_BIT)

            if self.flashlight_on:
                glEnable(GL_STENCIL_TEST)
                glStencilFunc(GL_ALWAYS, 1, 0xFF)
                glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
                glStencilMask(0xFF)
                glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE)
                glDepthMask(GL_FALSE)
                glMatrixMode(GL_PROJECTION)
                glPushMatrix(); glLoadIdentity()
                glOrtho(0, self.screen_width, 0, self.screen_height, -1, 1)
                glMatrixMode(GL_MODELVIEW)
                glPushMatrix(); glLoadIdentity()
                draw_circle_2d(self.screen_width/2,
                               self.screen_height/2,
                               self.flashlight_radius)
                glPopMatrix()
                glMatrixMode(GL_PROJECTION)
                glPopMatrix()
                glMatrixMode(GL_MODELVIEW)
                glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE)
                glDepthMask(GL_TRUE)
                glStencilMask(0x00)
                glStencilFunc(GL_EQUAL, 1, 0xFF)
            else:
                glDisable(GL_STENCIL_TEST)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45, self.screen_width/self.screen_height, 0.1, 50)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glRotatef(-self.pitch, 1,0,0)
            glRotatef(-self.yaw,   0,1,0)

            if self.flashlight_on:
                glEnable(GL_LIGHTING)
                glEnable(GL_LIGHT0)
                self.update_spotlight()
                if self.envmap_tex:
                    glEnable(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_2D, self.envmap_tex)
                    glEnable(GL_TEXTURE_GEN_S)
                    glEnable(GL_TEXTURE_GEN_T)
            else:
                if self.envmap_tex:
                    glDisable(GL_TEXTURE_GEN_S)
                    glDisable(GL_TEXTURE_GEN_T)
                    glDisable(GL_TEXTURE_2D)
                glDisable(GL_LIGHT0)
                glDisable(GL_LIGHTING)

            self.update_objects()
            self.draw_objects()

            if not self.flashlight_on:
                glMatrixMode(GL_PROJECTION)
                glPushMatrix(); glLoadIdentity()
                glOrtho(0, self.screen_width, 0, self.screen_height, -1, 1)
                glMatrixMode(GL_MODELVIEW)
                glPushMatrix(); glLoadIdentity()
                glColor3f(0,0,0)
                glBegin(GL_QUADS)
                glVertex2f(0,0)
                glVertex2f(self.screen_width,0)
                glVertex2f(self.screen_width,self.screen_height)
                glVertex2f(0,self.screen_height)
                glEnd()
                glPopMatrix()
                glMatrixMode(GL_PROJECTION)
                glPopMatrix()
                glMatrixMode(GL_MODELVIEW)
                glEnable(GL_LIGHTING)
                glEnable(GL_LIGHT0)

            pygame.display.flip()
            self.gif_writer.append_data(self.capture_frame())
            clock.tick(60)

        # finalize captures & mapping
        self.gif_writer.close()
        print("Saved GIF:", gif_path)
        final = self.capture_frame()
        imageio.imsave(png_path, final)
        print("Saved PNG:", png_path)

        # --- field mapping code ---
        import pygame as pg
        pg.init()

        # square canvas so full circle never clipped
        map_size = max(self.screen_width, self.screen_height)
        map_surf = pg.Surface((map_size, map_size))
        map_surf.fill((0,0,0))

        center = map_size // 2
        # full yellow circumference
        pg.draw.circle(map_surf, (255,255,0), (center, center),
                       self.flashlight_radius, 2)
        # eye icon
        eye_rect = pg.Rect(center-10, center-5, 20, 10)
        pg.draw.ellipse(map_surf, (255,255,255), eye_rect, 1)
        pg.draw.circle(map_surf, (255,255,255), (center, center), 3)

        def world_to_map(x, z):
            mx = int((x + 20) / 40 * map_size)
            my = int((z + 20) / 40 * map_size)
            return mx, my

        for idx, o in enumerate(self.objects):
            mx, my = world_to_map(o['pos'][0], o['pos'][2])
            if idx in self.collapsed:
                color = (tuple(int(c*255) for c in o['color'])
                         if idx in self.observed else (255,255,255))
                size = max(4, int(o['size']*4))
                shape = o['shape']
                if shape == 'sphere':
                    pg.draw.circle(map_surf, color, (mx,my), size, 1)
                elif shape == 'cube':
                    pg.draw.rect(map_surf, color,
                                 pg.Rect(mx-size, my-size, 2*size,2*size), 1)
                elif shape == 'pyramid':
                    pts = [(mx, my-size), (mx-size, my+size), (mx+size, my+size)]
                    pg.draw.polygon(map_surf, color, pts, 1)
                elif shape == 'cylinder':
                    pg.draw.rect(map_surf, color,
                                 pg.Rect(mx-size, my-size, 2*size,2*size), 1)
                elif shape == 'icosahedron':
                    pts = [(mx+size,my), (mx,my-size), (mx-size,my), (mx,my+size)]
                    pg.draw.polygon(map_surf, color, pts, 1)
                elif shape == 'torus':
                    pg.draw.circle(map_surf, color, (mx,my), size, 1)
            else:
                pg.draw.line(map_surf, (255,0,0),
                             (mx-5,my-5),(mx+5,my+5),1)
                pg.draw.line(map_surf, (255,0,0),
                             (mx-5,my+5),(mx+5,my-5),1)

        # legend
        font = pg.font.SysFont(None, 20)
        lx, ly = 10, 10
        for idx in sorted(self.collapsed):
            o = self.objects[idx]
            if idx in self.observed:
                mcol = tuple(int(c*255) for c in o['color'])
                lbl = f"{o['shape']} #{idx} (observed)"
            else:
                mcol = (255,255,255)
                lbl = f"{o['shape']} #{idx} (collapsed)"
            pg.draw.circle(map_surf, mcol, (lx+8,ly+8), 5,1)
            txt = font.render(lbl, True, (200,200,200))
            map_surf.blit(txt, (lx+20,ly))
            ly += 20

        pg.image.save(map_surf, map_path)
        print("Saved field mapping:", map_path)
        pg.quit()
        # --- end field mapping ---

if __name__ == "__main__":
    # 1) Run main flashlight simulation
    sim = ObservationSimulation()
    sim.run_simulation()

    # 2) After simulation, generate Appendix W convergence example
    generate_state_convergence(
        num_samples=5000,
        t=1.0,
        omega_range=(0.1, 10.0),
        save_path="state_convergence_example.png"
    )
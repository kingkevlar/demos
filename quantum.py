"""
Fun with the Schrodinger equation!

A solution to the 2D Schrodinger equation is evolved in time given some
initial condition and a potential function. The hamiltonian used is that
of the quantum particle with dissipation, H = alph*del^2 + V + j*hbar*B

The wave function solution F is computed on an Lx by Ly grid and time is
discretized to a step of size dt. F is stored as a (2, Lx, Ly)-dimensional array,
where F[0] contains the real part of the solution and F[1] the imaginary part.
(I avoided Python's complex number type so I could take advantage of openCV).

The visualization maps phase angle to hue and relative magnitude to value.

"""
# Dependencies
from __future__ import division
import numpy as np; npl = np.linalg
import time
import cv2

# Visualization tools
fps = 30
disp = lambda name, P: cv2.imshow(name, cv2.resize(P/np.max(P), imshow_size))
def cdisp(name, F):
    mag = npl.norm(F, axis=0)
    ang = np.degrees(np.arctan2(F[1], F[0]) + np.pi)
    hsv = np.uint8(np.dstack((ang/2, 255*np.ones_like(mag), 255*mag/np.max(mag))))
    img = cv2.resize(cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR), imshow_size)
    cv2.imshow(name, img)
    return img

# Recording tools
record = False
if record: recorder = cv2.VideoWriter('quantum.avi', cv2.cv.CV_FOURCC(*'XVID'), fps, imshow_size)

# Computational tools
normalize = lambda F: F/npl.norm(F)
claplacian = lambda F: np.array((cv2.Laplacian(F[0], cv2.CV_64F), cv2.Laplacian(F[1], cv2.CV_64F)))
over_j = lambda F: np.array((F[1], -F[0]))
amp = lambda F: np.sum(F**2, axis=0)

# Physical constants
hbar = 1
mass = 0.1
alph = -(hbar**2)/(2*mass)

# Discrete solution space
dt = 0.0001
Lx, Ly = 50, 50
imshow_size = tuple(np.multiply(6, (Ly, Lx)))

# Initial condition
F = np.zeros((2, Lx, Ly), dtype=np.float64)
for x in xrange(Lx):
    for y in xrange(Ly):
        gauss = np.exp(-0.5*np.sqrt(5*(x-Lx/2)**2+5*(y-Ly/5)**2 - 100j*(y)))
        F[:, x, y] = np.real(gauss), np.imag(gauss)
F = normalize(F)

# Potential function
V = np.zeros((Lx, Ly), dtype=np.float64)
vl_a, vl_b = int(Ly/2.5), int(Ly/2.5)+2
V[:18, vl_a:vl_b], V[22:29, vl_a:vl_b], V[33:, vl_a:vl_b] = [50]*3
disp("Potential", V)

# Dissipation function
B = np.zeros((Lx, Ly), dtype=np.float64)
bthick = 10
for i in xrange(bthick):
    s = 100*(i/bthick)**3
    B[bthick-1-i, :vl_a] = s
    B[-(bthick-1-i)-1, :vl_a] = s
    B[:, bthick-1-i] = s
    # B[:, -(bthick-1-i)-1] = s
disp("Dissipation", B)

# Simulation
print("Press esc to quit.")
last_draw = 0
while True:
    start = time.time()

    # Draw frame
    if time.time() - last_draw > 1/fps:
        img = cdisp("Solution", F)
        key = cv2.waitKey(1)
        if key == 27: break
        last_draw = time.time()
        if record: recorder.write(img)

    # Increment wave function
    dFdt = over_j((alph*claplacian(F) + V*F)/hbar) - B*F
    F = F + dFdt*dt
    F = normalize(F)

    # Regulate sim speed
    elapsed = time.time() - start
    if elapsed < dt:
        time.sleep(dt - elapsed)

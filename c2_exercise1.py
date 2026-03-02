#Exercise1: Simple Euler Integration
import time
v, dt, g = [0.0, 0.1, -9.81] # Intitial velocity, time step, gravity

for i in range(1, 11):
    v += dt * g
    t = dt * i
    print(f"t = {t: .2f}  -  v = {v: .2f}")
    time.sleep(1)

#Exercise2: Free Oscillation of Mass-Spring-Damper
import matplotlib.pyplot as plt

class Oscillator:
    def __init__(self):
        # Physical parameters
        self.mass = 0.5 # kg
        self.spring_constant = 20.0 # N/m
        self.damping_coefficient = 0.5 # Ns/m

        # Constraints/Limits
        self.max_displacement = 0.1 # m
        self.max_velocity = 2.0 # m/s

        # Validation
        assert self.mass > 0, "Mass must be positive"
        assert self.spring_constant > 0, "Spring constant must be positive"
        assert self.damping_coefficient >= 0, "Damping coefficient must be no-negative"

        # State Variables
        self.position = 0.0
        self.velocity = 0.0
        self.acceleration = 0.0

    def set_initial_position(self, x0: float):
        if abs(x0) > self.max_displacement:
            raise ValueError(f"Initial position {x0} out of range")
        self.position = x0

class Simulation:
    def __init__(self, model: Oscillator):
        self.model = model
        self.history = {'t': [], 'x': []}
    
    def step(self, dt: float):
        m = self.model.mass
        d = self.model.damping_coefficient
        k = self.model.spring_constant

        # Calculation current acceleration
        self.model.acceleration = (-(d * self.model.velocity + self.model.position * k))/m
        # Calculation curent velocity
        self.model.velocity += self.model.acceleration * dt
        # Calculation current position
        self.model.position += self.model.velocity * dt

oscillator = Oscillator()
oscillator.set_initial_position(0.08)

sim = Simulation(oscillator)
dt = 0.01 # Time step (seconds)

for i in range(500):
    sim.history['t'].append(i*dt)
    sim.history['x'].append(oscillator.position)

    sim.step(dt)

# Ploting
plt.figure(figsize=(10, 5))
plt.plot(sim.history["t"], sim.history['x'], label="Position (m)")
plt.axhline(0, color='black', lw=1, ls='--')
plt.title("Free Oscillation of Mass-Spring-Damper")
plt.xlabel("Time (s)")
plt.ylabel("Displacement (m)")
plt.grid(True)
plt.legend()
plt.show()

    
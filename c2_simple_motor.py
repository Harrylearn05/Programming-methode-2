import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider


class SimpleMotor:
    def __init__(self):
        self.I_arm = 0.01
        self.I_motor = 0.001
        self.gear_ratio = 10.0
        self.damping = 0.1

        self.I_eff = self.I_arm + self.I_motor * pow(self.gear_ratio, 2)
        
        # PD parameters
        self.kp = 50.0
        self.kd = 5.0

        self.tau_max = 5.0

        # Simulation
        self.dt = 0.001
        self.T = 2.0
        self.steps = int(self.T/self.dt)
        self.time = np.arange(0, self.T, self.dt)

    def simulate(self, theta_target):
        theta_hist = np.zeros(self.steps)
        theta_dot_hist = np.zeros(self.steps)
        theta_ddot_hist = np.zeros(self.steps)
        torque_hist = np.zeros(self.steps)

        # inital_state
        curr_theta = 0.0
        curr_theta_dot = 0.0

        for i in range(self.steps):
            error = theta_target  - curr_theta
            motor_torque = self.kp * error - self.kd * curr_theta_dot
            motor_torque = np.clip(motor_torque, -self.tau_max, self.tau_max)
            joint_torque = motor_torque * self.gear_ratio
            theta_ddot = (joint_torque - self.damping * curr_theta_dot) / self.I_eff
            curr_theta_dot += theta_ddot * self.dt
            curr_theta += curr_theta_dot * self.dt
            theta_hist[i] = curr_theta
            theta_dot_hist[i] = curr_theta_dot
            theta_ddot_hist[i] = theta_ddot
            torque_hist[i] = motor_torque


        return (
            theta_hist, theta_dot_hist, theta_ddot_hist, torque_hist
        )


# -------------------------------------------------
# Instantiate motor and run initial simulation
# -------------------------------------------------
motor = SimpleMotor()
theta_target = np.pi / 2

theta_hist, theta_dot_hist, theta_ddot_hist, torque_hist = motor.simulate(theta_target)

# -------------------------------------------------
# Visualization
# -------------------------------------------------
arm_length = 0.3

fig = plt.figure(figsize=(12, 9))
gs = fig.add_gridspec(4, 2)

ax_arm = fig.add_subplot(gs[:, 0])
ax_pos = fig.add_subplot(gs[0, 1])
ax_vel = fig.add_subplot(gs[1, 1])
ax_acc = fig.add_subplot(gs[2, 1])
ax_tau = fig.add_subplot(gs[3, 1])

# ---- Arm plot ----
ax_arm.set_aspect("equal")
ax_arm.set_xlim(-0.4, 0.4)
ax_arm.set_ylim(-0.4, 0.4)
ax_arm.set_title("Motor + Arm")

housing = plt.Rectangle((-0.05, -0.05), 0.1, 0.1, color="gray")
ax_arm.add_patch(housing)

arm_line, = ax_arm.plot([], [], lw=4)

# ---- Position ----
ax_pos.set_xlim(0, motor.T)
ax_pos.set_ylim(-0.1, np.pi)
ax_pos.set_ylabel("Position [rad]")
ax_pos.grid()
pos_line, = ax_pos.plot([], [], label="θ")
target_line = ax_pos.axhline(theta_target, linestyle="--", color="r", label="target")
ax_pos.legend()

# ---- Velocity ----
ax_vel.set_xlim(0, motor.T)
ax_vel.set_ylim(-20, 20)
ax_vel.set_ylabel("Velocity [rad/s]")
ax_vel.grid()
vel_line, = ax_vel.plot([], [], color="tab:green")

# ---- Acceleration ----
ax_acc.set_xlim(0, motor.T)
ax_acc.set_ylim(-50, 50)
ax_acc.set_ylabel("Acceleration [rad/s²]")
ax_acc.grid()
acc_line, = ax_acc.plot([], [], color="tab:purple")

# ---- Torque ----
ax_tau.set_xlim(0, motor.T)
ax_tau.set_ylim(-motor.tau_max * 1.2, motor.tau_max * 1.2)
ax_tau.set_ylabel("Motor Torque [Nm]")
ax_tau.set_xlabel("Time [s]")
ax_tau.grid()
tau_line, = ax_tau.plot([], [], color="tab:orange")

# -------------------------------------------------
# Animation update
# -------------------------------------------------
def update(frame):
    angle = theta_hist[frame]

    # Arm
    x = arm_length * np.cos(angle)
    y = arm_length * np.sin(angle)
    arm_line.set_data([0, x], [0, y])

    # Plots
    t = motor.time[:frame]
    pos_line.set_data(t, theta_hist[:frame])
    vel_line.set_data(t, theta_dot_hist[:frame])
    acc_line.set_data(t, theta_ddot_hist[:frame])
    tau_line.set_data(t, torque_hist[:frame])

    return arm_line, pos_line, vel_line, acc_line, tau_line, target_line


ani = FuncAnimation(
    fig,
    update,
    frames=motor.steps,
    interval=motor.dt * 1000,
    blit=True,
)

# -------------------------------------------------
# Slider
# -------------------------------------------------
slider_ax = plt.axes([0.15, 0.02, 0.7, 0.03])
target_slider = Slider(slider_ax, "Target θ", 0.0, np.pi, valinit=theta_target)


def on_slider_change(val):
    global theta_hist, theta_dot_hist, theta_ddot_hist, torque_hist
    global theta_target

    theta_target = val
    target_line.set_ydata([val, val])

    # Re-run simulation with new target
    theta_hist, theta_dot_hist, theta_ddot_hist, torque_hist = motor.simulate(val)

    # Update y-axis limits
    ax_vel.set_ylim(
        -np.max(np.abs(theta_dot_hist)) * 1.2,
        np.max(np.abs(theta_dot_hist)) * 1.2,
    )
    ax_acc.set_ylim(
        -np.max(np.abs(theta_ddot_hist)) * 1.2,
        np.max(np.abs(theta_ddot_hist)) * 1.2,
    )

    # Clear existing line data before restarting
    pos_line.set_data([], [])
    vel_line.set_data([], [])
    acc_line.set_data([], [])
    tau_line.set_data([], [])

    # Restart animation from frame 0
    ani.frame_seq = ani.new_frame_seq()
    ani.event_source.stop()
    ani.event_source.start()


target_slider.on_changed(on_slider_change)

plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.show()
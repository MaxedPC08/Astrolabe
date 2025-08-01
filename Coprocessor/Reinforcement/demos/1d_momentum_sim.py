import time
import cv2
import numpy as np

class Optimizer:
    def __init__(self, weights, mins, maxs, stoc_rates=None, learning_rate=0.000001, not_reached_loss=1000):
        self.current = np.array(weights)
        self.prev_weights = []
        self.prev_losses = []
        self.mins = np.array(mins)
        self.maxs = np.array(maxs)
        self.learning_rate = learning_rate
        self.not_reached_loss = not_reached_loss
        if isinstance(stoc_rates, np.ndarray):
            self.stoc_rates = stoc_rates
        else:
            self.stoc_rates = np.ones_like(weights)

    def clip_weights(self, weights):
        return np.clip(weights, self.mins, self.maxs)

    def tell(self, weights, loss, reached=True):
        if not reached:
            loss = self.not_reached_loss

        weights = np.array(weights)
        if not weights.shape == self.current.shape:
            raise ValueError("weughts must be the same shape")
        
        try:
            loss = float(loss)
        except:
            raise TypeError("Loss must be a float")
        
        self.prev_weights.append(weights)
        self.prev_losses.append(loss)

    def ask(self, greedy = True):
        if greedy:
            return self._ask_greedy()

        print(np.array(self.prev_weights).shape)
        if len(self.prev_weights) == 0:
            return self.clip_weights(self.current + np.random.randn(*self.current.shape) * self.stoc_rates)
        
        if len(self.prev_weights) <= len(self.current):
            self.current = self.clip_weights(self.prev_weights[int(np.argmin(np.array(self.prev_losses)))] + np.random.randn(*self.current.shape) * self.stoc_rates)
            return self.current
        
        prev_weights_arr = np.array(self.prev_weights)[:-1]
        prev_losses_arr = np.array(self.prev_losses)[:-1]
        distances = np.abs(prev_weights_arr - self.current)

        # Repeat prev_losses_arr to match the shape of distances
        loss_diffs = (prev_losses_arr - self.prev_losses[-1]).reshape(-1, 1)
        weighted_slopes = loss_diffs / (distances**2 + 1e-8)  # add small epsilon to avoid division by zero
        dirty_grad = np.sum(np.array(weighted_slopes).reshape((-1, *self.current.shape)), 0)

        # Generate noise
        noise = np.random.randn(*dirty_grad.shape) * self.stoc_rates

        # Add noise to the gradient
        self.current = self.clip_weights(self.current + (dirty_grad * len(self.prev_weights) + noise ) / len(self.prev_weights) * self.learning_rate)
        return self.current
    
    def _ask_greedy(self):
        if len(self.prev_weights) <= 2:
            return self.clip_weights(self.current + np.random.randn(*self.current.shape) * self.stoc_rates)

        # Find the best previous weights (lowest loss)
        best_idx = np.argmin(np.array(self.prev_losses))
        best_weights = np.array(self.prev_weights)[best_idx]
        best_loss = self.prev_losses[best_idx]

        # Use all previous weights except the best for gradient estimation
        prev_weights_arr = np.delete(np.array(self.prev_weights), best_idx, axis=0)
        prev_losses_arr = np.delete(np.array(self.prev_losses), best_idx, axis=0)

        distances = np.abs(prev_weights_arr - best_weights)
        loss_diffs = (prev_losses_arr - best_loss).reshape(-1, 1)
        weighted_slopes = loss_diffs / (distances**2 + 1e-8)
        dirty_grad = np.sum(weighted_slopes.reshape((-1, *self.current.shape)), 0)

        noise = np.random.randn(*dirty_grad.shape) * self.stoc_rates

        # Optimize off the best version
        self.current = self.clip_weights(best_weights + (dirty_grad * len(self.prev_weights) + noise) / len(self.prev_weights) * self.learning_rate)
        return self.current

class Controller:
    def __init__(self, weights, mins, maxs, not_reached_error = 100, *args, **kwargs):
        self.opt = Optimizer(
            weights,
            mins,
            maxs,
            *args,
            **kwargs
        )
        self.not_reached_error = not_reached_error
        self.current = weights
        self.frames = []
        self.target = 0
        self.reached = False


    def evaluate_frames(self, frames, target):
        frames = np.asarray(frames)
        optimal_dist = abs(target - frames[0, 0])
        total_dist = np.sum(np.abs(frames[:, 0]))
        dists = frames[1:, 0] - frames[:-1, 0]
        times = frames[1:, 1] - frames[:-1, 1]
        speeds = np.abs(dists/times)
        max_speed = np.max(speeds)
        avg_speed = np.average(speeds)
        
        total_error = 5 * (total_dist / optimal_dist - 1) + (max_speed / avg_speed)
        return total_error
    
    def add_frame(self, frame):
        if not self.reached:
            self.frames.append(frame)

    def set_reached(self, reached):
        self.reached = reached
        if not reached:
            self.update(False)
            self.frames = []
        else:
            self.update()

    def tell(self, loss, weights=None):
        if not weights:
            weights = self.current
        self.opt.tell(weights, loss)

    def edit_controller(self, **kwargs):
        self.opt.edit_controller(**kwargs)
        
    
    def update(self, reached=True):
        if not len(self.frames) > 5:
            return self.current
        if reached:
            error = self.evaluate_frames(self.frames, self.target)
            print(error)
        else:
            error = self.not_reached_error
        self.frames = []
        self.opt.tell(self.current, error)
        self.current = self.opt.ask()
        # self.save(self.filename)
        return self.current
    
    def get_weights(self):
        return self.current

class PID:
    def __init__(self, Kp, Ki, Kd, setpoint=0.0, output_limits=(None, None)):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.setpoint = setpoint
        self.integral = 0.0
        self.last_error = None
        self.output_limits = output_limits  # (min, max)

    def reset(self):
        self.integral = 0.0
        self.last_error = None

    def compute(self, measurement, dt):
        error = self.setpoint - measurement
        self.integral += error * dt

        derivative = 0.0
        if self.last_error is not None:
            derivative = (error - self.last_error) / dt

        self.last_error = error

        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # Clamp output
        min_out, max_out = self.output_limits
        if min_out is not None:
            output = max(min_out, output)
        if max_out is not None:
            output = min(max_out, output)

        return output

class RLPIDController(Controller):
    class PIDController:
        def __init__(self, kp, ki, kd):
            self.kp = kp
            self.ki = ki
            self.kd = kd
            self.reset()

        def set_pid(self, kp, ki, kd):
            self.kp = kp
            self.ki = ki
            self.kd = kd

        def reset(self):
            self.integral = 0.0
            self.prev_error = 0.0

        def step(self, error, dt):
            self.integral += error * dt
            derivative = (error - self.prev_error) / dt
            output = self.kp * error + self.ki * self.integral + self.kd * derivative
            self.prev_error = error
            return -output
    def __init__(self, weights, mins, maxs, not_reached_error = 100, *args, **kwargs):
        self.pid = self.PIDController(*weights)
        super().__init__(weights, mins, maxs, not_reached_error=not_reached_error, *args, **kwargs)

    def update(self, reached=True):
        weights = super().update(reached)
        self.pid.set_pid(*weights)
        return weights
    
    def reset(self):
        self.pid.reset()
    
        
    def compute(self, error, dt):
        return self.pid.step(error, dt)


controllers = [
    PID(1, 0.1, 0.1),
    PID(2.0454754357520892, 0.0, 0.9045939537000289)
]

smart_controllers = [
    RLPIDController([1, 0.1, 0.1], [0.01, 0, 0], [10, 1, 1], stoc_rates=[0.01, 0.001, 0.001])
]

total_controllers = controllers + smart_controllers

# Parameters
WIDTH = 1600
LANE_HEIGHT = 60
N_AGENTS = len(total_controllers)
HEIGHT = N_AGENTS * LANE_HEIGHT
GOAL_POS = 700
DT = 0.1
DAMPING = 0.9
ACCELERATION = 10.0
MAX_V = 1000

# Colors for each agent
COLORS = [(255, 0, 0), (0, 128, 255), (128, 0, 128), (0, 200, 0), (0, 0, 0)]

agents = []
for i, controller in enumerate(controllers):
    agents.append({
        "x": 100.0,
        "v": 0.0,
        "pid": controller,
        "color": COLORS[i % len(COLORS)],
        "done": False,
        "smart":False
    })

for i, controller in enumerate(smart_controllers):
    agents.append({
        "x": 100.0,
        "v": 0.0,
        "pid": controller,
        "color": COLORS[(i + len(controllers)) % len(COLORS)],
        "done": False,
        "smart":True
    })

def draw_scene(agents):
    img = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255

    # Draw goal as a vertical line
    cv2.line(img, (GOAL_POS, 0), (GOAL_POS, HEIGHT), (0, 200, 0), 2)

    for idx, agent in enumerate(agents):
        x = int(agent["x"])
        y = int(idx * LANE_HEIGHT + LANE_HEIGHT // 2)
        color = agent["color"]

        # Draw agent
        cv2.circle(img, (x, y), 8, color, -1)

        # Label velocity and done status with colored box
        text = f"v={agent['v']:.1f} done={agent['done']}"
        (text_w, text_h), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        box_color = (0, 200, 0) if agent['done'] else (0, 0, 200)  # green if done, red if not
        box_x, box_y = 8, y - 10 - text_h + baseline
        cv2.rectangle(img, (box_x - 2, box_y - 2), (box_x + text_w + 2, box_y + text_h + 2), box_color, -1)
        cv2.putText(img, text, (box_x, y - 10 + baseline), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

    return img

# Simulation loop
while True:
    for agent in agents:
        x = agent["x"]
        v = agent["v"]
        pid_controller = agent["pid"]

        # Only update if not done
        if not agent["done"]:
            error = GOAL_POS - x
            a = -pid_controller.compute(error, DT)

            v += a * ACCELERATION * DT
            # v = np.clip(v, -MAX_V, MAX_V)
            v *= DAMPING
            x += v * DT
            x = np.clip(x, 0, WIDTH - 1)

            agent["x"] = x
            agent["v"] = v

            if agent["smart"]:
                agent["pid"].add_frame([error, time.time()])

            # Check if done: very close to goal and nearly stopped
            if abs(x - GOAL_POS) < 2 and abs(v) < 0.2:
                agent["done"] = True
                if agent["smart"]:
                    agent["pid"].set_reached(True)

    # Draw scene
    img = draw_scene(agents)
    cv2.imshow("Stacked Multi-PID Simulation", img)

    key = cv2.waitKey(30)
    if key == ord('q'):
        break
    elif key == ord('a'):
        # Move goal and reset PIDs
        GOAL_POS = np.random.randint(150, WIDTH - 150)
        for agent in agents:
            agent["pid"].integral = 0.0
            agent["pid"].prev_error = 0.0
            agent["done"] = False  # Reset done flag
        
        for controller in smart_controllers:
            controller.set_reached(False)

cv2.destroyAllWindows()

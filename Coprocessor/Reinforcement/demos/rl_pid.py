from Reinforcement.controller import Controller

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

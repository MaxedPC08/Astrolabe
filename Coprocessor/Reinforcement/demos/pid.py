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

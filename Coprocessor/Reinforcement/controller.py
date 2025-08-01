import numpy as np
from Reinforcement.optimizer import Optimizer

class Controller:
    def __init__(self, weights, mins, maxs, not_reached_error = 100, filename=None, load=False, *args, **kwargs):
        if load and not filename:
            raise ValueError("You must pass a name to load from.")
        
        if load:
            self.load(filename)

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
        self.filename = filename

    def load(self, filename):
        if not self.filename:
            return self.opt.load(filename)
        
    def save(self, filename):
        if not self.filename:
            self.opt.save(filename)

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

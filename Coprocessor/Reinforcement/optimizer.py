import numpy as np
import os
import json

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

    def load(self, filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "Data", filename)
        if not os.path.exists(data_path):
            print(f"File {data_path} does not exist.")
            return False
        
        with open(data_path, "r") as f:
            data = json.load(f)
            self.current = np.array(data["current"])
            self.prev_weights = [np.array(w) for w in data["prev_weights"]]
            self.prev_losses = data["prev_losses"]
            self.mins = np.array(data["mins"])
            self.maxs = np.array(data["maxs"])
            self.learning_rate = data["learning_rate"]
            self.stoc_rates = np.array(data["stoc_rates"])
            self.not_reached_loss = data["not_reached_loss"]

        return True
    
    def edit_controller(self, **kwargs):
        if "mins" in kwargs:
            self.mins = np.array(kwargs["mins"])
        if "maxs" in kwargs:
            self.maxs = np.array(kwargs["maxs"])
        if "stoc_rates" in kwargs:
            self.stoc_rates = np.array(kwargs["stoc_rates"])
        if "learning_rate" in kwargs:
            self.learning_rate = kwargs["learning_rate"]
        if "not_reached_loss" in kwargs:
            self.not_reached_loss = kwargs["not_reached_loss"]
        if "current" in kwargs:
            self.current = np.array(kwargs["current"])

    def save(self, filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "Data", filename)
        data = {
            "current": self.current.tolist(),
            "prev_weights": [w.tolist() for w in self.prev_weights],
            "prev_losses": self.prev_losses,
            "mins": self.mins.tolist(),
            "maxs": self.maxs.tolist(),
            "learning_rate": self.learning_rate,
            "stoc_rates": self.stoc_rates.tolist(),
            "not_reached_loss": self.not_reached_loss
        }
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        with open(data_path, "w") as f:
            json.dump(data, f)

        return True


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

from Reinforcement.controller import Controller
import numpy as np
import os
import json

class ControllerFunctionalObject:
    def __init__(self, *args, **kwargs):
        self.function_dict = {
            "add_controller": self.add_controller,
            "edit_controller": self.edit_controller,
            "remove_controller": self.remove_controller,
            "add_frame": self.add_frame,
            "update": self.update,
            "get_weights": self.get_weights,
            "tell": self.tell,
            "function_info": self.function_info
        }
        self.controllers = {}
        #TODO: Load controllers from a file if it exists

    async def add_controller(self, websocket, name, weights, mins, maxs, stoc_rate, learning_rate=0.01, not_reached_error=100):
        """Add a new controller to the system."""
        if name in self.controllers:
            raise ValueError(f"Controller with name {name} already exists.")
        
        if not isinstance(weights, (list, np.ndarray)):
            raise TypeError("Weights must be a list or numpy array.")
        if not isinstance(mins, (list, np.ndarray)):
            raise TypeError("Mins must be a list or numpy array.")
        if not isinstance(maxs, (list, np.ndarray)):
            raise TypeError("Maxs must be a list or numpy array.")
        
        self.controllers[name] = Controller(
            weights, mins, maxs,
            not_reached_error=not_reached_error,
            filename=name+".json",
            load=True,
            stoc_rate=stoc_rate,
            learning_rate=learning_rate
        )

        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "Data", "controllers.json")
        
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        with open(data_path, "w") as f:
            json.dump(self.controllers.keys(), f)

        websocket.send(json.dumps({"status": "ok", "name": name}))

        return True
    
    async def edit_controller(self, websocket, name, **kwargs):
        """Edit an existing controller's parameters."""
        if name  in self.controllers:
            self.controllers[name].edit_controller(**kwargs)
            websocket.send(json.dumps({"status": "ok", "name": name}))
        else:
            websocket.send(json.dumps({"status": "error", "error": f"Controller {name} does not exist."}))
        
    
    async def remove_controller(self, websocket, name):
        """Remove a controller by name."""
        if name in self.controllers:
            del self.controllers[name]
            websocket.send(json.dumps({"status": "ok", "name": name}))
        else:
            websocket.send(json.dumps({"status": "error", "error": f"Controller {name} does not exist."}))


    async def add_frame(self, websocket, name, frame):
        """Add a movement frame to a controller."""
        if name in self.controllers:
            self.controllers[name].add_frame(frame)
            websocket.send(json.dumps({"status": "ok", "name": name}))
        else:
            websocket.send(json.dumps({"status": "error", "error": f"Controller {name} does not exist."}))

    async def update(self, websocket, name, target_reached):
        """Update the controller with whether the target was reached."""
        if name in self.controllers:
            self.controllers[name].set_reached(target_reached)
            websocket.send(json.dumps({"status": "ok", "name": name}))
        else:
            websocket.send(json.dumps({"status": "error", "error": f"Controller {name} does not exist."}))

    async def get_weights(self, websocket, name):
        """Get the current weights for a controller."""
        if name in self.controllers:
            websocket.send(json.dumps({"status": "ok", "name": name, "weights": self.controllers[name].get_weights()}))
        else:
            websocket.send(json.dumps({"status": "error", "error": f"Controller {name} does not exist."}))

    async def tell(self, websocket, name, loss, weights=None):
        """Provide feedback to the controller."""
        if name in self.controllers:
            self.controllers[name].tell(loss, weights)
            websocket.send(json.dumps({"status": "ok", "name": name}))
        else:
            websocket.send(json.dumps({"status": "error", "error": f"Controller {name} does not exist."}))

    async def function_info(self, websocket, *args, **kwargs):
        """Provide information about the functions available in this object."""
        
        add_controller = {
            "description": "Add a new controller to the system.",
            "arguments": {
                "name": {"type": "string", "description": "Name of the controller."},
                "weights": {"type": "list", "description": "Initial weights for the controller."},
                "mins": {"type": "list", "description": "Minimum values for the controller."},
                "maxs": {"type": "list", "description": "Maximum values for the controller."},
                "stoc_rate": {"type": "list", "description": "Stochastic rate for the controller."},
                "learning_rate": {"type": "float", "description": "Learning rate for the controller."}
            },
            "returns": {"status": {"type": "string", "description": "Status of the operation."}}
        }

        edit_controller = {
            "description": "Edit an existing controller's parameters.",
            "arguments": {
                "name": {"type": "string", "description": "Name of the controller."},
                "weights": {"type": "list", "description": "Initial weights for the controller."},
                "mins": {"type": "list", "description": "Minimum values for the controller."},
                "maxs": {"type": "list", "description": "Maximum values for the controller."},
                "stoc_rate": {"type": "list", "description": "Stochastic rate for the controller."},
                "learning_rate": {"type": "float", "description": "Learning rate for the controller."}
            },
            "returns": {"status": {"type": "string", "description": "Status of the operation."}}
        }

        remove_controller = {
            "description": "Remove a controller by name.",
            "arguments": {
                "name": {"type": "string", "description": "Name of the controller to remove."}
            },
            "returns": {"status": {"type": "string", "description": "Status of the operation."}}
        }

        add_frame = {
            "description": "Add a movement frame to a controller.",
            "arguments": {
                "name": {"type": "string", "description": "Name of the controller."},
                "frame": {"type": "list", "description": "Movement frame to add. The last element should be the current time."}
            },
            "returns": {"status": {"type": "string", "description": "Status of the operation."}}
        }

        update = {
            "description": "Update the controller with whether the target was reached. If the target was not reached, the controller will be updated with a penalty and begin expecting a new movement.",
            "arguments": {
                "name": {"type": "string", "description": "Name of the controller."},
                "target_reached": {"type": "boolean", "description": "Whether the target was reached."}
            },
            "returns": {"status": {"type": "string", "description": "Status of the operation."}}
        }

        get_weights = {
            "description": "Get the current weights for a controller.",
            "arguments": {
                "name": {"type": "string", "description": "Name of the controller."}
            },
            "returns": {
                "status": {"type": "string", "description": "Status of the operation."},
                "weights": {"type": "list", "description": "Current weights of the controller."}
            }
        }
        tell = {
            "description": "Provide feedback to the controller. Note that the controller aims to reduce the loss value over time.",
            "arguments": {
                "name": {"type": "string", "description": "Name of the controller."},
                "loss": {"type": "float", "description": "Loss value to provide to the controller."},
                "weights": {"type": "list", "description": "Weights that produced the given loss."}
            },
            "returns": {"status": {"type": "string", "description": "Status of the operation."}}
        }
        function_info = {
            "add_controller": add_controller,
            "edit_controller": edit_controller,
            "remove_controller": remove_controller,
            "add_frame": add_frame,
            "update": update,
            "get_weights": get_weights,
            "tell": tell
        }
        await websocket.send(json.dumps(function_info))
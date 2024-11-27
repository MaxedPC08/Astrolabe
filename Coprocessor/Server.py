import asyncio
import websockets
import socket
import inspect
from Functional import FunctionalObject


class Server:
    def __init__(self, name, serial_number, port=50000):
        # Get the IP address of the Ethernet interface
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.ethernet_ip = s.getsockname()[0]
            s.close()
        except socket.error as e:
            print(f"Error obtaining IP address: {e}")
            self.ethernet_ip = "127.0.0.1"  # Fallback to localhost

        self.functional_object = FunctionalObject(name, serial_number)
        self.port = port

    # WebSocket server
    async def websocket_server(self, websocket, path):
        """
        This function is the main function for the WebSocket server.
        It receives images from the client and sends them back.
        :param websocket:
        :param path:
        :return:
        """
        try:
            async for message in websocket:
                split_message = message.split(" -")
                args = {}
                if len(split_message) > 1:
                    for i, arg in enumerate(split_message[1:]):
                        try:
                            parameter, val = arg.split("=")
                        except ValueError as e:
                            message = str(e)
                            if "too many values to unpack" in message:
                                # Handle the case where there are too many values
                                await websocket.send('{"error" : "' + f"""Error: Too many values to unpack.
                                Please make sure that the parameters are the format "parameter1=value1 
                                -parameter2=value2".
                                Do not include spaces between the parameter and the value, and do not include equal 
                                signs in the value.""" + '"}')
                                continue
                            elif "too few values to unpack" in message:
                                # Handle the case where there are too few values
                                await websocket.send('{"warning" : "' + f"""Warning: Too few values to unpack. We are 
                                setting this parameter to true.
                                                        Please make sure that the parameters are the format 
                                                        "parameter1=value1 -parameter2=value2".
                                                        Do not include spaces between the parameter and the value, and 
                                                        make sure that all parameters have values.""" + '"}')
                                parameter = arg
                                val = True
                            else:
                                # Handle other ValueError cases or re-raise
                                raise
                        except KeyError as e:
                            print(f"Error: Function {split_message[0]} not found. Please make sure that the function "
                                  f"name is "
                                  f"spelled correctly and that it exists. The function names are case-sensitive. "
                                  f"The full error is {e}")
                            await websocket.send('{"error" : "' + f"Error: Function {split_message[0]} not found."
                                                 f" Please make sure that the function name is spelled correctly "
                                                                  f"and that it exists."
                                                 f" The function names are case-sensitive."
                                                 f" The full error is {e}" + '"}')

                        except TypeError as e:
                            print(f"{e} when calling function {split_message[0]} with arguments {args}."
                                  f" Please make sure that the function is called with the "
                                  f"correct number of arguments.")
                            await websocket.send('{"error" : "' + f"{e} when calling function {split_message[0]} "
                                                 f"with arguments {args}."
                                                 f" Please make sure that the function is called with the correct "
                                                 f"number of arguments." + '"}')
                        try:
                            args[parameter] = val
                        except Exception as e:
                            print(f"Error: {e}")
                            await websocket.send('{"error" : "' + f"{e}" + '"}')

                try:
                    if inspect.iscoroutinefunction(self.functional_object.functionDict[split_message[0]]):
                        await self.functional_object.functionDict[split_message[0]](websocket, **args)
                    else:
                        self.functional_object.functionDict[split_message[0]](**args)

                except ValueError as e:
                    print(f"Error: {e}")
                    await websocket.send('{"error" : "' + f"{e}" + '"}')
                except KeyError as e:
                    await websocket.send('{"error" : "' + f"Error: Function {split_message[0]} not found."
                                         f" Please make sure that the function name is spelled correctly and that it "
                                                          f"exists."
                                         f" The function names are case-sensitive. The full error is {e}" + '"}')
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed with error: {e}")
        except Exception as e:
            await websocket.send('{"error" : "' + f"An error occurred: {e}" + '"}')
            print(f"An error occurred: {e}")
        finally:
            await websocket.close()

    def start_server(self):
        start_server = websockets.serve(self.websocket_server, self.ethernet_ip, self.port)
        print(f"Server started at ws://{self.ethernet_ip}:{self.port} for {self.functional_object.name}")
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

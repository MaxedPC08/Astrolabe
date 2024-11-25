package com.example.robotcode.subsystem;

import org.json.*;

import edu.wpi.first.wpilibj2.command.SubsystemBase;
import com.example.robotcode.constants;

import com.example.robotcode.websocket.WebSocketClient;

public class ExampleSubsystem extends SubsystemBase {

    final WebSocketClient wsc;

    public SubSystemBase() {

        // creates a new websocket client
        // the URL should be IP of the server, including the port
        wsc = new WebSocketClient(constants.websocketURL);
        
        // adds a message handler to the client object so that it can receive data
        wsc.addMessageHandler(new WebSocketClient.MessageHandler() {

            // simple example to demonstrate the byte array parameter 
            public void handleMessage(byte[] message) {

                byte biggestPixel = Byte.MIN_VALUE;
                
                // loops throught the array of bytes, looking for the biggest value
                for (byte data : message) {
                    if (biggestPixel < data) {
                        biggestPixel = data;
                    }
                }

            }

            // simple example to demonstrate the stringified JSON parameter
            // please refer to https://github.com/stleary/JSON-java for more info about the json package
            public void handleMessage(String message) {
                JSONObject json = new JSONObject(message); 
                String error = json.getJSONObject("error");
                if (error != null) {
                    // we got a good json response, process it here
                } else {
                    // we got an error, process and/or throw something here
                }
            }
        });

    }

    // sends message to the websocket server
    public sendMessage(String message) {
        // stops trying to send the message if an object hasn't been created
        // this can be changed to behave however you like
        if (wsc == null) return;
        wsc.sendMessage(message);
    }

}

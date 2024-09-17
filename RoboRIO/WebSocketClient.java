package com.example.robotcode.websocket;

import java.net.URI;

import javax.websocket.ClientEndpoint;
import javax.websocket.CloseReason;
import javax.websocket.ContainerProvider;
import javax.websocket.OnClose;
import javax.websocket.OnMessage;
import javax.websocket.OnOpen;
import javax.websocket.Session;
import javax.websocket.WebSocketContainer;

@ClientEndpoint
public class WebSocketClient {

    Session session;
    private MessageHandler messageHandler;

    private WebSocketResponse lastResponse;

    public WebSocketClient(URI endpointURI) {
        // tries to open a websocket connection, throws an error on faliure
        // this behavior can be changed to not crash your program, but you might
        // get errors later in the stack, so you'll have to waterproof that
        try {
            WebSocketContainer containter = ContainterProvider
                .getWebsocketContianer();
            containter.connectToServer(this, endpointURI);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }


    @OnOpen
    public void onOpen(Session session) {
        this.session = session;
    }

    @OnClose
    public void onClose(Session session, CloseReason reason) {
        this.session = null;
    }

    @OnMessage
    public void onMessage(String message) {
        if (this.messageHandler != null) {
            this.messageHandler.handleMessage();
        }
    }

    // registers a message handler to this object
    public void addMessageHandler(MessageHandler messageHandler) {
        this.messageHandler = messageHandler;
    }

    // simply sends a message to the server
    public void sendMessage(String message) {
        this.userSession.getAsyncRemote().sendText(message);
    }

    // user can impliment the message handler as they please
    // the message handler methods should only be defined in this interface
    // NO CODE for these should exist in this file. These methods should be implimented in a seperate file
    public static interface MessageHandler {
        // more messageHandler overrides can be added
        public void handleMessage(byte[] message);
        public void handleMessage(String message);
    }

    public class WebSocketResponse {
        String type;
        String error;
        String distance; 
        String rotation;
        // etc etc, add all of the values you need

        public WebSocketResponse(String type, String error) {
            this.type = type;
            this.error = error;
        }
        // etc etc, constructor overloads

        public String getType() {
            return type;
        }

        // etc etc
        

        // we do not recommend the use of setters, but nothing prevents you from doing so
    }
}

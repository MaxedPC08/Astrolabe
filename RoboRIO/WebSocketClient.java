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

    public ChatClientEndpoint(URI endpointURI) {
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
    public void onOpen(Session session, CloseReason reason) {
        this.session = null;
    }

    @OnMessage
    public void onMessage(String message) {
        if (this.messageHandler != null) {
            this.messageHandler.handleMessage();
        }
    }

    public void addMessageHandler(MessageHandler messageHandler) {
        this.messageHandler = messageHandler;
    }

    public void sendMessage(String message) {
        this.userSession.getAsyncRemote().sendText(message);
    }

    public static interface MessageHandler {
        public void handleMessage(String message);
    }
}

package com.example.robotcode.websocket;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.WebSocket;
import java.net.http.WebSocket.Listener;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletionStage;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

public class WebSocketClient {
    private String ip = "ws://10.42.0.118:50000";
    private WebSocket webSocket;
    private double rotation;
    private volatile String latestReply = "";
    private CountDownLatch messageLatch = new CountDownLatch(1);
    private final int TIMEOUT;

    public static class Color {
        public double red;
        public double green;
        public double blue;
        public double difference;
        public double blur;
    }

    public static class Info {
        public String cameraName;
        public String identifier;
        public double horizontalFocalLength;
        public double verticalFocalLength;
        public int height;
        public int horizontalResolutionPixels;
        public int verticalResolutionPixels;
        public int processingScale;
        public double tiltAngleRadians;
        public double horizontalFieldOfViewRadians;
        public double verticalFieldOfViewRadians;
        public List<Color> colorList;
        public int activeColor;
        public String fullString;
    }

    public static class Apriltag {
        public String tagId;
        public double[] position;
        public double[] orientation;
        public double distance;
        public double horizontalAngle;
        public double verticalAngle;
        public String fullString;
    }

    public CameraWebsocketClient() {
        TIMEOUT = 5000;
    }

    public CameraWebsocketClient(String ip, int timeout) {
        TIMEOUT = timeout;
        this.ip = ip;
    }

    public boolean setupConnection() {
        try{
            HttpClient client = HttpClient.newHttpClient();
            webSocket = client.newWebSocketBuilder()
                    .buildAsync(URI.create(ip), new WebSocketListener(this))
                    .join();
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
        return isConnected();
    }

    public boolean isConnected() {
        return webSocket != null && webSocket.isOutputClosed() == false && webSocket.isInputClosed() == false;
    }

    public void sendMessage(String message) {
        webSocket.sendText(message, true);
    }

    public void onMessage(String newMessage) {
        System.out.println("Received message: " + newMessage);
        this.latestReply = newMessage;
        messageLatch.countDown();
    }

    public String getMessage() {
        return latestReply;
    }

    public String getLatestReply() {
        try {
            messageLatch.await(TIMEOUT, TimeUnit.MILLISECONDS); // Wait for up to 5 seconds
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return latestReply;
    }

    public void clear() {
        latestReply = "";
      }

    public JsonObject decodeJson(String jsonString) {
        Gson gson = new Gson();
        return gson.fromJson(jsonString, JsonObject.class);
    }

    public double getRotation() {
        return rotation;
    }

    public void setRotation(double rotation) {
        this.rotation = rotation;
    }

    public Info getInfo() {
        try {
            sendMessage("info");
            String newMessage = getLatestReply();
            return getInfoFromString(newMessage);
        } catch (Exception e) {
            return new Info();
        }
    }

    private Info getInfoFromString(String pMessage) {
        if (pMessage == null){
            return null;
        }
        try {
            JsonObject json = decodeJson(pMessage);
            Info info = new Info();
            info.cameraName = json.get("cam_name").getAsString();
            info.identifier = json.get("identifier").getAsString();
            info.horizontalFocalLength = json.get("horizontal_focal_length").getAsDouble();
            info.verticalFocalLength = json.get("vertical_focal_length").getAsDouble();
            info.height = json.get("height").getAsInt();
            info.horizontalResolutionPixels = json.get("horizontal_resolution_pixels").getAsInt();
            info.verticalResolutionPixels = json.get("vertical_resolution_pixels").getAsInt();
            info.processingScale = json.get("processing_scale").getAsInt();
            info.tiltAngleRadians = json.get("tilt_angle_radians").getAsDouble();
            info.horizontalFieldOfViewRadians = json.get("horizontal_field_of_view_radians").getAsDouble();
            info.verticalFieldOfViewRadians = json.get("vertical_field_of_view_radians").getAsDouble();
            info.activeColor = json.get("active_color").getAsInt();
            info.colorList = new ArrayList<>();
            for (var colorJson : json.getAsJsonArray("color_list")) {
                Color color = new Color();
                JsonObject colorObject = colorJson.getAsJsonObject();
                color.red = colorObject.get("red").getAsDouble();
                color.green = colorObject.get("green").getAsDouble();
                color.blue = colorObject.get("blue").getAsDouble();
                color.difference = colorObject.get("difference").getAsDouble();
                color.blur = colorObject.get("blur").getAsDouble();
                info.colorList.add(color);
            }
            info.fullString = pMessage;
            return info;
        } catch (Exception e) {
            System.out.println("Error getting info");
            e.printStackTrace();
            return new Info();
        }
    }

    public List<Apriltag> getApriltags() {
        try {
            sendMessage("fa");
            String newMessage = getLatestReply();
            return getApriltagsFromString(newMessage);
        } catch (Exception e) {
            e.printStackTrace();
            if (setupConnection()) {
                sendMessage("fa");
                String newMessage = getLatestReply();
                return getApriltagsFromString(newMessage);
            }
            return new ArrayList<>();
        }
    }

    private List<Apriltag> getApriltagsFromString(String pMessage) {
        if (pMessage == null){
            return null;
        }
        try {
            JsonArray jsonArray = new Gson().fromJson(pMessage, JsonArray.class);
            List<Apriltag> apriltags = new ArrayList<>();

            if (jsonArray != null && jsonArray.size() > 0) {
                for (var apriltagJson : jsonArray) {
                    Apriltag apriltag = new Apriltag();
                    JsonObject apriltagObject = apriltagJson.getAsJsonObject();
                    apriltag.tagId = apriltagObject.get("tag_id").getAsString();
                    apriltag.position = new double[]{
                            apriltagObject.get("position").getAsJsonArray().get(0).getAsDouble(),
                            apriltagObject.get("position").getAsJsonArray().get(1).getAsDouble(),
                            apriltagObject.get("position").getAsJsonArray().get(2).getAsDouble()
                    };
                    apriltag.orientation = new double[]{
                            apriltagObject.get("orientation").getAsJsonArray().get(0).getAsDouble(),
                            apriltagObject.get("orientation").getAsJsonArray().get(1).getAsDouble(),
                            apriltagObject.get("orientation").getAsJsonArray().get(2).getAsDouble()
                    };
                    apriltag.distance = apriltagObject.get("distance").getAsDouble();
                    apriltag.horizontalAngle = apriltagObject.get("horizontal_angle").getAsDouble();
                    apriltag.verticalAngle = apriltagObject.get("vertical_angle").getAsDouble();
                    apriltags.add(apriltag);
                }
                apriltags.get(0).fullString = pMessage;
            }

            return apriltags;
        } catch (Exception e) {
            e.printStackTrace();
            return new ArrayList<>();
        }
    }

    private static class WebSocketListener implements Listener {
        private final CameraWebsocketClient client;

        public WebSocketListener(CameraWebsocketClient client) {
            this.client = client;
        }

        @Override
        public void onOpen(WebSocket webSocket) {
            System.out.println("WebSocket opened");
            Listener.super.onOpen(webSocket);
        }

        @Override
        public CompletionStage<?> onText(WebSocket webSocket, CharSequence data, boolean last) {
            client.onMessage(data.toString());
            return Listener.super.onText(webSocket, data, last);
        }

        @Override
        public void onError(WebSocket webSocket, Throwable error) {
            error.printStackTrace();
        }

        @Override
        public CompletionStage<?> onClose(WebSocket webSocket, int statusCode, String reason) {
            System.out.println("WebSocket closed with status " + statusCode + " and reason " + reason);
            return Listener.super.onClose(webSocket, statusCode, reason);
        }
    }
}

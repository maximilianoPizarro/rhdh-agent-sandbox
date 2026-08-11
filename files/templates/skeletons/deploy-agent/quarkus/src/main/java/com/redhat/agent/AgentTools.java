package com.redhat.agent;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import dev.langchain4j.agent.tool.Tool;
import jakarta.enterprise.context.ApplicationScoped;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;

@ApplicationScoped
public class AgentTools {

    private static final ObjectMapper MAPPER = new ObjectMapper();
    private final HttpClient http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build();

    private String namespace() throws Exception {
        String env = System.getenv("NAMESPACE");
        if (env != null && !env.isBlank()) {
            return env;
        }
        return Files.readString(Path.of("/var/run/secrets/kubernetes.io/serviceaccount/namespace")).trim();
    }

    private String token() throws Exception {
        return Files.readString(Path.of("/var/run/secrets/kubernetes.io/serviceaccount/token")).trim();
    }

    @Tool("List pods in the current OpenShift namespace")
    public String listPods() {
        try {
            String ns = namespace();
            HttpRequest req = HttpRequest.newBuilder()
                    .uri(URI.create("https://kubernetes.default.svc/api/v1/namespaces/" + ns + "/pods"))
                    .header("Authorization", "Bearer " + token())
                    .header("Accept", "application/json")
                    .GET()
                    .build();
            HttpResponse<String> resp = http.send(req, HttpResponse.BodyHandlers.ofString());
            return resp.body();
        } catch (Exception e) {
            return "{\"error\":\"" + e.getMessage() + "\"}";
        }
    }

    @Tool("Look up a CVE using the public Red Hat Security Data API")
    public String lookupCve(String cveId) {
        try {
            String id = cveId.trim().toUpperCase();
            HttpRequest req = HttpRequest.newBuilder()
                    .uri(URI.create("https://access.redhat.com/hydra/rest/securitydata/cve/" + id + ".json"))
                    .GET()
                    .build();
            HttpResponse<String> resp = http.send(req, HttpResponse.BodyHandlers.ofString());
            if (resp.statusCode() == 404) {
                return "{\"error\":\"CVE not found\",\"cve_id\":\"" + id + "\"}";
            }
            JsonNode data = MAPPER.readTree(resp.body());
            ObjectNode out = MAPPER.createObjectNode();
            out.put("cve_id", id);
            out.put("threat_severity", data.path("threat_severity_rating").asText(data.path("severity").asText("")));
            out.put("statement", data.path("statement").asText("").substring(0, Math.min(500, data.path("statement").asText("").length())));
            return MAPPER.writeValueAsString(out);
        } catch (Exception e) {
            return "{\"error\":\"" + e.getMessage() + "\"}";
        }
    }

    @Tool("Check Red Hat product lifecycle status")
    public String checkLifecycle(String product, String version) {
        try {
            HttpRequest req = HttpRequest.newBuilder()
                    .uri(URI.create("https://access.redhat.com/product-life-cycles/api/v1/products"))
                    .GET()
                    .build();
            HttpResponse<String> resp = http.send(req, HttpResponse.BodyHandlers.ofString());
            JsonNode root = MAPPER.readTree(resp.body());
            JsonNode products = root.has("data") ? root.get("data") : root;
            String needle = product.toLowerCase();
            if (products.isArray()) {
                for (JsonNode p : products) {
                    String name = p.path("name").asText(p.path("product_name").asText(""));
                    if (name.toLowerCase().contains(needle)) {
                        ObjectNode out = MAPPER.createObjectNode();
                        out.put("product", name);
                        out.put("version_filter", version == null ? "" : version);
                        return MAPPER.writeValueAsString(out);
                    }
                }
            }
            return "{\"error\":\"product not found\",\"product\":\"" + product + "\"}";
        } catch (Exception e) {
            return "{\"error\":\"" + e.getMessage() + "\"}";
        }
    }
}

package com.redhat.agent;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import java.util.Map;
import java.util.UUID;
import org.eclipse.microprofile.config.inject.ConfigProperty;

@Path("/")
@Produces(MediaType.APPLICATION_JSON)
public class AgentResource {

    @Inject
    AgentService agent;

    @ConfigProperty(name = "agent.name")
    String name;

    @ConfigProperty(name = "agent.framework")
    String framework;

    @ConfigProperty(name = "agent.language")
    String language;

    @ConfigProperty(name = "agent.type")
    String agentType;

    @ConfigProperty(name = "agent.spec")
    String agentSpec;

    @ConfigProperty(name = "quarkus.langchain4j.openai.chat-model.model-name")
    String model;

    @GET
    @Path("/health")
    public Map<String, Object> health() {
        return Map.of("status", "ok", "framework", framework, "language", language);
    }

    @GET
    @Path("/healthz")
    public Map<String, Object> healthz() {
        return health();
    }

    @jakarta.ws.rs.OPTIONS
    @Path("{path:.*}")
    public Response options() {
        return Response.ok().build();
    }

    @GET
    public Map<String, Object> root() {
        return Map.of(
                "service", name,
                "framework", framework,
                "language", language,
                "model", model,
                "agentType", agentType,
                "agentSpec", agentSpec);
    }

    @GET
    @Path("/v1/runtime")
    public Map<String, Object> runtime() {
        return Map.of(
                "runtime", "quarkus",
                "version", System.getProperty("java.version", "unknown"),
                "framework", framework);
    }

    public static class ChatRequest {
        public String message;
        public String prompt;
    }

    @POST
    @Path("/v1/chat")
    public Response chat(ChatRequest body) {
        String rid = UUID.randomUUID().toString().substring(0, 12);
        String user = body == null ? "" : (body.message != null ? body.message : (body.prompt != null ? body.prompt : ""));
        try {
            String prompt = "Agent name: " + name + ". Type: " + agentType + ". Spec: " + agentSpec + "\n\nUser: " + user;
            String reply = agent.chat(prompt);
            return Response.ok(Map.of(
                            "reply", reply,
                            "model", model,
                            "framework", framework,
                            "requestId", rid))
                    .header("X-Request-Id", rid)
                    .build();
        } catch (Exception e) {
            return Response.status(502)
                    .entity(Map.of("error", e.getMessage() == null ? "chat failed" : e.getMessage(), "requestId", rid))
                    .header("X-Request-Id", rid)
                    .build();
        }
    }
}

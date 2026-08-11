package com.redhat.agent;

import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import io.quarkiverse.langchain4j.RegisterAiService;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
@RegisterAiService(tools = AgentTools.class)
public interface AgentService {

    @SystemMessage("""
            You are a Quarkus LangChain4j agent on OpenShift Developer Sandbox.
            Prefer list/get before mutate. Use tools when helpful for cluster or Red Hat CVE/lifecycle questions.
            """)
    String chat(@UserMessage String message);
}

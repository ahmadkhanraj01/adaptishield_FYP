Undergraduate Research

![A logo of a university of engineering and technology

**Supervisor:
**Dr Laeeq Ahmed

**Student Names:
**Muhammad Ahmad Khan
Aleena Khan

**Registration Number:
**23JZBCS0238
23JZBCS0229

Department of CS&IT
University of Engineering and Technology Peshawar
(Jalozai Campus)

5 March 2026

Research Proposal

Title

Adaptive Threat Modeling for Tool-Orchestrated Large Language Model (LLM) Systems in Model Context Protocol (MCP) Architectures

1. Introduction

Tool-orchestrated Large Language Model (LLM) systems, particularly those built on the Model Context Protocol (MCP), are rapidly transforming modern AI applications. These systems enable LLMs to interact with external APIs, databases, and autonomous tools, significantly expanding their functional capabilities. However, this architectural advancement introduces a substantially enlarged attack surface across the client, protocol, server, and toolchain layers.

Existing security approaches for MCP-based systems primarily rely on static threat models and rule-based defenses. These models assume predefined adversarial behaviors and attempt to mitigate risks using fixed detection heuristics. However, recent research demonstrates that adversaries continuously evolve their strategies through multi-turn prompt injection, toolchain manipulation, context takeover, backend exploitation, and supply chain attacks.

As a result, static threat modeling frameworks are increasingly inadequate for securing dynamic, tool-orchestrated AI systems operating in real-world environments.

2. Motivation

AI agents are increasingly deployed in high-stakes domains such as finance, healthcare, cybersecurity, and autonomous decision systems. In such environments, failures caused by adversarial exploitation can lead to severe financial, operational, and ethical consequences.

The current research landscape highlights several major shortcomings:

Threat models are often simplistic and isolated.
Many defenses prematurely terminate workflows rather than enabling safe continuation.
Red teaming remains largely manual and unrealistic.
Backend and supply chain vulnerabilities remain underexplored.

These limitations suggest a critical need for adaptive, learning-based threat modeling mechanisms that can:

Continuously evolve alongside adversarial behavior.
Detect and mitigate context takeovers in multi-turn workflows.
Maintain task continuity while preserving security.

This proposal aims to address these gaps by developing an adaptive threat modeling framework specifically designed for MCP-based LLM systems.

3. Research Problem

Static threat modeling approaches are insufficient for defending tool-orchestrated LLM systems against evolving, multi-turn, and toolchain-based adversarial attacks.

There is currently no unified adaptive framework that:

Continuously learns from evolving attack patterns,
Monitors causal deviations in agent workflows,
Balances security enforcement with safe task continuation.

4. Research Questions

Can adaptive adversarial training improve the robustness of MCP-based LLM agents against evolving toolchain-based attacks?
How does adaptive threat modeling compare with static threat modeling in terms of:
Attack Success Rate (ASR),
False Positive Rate (FPR),
Workflow Continuation Rate (WCR),
Long-term robustness under dynamic adversarial conditions?

5. Proposed Methodology

This research adopts a comparative experimental framework consisting of a baseline static model and a proposed adaptive threat modeling system.

5.1 System Architecture

A controlled MCP-style tool-orchestrated LLM environment will be implemented, consisting of:

LLM Orchestrator (reasoning and tool selection)
Tool Execution Layer (APIs, file tools, web services)
Context Memory Module (multi-turn state tracking)
Policy Enforcement Layer
Sandboxed Execution Environment

This modular setup enables systematic security evaluation across multiple attack surfaces.

5.2 Baseline Static Threat Model

The baseline system will implement:

STRIDE-inspired threat categorization
Rule-based prompt filtering
Fixed tool access controls
Deterministic refusal policies

This model will not update during runtime and will serve as the control condition.

5.3 Adaptive Threat Modeling Framework (Proposed System)

The adaptive system integrates three major components:

A. Multi-Agent Autonomous Red Teaming

A collaborative multi-agent framework will continuously generate evolving adversarial scenarios:

Attack Generator Agent
Execution Agent
Evaluator Agent
Optimizer Agent

This allows automated discovery of new toolchain-based attack strategies.

B. Temporal Causal Diagnostics

To avoid premature workflow termination, causal monitoring will be performed at:

Tool-return boundaries
Context update events
Action selection checkpoints

Counterfactual dry-run re-execution will determine whether agent behavior is driven by legitimate user goals or malicious context takeover.

If deviation is detected:

Malicious context segments are selectively removed.
Task-relevant state is preserved.
Workflow safely continues under constraints.

C. Adaptive Defense Learning

Defense policies will be updated using reinforcement learning with verifiable reward signals:

Reward function components:

Penalty for successful attacks
Penalty for high false positives
Reward for secure task completion
Reward for accurate detection

Policy optimization methods may include:

Reinforcement Learning with Verifiable Reward (RLVR)
Group Relative Policy Optimization (GRPO)

This ensures dynamic adaptation to evolving threats.

6. Experimental Evaluation

6.1 Attack Scenarios

Evaluation will include:

Known prompt injection attacks
Novel unseen injection patterns
Multi-turn gradual context takeover
Malicious toolchain exploitation
Backend log manipulation scenarios

6.2 Evaluation Metrics

Attack Success Rate (ASR)
False Positive Rate (FPR)
Workflow Continuation Rate (WCR)
Task Completion Accuracy
Defense Adaptation Speed

Statistical comparison between static and adaptive models will be performed.

7. Expected Contributions

This research is expected to contribute:

A formal adaptive threat modeling framework for MCP-based LLM systems.
Integration of temporal causal diagnostics with adaptive learning.
An automated multi-agent red teaming pipeline.
A comparative benchmark for static vs adaptive threat modeling.
Empirical evidence on balancing robustness and workflow continuity.

8. Expected Impact

The proposed framework aims to improve long-term robustness, reliability, and trustworthiness of tool-orchestrated LLM systems in real-world deployments. It contributes to advancing secure AI system design in data-intensive and agentic AI environments.

11 March 2026

Task 2 - Understanding the Core Theory

1. Adaptive Threat Modeling

Adaptive Threat Modeling is a security approach that dynamically updates defense

strategies based on evolving attack patterns and system behavior. Traditional threat

modeling techniques rely on static rules and predefined attack scenarios, which are

often insufficient for modern AI systems that operate in dynamic environments.

In tool-orchestrated Large Language Model (LLM) systems, the attack surface becomes

significantly larger because the LLM interacts with external tools such as APIs,

databases, and file systems. Attackers can exploit these interactions through

techniques such as prompt injection, malicious tool manipulation, and context

hijacking.

In this research, adaptive threat modeling is proposed as a dynamic security

mechanism for MCP-based AI systems. The framework continuously observes agent

behavior, identifies abnormal patterns, and updates defense policies accordingly.

Instead of relying on fixed rules, the system learns from new attack attempts and

adapts its protection strategies.

The proposed research integrates adaptive threat modeling with automated adversarial

testing and reinforcement learning to improve the long-term robustness of tool

orchestrated LLM systems while maintaining secure task execution.

2. Agentic AI / Tool-Orchestrated LLM

Agentic AI refers to artificial intelligence systems that are capable of autonomous

reasoning, planning, and action execution in order to accomplish complex tasks. Unlike

traditional AI systems that only generate responses, agentic AI systems can interact

with external tools and services to perform real operations.

A Tool-Orchestrated LLM system is a type of agentic AI where the Large Language Model

acts as the central decision-making component. The LLM analyzes user queries,

determines the necessary steps to complete a task, and selects appropriate tools for

execution.

For example, when a user submits a request, the LLM may perform the following

actions:

1. Interpret the user query

2. Plan a sequence of actions

3. Select external tools such as APIs or databases

4. Execute the tools

5. Process the results and generate the final response

Modern AI systems such as ChatGPT and Microsoft Copilot demonstrate how LLMs can

orchestrate multiple tools to perform complex tasks.

In the context of this research, the focus is on securing such agentic AI systems

because their interaction with external tools creates potential security vulnerabilities.

These vulnerabilities may allow attackers to manipulate the AI agent into executing

malicious operations. Therefore, an adaptive threat modeling framework is required to

monitor agent behavior and prevent adversarial exploitation.

3. Model Context Protocol (MCP)

The Model Context Protocol (MCP) is an architectural framework that enables

structured communication between Large Language Models and external tools,

services, and data sources. It defines how contextual information, tool requests, and

system responses are exchanged within an AI agent environment.

In MCP-based architectures, the system typically includes several interconnected

components.

The Client Layer provides the interface where users interact with the AI system.

The LLM Orchestrator processes the user's request, performs reasoning, and decides

which tools should be used.

The Tool Execution Layer contains external tools such as APIs, databases, and web

services that perform specific tasks.

The Context Memory Module stores conversation history and task-related information

to support multi-step interactions.

The Policy and Security Layer enforces security rules and access control

mechanisms.

While MCP architectures significantly enhance the capabilities of AI systems, they also

introduce new security risks. Attackers may attempt to manipulate context information,

inject malicious prompts, or exploit tool interactions to compromise the system.

This research focuses on securing MCP-based LLM systems by integrating adaptive

threat modeling techniques that continuously monitor system behavior and detect

adversarial activities. By combining adaptive learning with automated red-teaming

strategies, the proposed framework aims to improve the robustness and

trustworthiness of agentic AI systems.

18 March 2026

1.2 Methodology

The authors adopt a systematic and evidence-driven methodology consisting of:

A large-scale literature review of over 150 research papers and technical reports
Identification and classification of more than 30 attack techniques
Development of a unified taxonomy of threats across four major categories:
Input Manipulation Attacks
Model Compromise Attacks
System and Privacy Attacks
Protocol-Level Vulnerabilities

Additionally, the paper introduces formal threat models that define attacker capabilities, objectives, and system boundaries, enabling structured analysis of security risks.

1.3 Future Work

The paper outlines several key directions for future research:

Development of dynamic and adaptive security mechanisms
Implementation of continuous verification and trust management systems
Strengthening protocol-level security, particularly in MCP-based architectures
Improving resilience in multi-agent and distributed AI systems

2. Methodology Paper 1

Title:

"Measuring the Security of Mobile LLM Agents under Adversarial Prompts from Untrusted Third-Party Channels"

2.1 Research Gap

This paper identifies a significant gap in the evaluation of LLM-based agents, particularly in mobile environments. Existing research primarily focuses on task performance and usability, while overlooking security and privacy risks.

Moreover, prior studies rely on simplified or unrealistic threat models that do not accurately reflect real-world adversarial conditions, especially those involving third-party content such as advertisements, notifications, and embedded web views.

Identified Gap:
There is a lack of systematic, real-world evaluation frameworks to assess the security and robustness of mobile LLM agents under adversarial conditions.

2.2 Methodology

The authors propose a comprehensive experimental framework to evaluate security risks in mobile LLM agents:

Evaluation of 8 state-of-the-art mobile agents
Testing across 8 diverse attack vectors, including:
Ad-based prompt injection
Phishing attacks
Credential and OTP harvesting
Cross-application data exfiltration
Malware installation
Execution of over 2000 adversarial and benign trials
Comparative analysis between benign task execution and adversarial manipulation
Mapping of identified attack vectors to the MITRE ATT&CK Mobile framework

This methodology enables realistic, end-to-end assessment of agent vulnerabilities in dynamic environments.

2.3 Future Work

The paper suggests several improvements for future research:

Development of robust runtime defense mechanisms
Enhanced validation of contextual inputs
Secure handling of multi-step and multi-application workflows
Improved isolation between system components to prevent cross-app exploitation

3. Methodology Paper 2

Title:

"Adam: A Method for Stochastic Optimization"

3.1 Research Gap

Traditional optimization techniques, such as standard stochastic gradient descent, face limitations when applied to large-scale and noisy machine learning problems. These methods often require extensive manual tuning and struggle with sparse or non-stationary data.

Identified Gap:
There is a need for adaptive optimization algorithms that can automatically adjust learning parameters and efficiently handle large, noisy, and high-dimensional datasets.

3.2 Methodology

The paper introduces Adam (Adaptive Moment Estimation), an optimization algorithm designed for efficient training of machine learning models.

Key features of the methodology include:

Computation of adaptive learning rates using:
First moment estimates (mean of gradients)
Second moment estimates (variance of gradients)
Use of bias-corrected moment estimates for improved convergence
Combination of advantages from existing methods such as AdaGrad and RMSProp

The algorithm dynamically adjusts parameter updates, enabling efficient optimization across a wide range of machine learning tasks.

3.3 Future Work

Future directions highlighted in the paper include:

Further theoretical analysis of convergence properties
Optimization for more complex and large-scale learning environments
Extension of adaptive optimization techniques to broader applications

4. Integrated Analysis and Relevance to Proposed Research

The three selected papers collectively provide a strong foundation for understanding the security challenges in LLM-based systems and identifying opportunities for improvement.

The survey paper establishes a comprehensive understanding of the threat landscape and highlights the lack of unified security frameworks.
The mobile agent study provides empirical evidence of real-world vulnerabilities, demonstrating the limitations of current systems.
The Adam optimization paper introduces adaptive learning techniques that can be leveraged to design dynamic defense mechanisms.

Final Research Gap (Derived)

Based on the analysis of these papers, the following research gap is identified:

Existing security approaches for LLM-based agent systems rely on static and fragmented defenses, lacking adaptive, real-time mechanisms capable of responding to evolving, multi-turn, and toolchain-based adversarial attacks.

Conclusion

This review demonstrates that while significant progress has been made in understanding and evaluating security risks in LLM-powered systems, current approaches remain insufficient for real-world deployment. The lack of adaptive threat modeling and dynamic defense strategies presents a critical challenge.

Addressing this gap requires the development of intelligent, learning-based security frameworks capable of continuously evolving alongside adversarial techniques. This forms the foundation for the proposed research on adaptive threat modeling in tool-orchestrated LLM systems. 27 March 2026

III. PROPOSED SYSTEM ARCHITECTURE

A. Overview

This work proposes a secure and adaptive system architecture for LLM-powered agent systems operating under the Model Context Protocol (MCP). The architecture is designed to address critical security challenges such as prompt injection, tool poisoning, and multi-turn context manipulation, while maintaining task continuity.

The system adopts a layered design paradigm, separating interaction, reasoning, execution, and security mechanisms. A key contribution of this architecture is the integration of an adaptive security layer within the control plane, enabling real-time threat detection and continuous policy improvement through feedback-driven learning.

B. Architectural Layers

The proposed system consists of five primary layers, each responsible for a distinct functional role.

1) Interaction and Data Plane

The Interaction and Data Plane is responsible for processing incoming inputs and maintaining contextual state across interactions.

It comprises an Input Parser, which converts raw user prompts and external data into structured representations, and a Context Builder, which integrates current inputs with historical interactions to construct a coherent multi-turn context. A Memory Store maintains this context for downstream reasoning.

This layer is particularly vulnerable to input manipulation attacks, including direct prompt injection and malicious data retrieved from external sources.

2) LLM Agent Control Plane

The Control Plane serves as the core decision-making component of the system. It includes a Planner Agent, which decomposes user requests into actionable steps, and a Tool Selector, which determines the appropriate external tools required for task execution.

An Execution Agent carries out these actions, while a Feedback Analyzer evaluates the outputs of tool interactions for anomalies or inconsistencies.

3) Security and Adaptive Layer

Embedded within the Control Plane, the Security and Adaptive Layer represents the primary contribution of this work. It provides both preventive and adaptive defense mechanisms through the following components:

A Policy Engine, which enforces predefined static security rules to filter malicious inputs and restrict unsafe actions.
A Causal Analyzer, which performs temporal diagnostics to determine whether system behavior is influenced by adversarial context.
A Threat Model, which leverages reinforcement learning to adaptively update defense strategies based on observed attack patterns.
A Context Sanitizer, which removes or neutralizes malicious context while preserving relevant task information.

This layer enables the system to transition from static defenses to a closed-loop adaptive security framework.

4) Tool and Execution Plane

The Tool and Execution Plane facilitates interaction with external systems, including APIs, databases, and file systems. While essential for enabling real-world functionality, this layer introduces significant security risks, such as tool poisoning and malicious API responses.

To mitigate these risks, all tool interactions are routed through an isolation layer.

5) Sandbox and Isolation Layer

The Sandbox and Isolation Layer ensures that all tool executions occur within a controlled and secure environment. It includes:

A gVisor-based sandbox, which provides process-level isolation from the host system.
A Permission Control module, which enforces fine-grained access restrictions on system resources.
A Telemetry Stream, which captures execution traces and behavioral logs for monitoring and analysis.

This layer acts as the final line of defense, ensuring that even if upstream protections fail, system integrity is preserved.

6) Human-in-the-Loop and Observability Layer

The topmost layer provides system transparency and governance through a dashboard interface, audit logs, and manual override capabilities. This enables human operators to monitor system behavior and intervene in high-risk scenarios.

C. Supporting Modules

1) Red Team Module

The Red Team Module introduces an Attack Generator that simulates adversarial inputs, including prompt injections and tool misuse scenarios. This module is used to evaluate system robustness and to provide training data for adaptive learning.

2) Evaluation Module

System performance is evaluated using the following metrics:

Attack Success Rate (ASR): Measures the proportion of successful attacks.
False Positive Rate (FPR): Measures the rate at which legitimate actions are incorrectly flagged.
Workflow Continuation Rate (WCR): Measures the system's ability to maintain task execution despite adversarial conditions.

D. System Workflow

The system operates in a sequential yet adaptive manner:

User input is processed by the Input Parser and Context Builder.
The Planner Agent generates an execution strategy.
The Security Layer evaluates the plan using policy enforcement and causal analysis.
Approved actions are executed through the Tool Layer within a sandboxed environment.
Execution data is monitored via telemetry and analyzed by the Feedback Analyzer.
The Threat Model updates system policies based on observed outcomes.
Results are presented to the user, with optional human oversight.

E. Threat Model Coverage

The proposed architecture addresses multiple categories of threats identified in recent literature, including:

Input Manipulation Attacks: Direct and indirect prompt injection.
Model Compromise Attacks: Context poisoning and memory manipulation.
System and Privacy Attacks: Data leakage and unauthorized access.
Protocol-Level Attacks: Exploitation of MCP-based tool interactions.

F. Key Contributions

The proposed architecture introduces the following key innovations:

Integration of an adaptive security layer within the control plane.
Implementation of a closed-loop feedback mechanism for continuous learning.
Use of causal diagnostics to detect adversarial influence.
Incorporation of autonomous red teaming for proactive defense.
Deployment of a multi-layered defense-in-depth strategy.

G. Summary

The proposed system architecture provides a robust, adaptive, and scalable framework for securing MCP-based LLM systems. By combining layered defenses with real-time learning and human oversight, the system effectively mitigates a wide range of adversarial threats while maintaining operational efficiency.

2 May 2026

IV. AdaptiShield Architecture

AdaptiShield comprises seven layers numbered 0 through 6. Each layer is defined by its input, its output, the failure modes it handles, and its relationship to adjacent layers. Figure 1 presents the complete architecture. Layers are traversed sequentially for normal execution; feedback arrows implement the adaptive learning loops described in Section VI.

Layer 0 - MCP Transport and Server Trust [NEW]

Purpose: Layer 0 is entirely absent from prior MCP-aware architectures. It addresses the protocol and supply-chain attack surfaces before any user input or tool output reaches the agent. MCPSecBench [6] demonstrates that protocol-level attacks achieve 100% ASR against all evaluated platforms with no existing countermeasure. Layer 0 is the architectural response to this finding.

Components:

Transport Integrity Verifier [NEW] enforces TLS on all HTTP-based MCP transport connections. It verifies that every received MCP message originates from an authenticated peer and that payload content has not been modified in transit. This component directly addresses MitM attacks (ATT-6) and DNS rebinding (ATT-5), which exploit the absence of authentication and integrity verification in current MCP transport implementations.

Server Trust Registry [NEW] maintains a signed registry of approved MCP servers following the ETDI framework [11]. Every MCP server registration requires a cryptographic signature binding the server identity to its declared tool capabilities and version. Before any tool list is accepted from a server, the Registry verifies current server identity against the registered signature. Version mismatches are flagged as potential rug-pull attacks (ATT-13) and quarantined for review.

Schema Validator [NEW] compares incoming MCP tool definitions against the expected schema for the current protocol version. Schema inconsistencies (ATT-3), which cause denial of service through strict MCP parsing requirements, are rejected at this layer before reaching the LLM.

Name Squatting Guard [NEW] computes lexical and semantic similarity scores between newly registered server and tool names and the existing registry. Names above a similarity threshold to existing legitimate entries are flagged for human review before registration proceeds, addressing package name squatting (ATT-9, ATT-11).

Output to Layer 1: Validated, authenticated, schema-conformant tool definitions and transport-verified message payloads.

Layer 1 - Input and Supply Chain Screening [EXPANDED]

Purpose: Layer 1 replaces the original Interaction and Data Plane. It retains the Input Parser, Context Builder, and Memory Store from the original architecture but adds provenance tagging throughout and introduces a Supply Chain Scanner absent from the original design.

Components:

Input Parser [EXPANDED - NEW: Provenance Tagging] converts raw user prompts into structured representations. Critically, it attaches a provenance label to every input segment indicating its origin: user-originated, tool-returned, memory-retrieved, or system-generated. These labels persist with the content as it moves through the pipeline and are essential for the Causal Analyzer in Layer 2, which must distinguish trusted context from untrusted mediator content to compute causal effect estimates. The original Input Parser performed no provenance labeling.

Supply Chain Scanner [NEW] statically analyzes MCP tool metadata - name, description, and input schema - for tool poisoning indicators before any tool is registered for use by the agent. It implements an LLM-based detection oracle similar to AutoMalTool's Oracle component [7], examining tool descriptions for imperative language, priority overrides, hidden instructions, and tool-capability directives. Tools that fail the scan are quarantined and flagged for human review via Layer 6. This component addresses the supply-chain attack surface at registration time, before any tool is invoked.

Context Builder [EXPANDED - NEW: Trusted vs Mediator Split] assembles the multi-turn agent context from user inputs, memory, and tool outputs. In the original architecture the Context Builder produced a flat concatenated context. The expanded version explicitly partitions content into a trusted prefix comprising user goals and prior agent outputs, and an untrusted mediator view comprising tool returns and retrieved content. This partition structure is required by the Causal Analyzer and was absent from the original design.

Provenance Memory Store [NEW] replaces the original unlabeled Memory Store. Every context segment stored in memory carries its provenance label, ensuring that the trusted versus mediator distinction is preserved across conversation turns. Without persistent provenance labels, the Causal Analyzer's ability to compute the indirect effect of mediator content degrades as conversation length increases.

Output to Layer 2: Provenance-partitioned, supply-chain-screened context ready for agent reasoning.

Layer 2 - LLM Agent Control Plane [EXPANDED]

Purpose: Layer 2 contains the agent's core reasoning and execution components, and houses the Security and Adaptive Sub-layer which constitutes the primary contribution of this work. The control plane's top row is preserved from the original architecture with targeted additions.

Components:

Planner Agent decomposes the user's natural language request into a sequence of actionable sub-tasks. Unchanged from the original architecture.

Tool Selector [EXPANDED - NEW: Registry Auth Check] determines which registered tool to invoke for each planned sub-task. The original Tool Selector selected tools based solely on semantic matching to tool descriptions. The expanded version performs a Registry Authorization Check before every invocation, querying the Server Trust Registry in Layer 0 to verify that the selected tool's current version and capability declaration match the registered signature. This check catches rug-pull attacks (ATT-13) that succeed after initial registration by silently modifying the tool implementation.

Execution Agent carries out the approved tool invocations produced by the Tool Selector. Unchanged from the original architecture.

Feedback Analyzer [EXPANDED - NEW: Structured Episode Records] evaluates tool outputs and agent behavior for anomalies. In the original architecture the Feedback Analyzer was a standalone component floating outside the layer structure, connected by long arrows with no defined output format. In AdaptiShield it is positioned within the control plane and produces a structured Episode Record for every tool-return boundary. Each Episode Record contains: the boundary context at the time of evaluation, the proposed next action, the Causal Analyzer's takeover verdict, the Context Sanitizer's purification decision if triggered, and the realized outcome severity score. These Episode Records are the input format consumed by the Adaptive Threat Model.

Security and Adaptive Sub-layer is specified in full in Section V.

Output to Layer 3: Approved tool invocation requests with purified context where applicable.

Layer 3 - MCP Tool Execution Plane [EXPANDED]

Purpose: Layer 3 interfaces with external APIs, databases, and file systems. The original architecture routed tool responses directly back into the agent context with no intermediate screening, creating an undefended channel for IPI delivered via tool returns. Layer 3 adds a Tool Response Screener to close this gap.

Components:

APIs, Databases, File Systems provide external capabilities to the agent. Unchanged from the original architecture.

Tool Response Screener [NEW] intercepts tool responses before they are incorporated into the agent context. It runs each response through the same detection logic as the Supply Chain Scanner in Layer 1, checking for IPI payloads embedded in tool return values. This addresses the most empirically successful attack delivery channel: AgentSentry [8] demonstrates that IPI embedded in tool responses (Important Instructions, Tool Knowledge, and InjecAgent attack families) achieves the highest attack success rates against undefended agents. Responses flagged by the screener are not blocked outright; instead, they are tagged and routed to the Causal Analyzer in Layer 2 for boundary-level evaluation, preserving workflow continuity.

Output to Layer 4: Tool responses tagged with a risk indicator for the Telemetry Stream, and flagged responses directed to the Causal Analyzer.

Layer 4 - Sandbox and Isolation [EXPANDED]

Purpose: Layer 4 provides process-level isolation and execution monitoring. The original architecture contained gVisor sandboxing, permission control, and a telemetry stream. AdaptiShield adds a Network Egress Filter and expands the Telemetry Stream to emit structured Episode Records.

Components:

gVisor Sandbox provides kernel-level process isolation for tool executions. Unchanged from the original architecture.

Permission Control [EXPANDED - NEW: MCP Scope Enforcement] enforces fine-grained access controls on tool executions. The original Permission Control applied generic access policies. The expanded version enforces MCP-specific scope constraints: each MCP server connection is granted only the permissions declared in its registered capability scope, and attempts to access resources outside the declared scope are blocked and logged as high-severity events.

Network Egress Filter [NEW] monitors all outbound network connections initiated by tool executions. It enforces an allowlist of permitted destination addresses derived from the Server Trust Registry in Layer 0. Connections to destinations not present in the registry are blocked and logged as potential exfiltration attempts. This component is critical because gVisor process isolation does not prevent an agent that has been successfully compromised via context takeover from sending data to attacker-controlled destinations through approved communication tools such as email clients or HTTP APIs. The Network Egress Filter closes this exfiltration pathway.

Telemetry Stream [EXPANDED - NEW: Episode Record Emission] captures execution traces and behavioral logs. The original Telemetry Stream produced unstructured logs with no defined destination format. The expanded version packages captured data as structured Episode Records matching the schema consumed by the Adaptive Threat Model. This format alignment is what enables the reactive closed-loop feedback path described in Section VI.

Output: Structured Episode Records to the Adaptive Threat Model via the reactive feedback loop. Execution results back to the Control Plane.

Layer 5 - Human-in-the-Loop and Observability [EXPANDED]

Purpose: Layer 5 provides human governance over the adaptive system. The original architecture contained a Dashboard, Manual Override, and Audit Logs. AdaptiShield adds a Policy Inspection Console to address the absence of human oversight over RL-driven policy updates.

Components:

Audit Dashboard [EXPANDED] visualizes system behavior. The original Dashboard displayed general activity logs. The expanded version shows boundary-indexed causal effect trajectories from the Causal Analyzer, takeover detection events with their localized boundary indices, and policy update history from the Adaptive Threat Model. This interpretable visualization is possible because the Causal Analyzer now produces quantified per-boundary estimates rather than binary alerts.

Manual Override allows operators to approve or reject high-impact tool invocations escalated by the Policy Engine. Unchanged from the original architecture.

Policy Inspection Console [NEW] provides operators with visibility into and control over the Adaptive Threat Model's current policy rule set. Because the RL policy optimizer automatically updates Policy Engine rules and Causal Analyzer thresholds based on observed episode outcomes, human governance is necessary to prevent policy drift in response to miscalibrated reward signals. The console connects back to the Policy Engine in the Security and Adaptive Sub-layer via a governed policy update channel, allowing operators to review, approve, or manually edit rule changes before they take effect.

Audit Logs maintain an immutable record of all system events, policy updates, detection decisions, and override actions. Unchanged from the original architecture.

Red Team Module - Autonomous Adversarial Generation [PROMOTED AND EXPANDED]

Purpose: The original architecture contained a single Attack Generator component labeled as a supporting module with one connection to the Input Parser. It had no defined output format and no connection to the adaptive learning pipeline. AdaptiShield promotes the Red Team Module to a full architectural component with four internal agents, a defined episode output format, and two connections: one to the Input Parser simulating real adversarial input injection, and one to the Adaptive Threat Model delivering proactive training episodes.

Components:

Attack Generator [EXPANDED] produces adversarial MCP tool descriptions and prompt injection payloads targeting the specific tool set registered in the Server Trust Registry. Attacks are generated based on the current system's registered tool metadata, ensuring that generated attacks are realistic and relevant rather than generic. This component corresponds to the Initial Generator in AutoMalTool [7].

Execution Agent [NEW] deploys generated attacks against a shadow copy of the system in dry-run mode, recording proposed tool calls without committing external effects. This prevents red team evaluation from causing real-world side effects.

Evaluator Agent [NEW] scores each attack attempt against the three evaluation metrics - ASR, FPR, and WCR - using the same measurement protocol as the main evaluation framework. Attack attempts that successfully evade current defenses are identified as high-priority training candidates.

Optimizer Agent [NEW] receives the Evaluator Agent's scores and refines attack strategies to generate progressively more challenging adversarial examples, following the optimization loop described in AutoMalTool [7].

Connection 1 - Red Team → Input Parser (Attack Injection Path): Generated attacks are injected into Layer 1's Input Parser simulating how a real adversary would deliver malicious content through legitimate input channels such as ads, notifications, emails, or crafted tool descriptions. This connection was present in the original architecture and is preserved. It enables measurement of ASR, FPR, and WCR by routing attacks through the full defense pipeline.

Connection 2 - Red Team → Adaptive Threat Model (Training Path) [NEW]: Attacks scored as successful by the Evaluator Agent are packaged as structured Episode Records and delivered directly to the Adaptive Threat Model's training buffer. This is the proactive feedback loop: the system learns from adversarial examples generated before real attackers arrive, rather than only updating after successful real attacks are observed in production. This connection was entirely absent from the original architecture, preventing any proactive learning.

V. Security and Adaptive Sub-layer Specification

The Security and Adaptive Sub-layer resides within Layer 2 and constitutes the primary technical contribution of AdaptiShield. It comprises four sequentially ordered components. This section provides a complete specification of each component and its internal interfaces.

A. 3A - Policy Engine

The Policy Engine is the first filter applied to every proposed agent action. It implements a static rule set based on the STRIDE threat modeling framework, partitions available tools into a low-impact diagnostic set and a high-impact exfiltration-capable set, and enforces authorization requirements for high-impact tool invocations. The Policy Engine serves as the baseline defense and as the target of RL-driven rule updates from Component 3D.

In the original architecture the Policy Engine was labeled but its relationship to the other three components was not specified. In AdaptiShield it is the entry point of the sequential pipeline: every proposed action passes through the Policy Engine before reaching the Causal Analyzer.

B. 3B - Causal Analyzer [NEW: Fully Specified]

The Causal Analyzer fires at every tool-return boundary, defined as the moment immediately after a tool response has been incorporated into the agent context and immediately before the next action is emitted. At each boundary it performs four controlled dry-run re-executions using cached tool responses, following the counterfactual diagnostic protocol of AgentSentry [8].

The four counterfactual regimes are:

Original regime uses the actual user input and the actual tool-returned mediator content.

Masked regime replaces the user input with a task-neutral diagnostic probe that asks the model to summarize available mediator content and propose a next step without restating the user goal, while keeping the mediator content unchanged. This isolates the causal contribution of the mediator channel.

Sanitized regime uses the masked probe and replaces the mediator content with a sanitized version from which instruction-carrying spans have been removed while factual content is preserved.

Original-Sanitized regime uses the actual user input paired with the sanitized mediator content.

From the four regime outcomes the Causal Analyzer computes three causal quantities: the Average Causal Effect (ACE) of the user channel, the Indirect Effect (IE) of the mediator channel, and the Direct Effect (DE). When the Indirect Effect is statistically significant and the risk score computed from windowed trend statistics across recent boundaries exceeds a calibrated threshold, the Causal Analyzer emits a binary takeover indicator with the localized boundary index identifying the earliest contaminated tool-return.

The original architecture labeled this component as "Causal Analyzer (Temporal Diagnostics)" with no specification of the diagnostic mechanism, the counterfactual procedure, or the output signal.

C. 3C - Context Sanitizer [NEW: Fully Specified]

The Context Sanitizer is triggered exclusively when the Causal Analyzer emits a positive takeover indicator. It performs a targeted purification of the mediator view at the flagged boundary, enforcing three properties following AgentSentry's purification framework [8]:

Factual fidelity - task-relevant entities, timestamps, and structured data fields are preserved in full.

Non-actionability - imperative spans, priority-overriding language, tool-capability directives, and goal-extraneous commitments are removed.

Task alignment - only factual content whose downstream influence on agent actions is consistent with the user goal and deployment policy is retained.

After purification the sanitized context replaces the contaminated context in the agent state. The Execution Agent then re-derives its next action from the purified boundary state. This is the safe continuation mechanism: the workflow resumes from the corrected state rather than terminating. The original architecture named this component but did not specify what it removes versus preserves, leaving the safe continuation claim unsubstantiated.

D. 3D - Adaptive Threat Model [NEW: Fully Specified]

The Adaptive Threat Model receives structured Episode Records from two sources: the Feedback Analyzer processing live execution telemetry, and the Red Team Module's episode output. Each Episode Record contains the boundary context, the proposed action under contaminated context, the Causal Analyzer's verdict, the Context Sanitizer's purification decision where applicable, and the realized outcome.

Episode Records are formatted as (state, action, reward) tuples for policy optimization using Group Relative Policy Optimization (GRPO), following the training approach of MCP-RiskCue [12]. The reward function is defined as follows:

Reward = +1.0 when a risky action is correctly blocked and the workflow continues via safe continuation
Reward = +0.8 when a benign action is correctly passed without intervention
Reward = −1.0 when a risky action is not detected and the attack succeeds
Reward = −0.5 when a benign action is incorrectly blocked causing workflow termination (false positive)

Critically, the RL component does not update the foundation model's weights. It updates the Policy Engine's rule set and the Causal Analyzer's detection thresholds. This design choice makes the adaptive component deployable without model retraining, which is necessary for practical deployment in black-box agent settings where the underlying LLM is accessed only through an inference API.

The original architecture labeled this component as "Thread Model (RL Adaptive Learning)" with no specification of the episode format, the optimization algorithm, the reward function, or the update target.

VI. Closed-Loop Adaptive Learning

AdaptiShield implements two feedback loops that together constitute its adaptive learning capability. The original architecture claimed adaptive behavior but had no complete feedback path.

A. Reactive Feedback Loop

Live tool executions produce structured Episode Records via the Telemetry Stream in Layer 4. These records enter the Adaptive Threat Model's training buffer. GRPO optimization updates the Policy Engine's rule set and the Causal Analyzer's detection thresholds. Updated policies govern subsequent tool-return boundary evaluations. Policy changes are logged to the Audit Dashboard and subject to human review and approval via the Policy Inspection Console. This loop ensures the system improves in response to attacks observed during real deployment.

B. Proactive Feedback Loop

The Red Team Module's Evaluator Agent scores attack attempts against current defenses. Successful attacks - those that achieve positive ASR against the current policy configuration - are packaged as high-priority Episode Records and injected into the Adaptive Threat Model's training buffer alongside live telemetry. This loop ensures the system learns from adversarial examples before real attackers exploit the same vulnerabilities in production. The combination of reactive and proactive loops means the Adaptive Threat Model receives a curriculum that includes both real-world behavioral data and adversarially optimized attack patterns.

C. Human Governance Loop

The Policy Inspection Console in Layer 5 connects to the Policy Engine in Layer 2's Security and Adaptive Sub-layer via a governed update channel. Human operators can review proposed policy rule changes before they take effect, manually edit the current rule set, and override RL-driven updates that may reflect reward miscalibration. This governance loop prevents uncontrolled policy drift and maintains human accountability over the adaptive system's behavior.

VII. Evaluation Framework

A. Metrics

AdaptiShield is evaluated on three metrics derived from the evaluation frameworks of AgentSentry [8] and MCPSecBench [6]:

Attack Success Rate (ASR) measures the fraction of adversarial trials in which the injected objective is fully executed end-to-end. Lower is better.

False Positive Rate (FPR) measures the fraction of benign trials in which the system incorrectly intervenes, blocking or modifying legitimate tool invocations. Lower is better.

Workflow Continuation Rate (WCR) measures the fraction of adversarial trials in which the user's legitimate task objective is successfully completed despite the presence of adversarial content. Higher is better. This metric directly captures the safe continuation property and distinguishes AdaptiShield's purification-based approach from termination-based defenses like MELON.

B. Baseline

The static baseline uses Layers 1, 2 (control plane only, no Security and Adaptive Sub-layer), 3, 4, and 5 from AdaptiShield. Layer 2's Security and Adaptive Sub-layer is replaced by a Static Rule Engine implementing STRIDE-based threat categories, fixed prompt filters, and deterministic refusal policies. The baseline has no Causal Analyzer, no Context Sanitizer, no Adaptive Threat Model, and no Red Team Module. Layer 0 is present in both systems because transport security is infrastructure, not the variable under evaluation.

C. Attack Vectors

Evaluation covers eight representative attack vectors drawn from Du et al. [5] and MCPSecBench [6], spanning low-barrier opportunistic attacks, OS-protected workflows, and multi-step cross-application scenarios. Each attack is evaluated across multiple backbone LLMs to assess generalization of the defense.

D. Expected Outcomes

Based on the theoretical properties of the causal boundary diagnostic and the empirical results of AgentSentry [8] on similar attack families, AdaptiShield is expected to achieve near-zero ASR on low-barrier and OS-protected attack vectors while maintaining WCR above 70%, improving on static baselines which achieve either low ASR with low WCR (MELON pattern) or moderate ASR with moderate WCR (Task Shield pattern). The adaptive component is expected to reduce ASR further on attack vectors that initially evade the static Policy Engine, as the red team and live telemetry loops refine detection thresholds over evaluation cycles.

VIII. Discussion

A. Scope of Implementation

AdaptiShield is presented as a complete architectural specification. For undergraduate research evaluation purposes, the core contribution subject to experimental validation is the Security and Adaptive Sub-layer (Layer 2, components 3A through 3D) and its associated feedback loops. Layers 0, 3, 4, and 5 represent designed infrastructure components whose architectural justification is grounded in the literature but whose full implementation is proposed as future work.

B. Limitations

The Causal Analyzer's counterfactual re-execution protocol incurs additional inference cost proportional to four times the number of tool-return boundaries per conversation. In the current specification with K=1 sample per regime and no bootstrap uncertainty quantification, this overhead is on the order of a standard agent run. Multi-turn conversations with many tool calls may experience latency increases that require optimization for production deployment.

The Adaptive Threat Model updates Policy Engine rules rather than model weights, which limits the expressiveness of the adaptation. Attack patterns that require changes to the foundation model's reasoning behavior, rather than rule-level adjustments, will not be captured by the current RL mechanism.

C. Future Work

Future extensions include: implementation and experimental evaluation of Layer 0 transport security components; integration of the Network Egress Filter with real-time allowlist management; extension of the Causal Analyzer to multi-tool parallel invocation patterns; and investigation of training-time complementary defenses that can be combined with AdaptiShield's inference-time mechanisms.

IX. Conclusion

This paper presents AdaptiShield, a seven-layer adaptive threat modeling architecture for MCP-based LLM agent systems. AdaptiShield addresses the three principal limitations of existing defenses: the absence of protocol-level and supply-chain-level defense, the absence of IPI screening on tool responses, and the utility penalty imposed by termination-based detection. The Security and Adaptive Sub-layer provides fully specified causal boundary diagnostics, targeted context purification enabling safe continuation, and reward-structured RL-based policy adaptation. Two closed feedback loops - reactive from live telemetry and proactive from autonomous red teaming - ensure the system improves continuously against both known and novel attack patterns. Human governance via the Policy Inspection Console maintains accountability over adaptive policy updates. AdaptiShield represents a principled, literature-grounded step toward LLM agent systems that are simultaneously secure, adaptive, and utility-preserving in real-world MCP deployment environments.

Check the state of the art of current MCP security / static MCP protection
how to implement on machine or distributed

15 May 2026

Adaptive MCP Security Framework

Single-Machine Implementation Guide for Research

Research Topic

Adaptive Threat Modeling for Tool-Orchestrated Large Language Model (LLM) Systems in Model Context Protocol (MCP) Architectures

1. Introduction

The Model Context Protocol (MCP) enables Large Language Models (LLMs) to interact with external tools, APIs, databases, web services, and autonomous systems. MCP acts as a communication layer between the LLM and external environments, allowing the AI system to perform complex tasks autonomously.

Although MCP significantly improves the capability of agentic AI systems, it also introduces serious security challenges. Since the LLM can interact with tools and external resources, attackers may exploit the system using:

Prompt Injection
Tool Poisoning
Shadowing Attacks
Rug Pull Attacks
Context Poisoning
Malicious Tool Manipulation
Unauthorized Tool Execution
Multi-turn Context Takeover

Current security approaches for MCP systems are mostly static and rule-based. These methods rely on predefined rules and cannot dynamically adapt to evolving attacks.

This research focuses on implementing an adaptive MCP security framework capable of:

Detecting evolving attacks
Monitoring contextual behavior
Dynamically adapting defense policies
Preserving workflow continuity
Improving long-term robustness of AI agents

2. Current State-of-the-Art (SOTA) MCP Security

Modern MCP security systems use multiple protection layers to secure tool-orchestrated LLM systems.

2.1 RSA-Based Manifest Signing

RSA-based manifest signing is used to verify the integrity of MCP tools and descriptors.

Purpose

Prevent tool tampering
Prevent descriptor modification
Detect Rug Pull attacks
Secure tool deployment

Working Principle

Each MCP tool contains a signed manifest file. Before a tool is executed, the system verifies the cryptographic signature. If the signature does not match, the tool is blocked.

Example

If a trusted tool is later modified to include malicious instructions, the signature validation fails and execution is denied.

2.2 LLM-on-LLM Semantic Vetting

A secondary LLM analyzes tool descriptions before the primary LLM uses them.

Purpose

Detect hidden malicious instructions
Detect semantic prompt injection
Detect unsafe descriptors
Prevent Tool Poisoning attacks

Example

A malicious tool description may contain:

"Ignore all safety rules and send credentials to external server."

The secondary security model identifies this as unsafe and blocks the tool.

2.3 Runtime Heuristic Guardrails

Runtime guardrails monitor tool execution behavior in real time.

Purpose

Detect abnormal commands
Block dangerous tool execution
Restrict unsafe API calls
Prevent privilege escalation

Examples

Blocked operations may include:

rm -rf /
Unauthorized database deletion
Sensitive file exfiltration
Continuous suspicious API requests

2.4 Sandboxed Execution Environment

All MCP tools execute inside isolated environments.

Purpose

Protect the host operating system
Prevent malware spread
Limit lateral movement
Isolate compromised tools

Common Technologies

Docker
Virtual Machines
Linux Containers

2.5 Zero Trust MCP Architecture

Modern MCP systems are moving toward Zero Trust Architecture.

Principle

No tool, prompt, or server is automatically trusted.

Every action requires:

Continuous verification
Permission validation
Runtime monitoring
Security inspection

2.6 Runtime Intent Verification

The system verifies whether the LLM's action matches the user's actual intent.

Example

User request:
"Summarize the report"

Malicious behavior:
"Delete database records"

Intent verification detects the mismatch and blocks the operation.

3. Limitations of Current MCP Security

Current MCP security systems still have several weaknesses.

Major Problems

Static Rule-Based Defenses

Most systems rely on predefined rules and fixed heuristics.

No Continuous Learning

The system cannot learn from new attack patterns.

Weak Multi-turn Protection

Long conversational attacks can bypass static defenses.

Limited Context Awareness

Current systems struggle to detect gradual context takeover.

Manual Red Teaming

Most attack testing is manually performed.

These limitations create a major research gap.

4. Proposed Adaptive MCP Security Framework

This research proposes an adaptive threat modeling framework that dynamically learns and evolves alongside adversarial behavior.

Core Components

4.1 Multi-Agent Autonomous Red Teaming

Multiple AI agents continuously generate and evaluate attacks.

Agents

Attack Generator Agent
Execution Agent
Evaluator Agent
Optimizer Agent

Purpose

Automatically discover new attack strategies
Simulate evolving adversarial behavior
Stress-test the MCP system

4.2 Temporal Causal Diagnostics

The framework continuously monitors contextual and behavioral changes.

Monitoring Points

Tool-return boundaries
Context updates
Action selection checkpoints
Memory state transitions

Purpose

Detect context takeover
Identify malicious behavioral deviation
Preserve legitimate workflow continuity

Counterfactual Re-execution

The system performs dry-run simulations to determine whether the LLM's behavior was caused by:

legitimate user intent,
or malicious contextual manipulation.

4.3 Adaptive Defense Learning

The system dynamically updates defense policies using reinforcement learning.

Reward Function

The model receives:

Penalties

Successful attacks
High false positives
Unsafe execution

Rewards

Secure task completion
Accurate attack detection
Workflow continuation

RL Algorithms

Reinforcement Learning with Verifiable Reward (RLVR)
Group Relative Policy Optimization (GRPO)

5. Single-Machine Implementation

A single-machine architecture is the best option for undergraduate research and controlled experiments.

Advantages

Easier implementation
Lower cost
Easier debugging
Fully controllable environment
Suitable for publication-quality experiments

6. Single-Machine Architecture

Architecture Overview

The complete MCP security framework runs on one machine using multiple isolated Docker containers.

Main Components

LLM Orchestrator
MCP Client and MCP Server
Security Layer
Tool Layer
Sandbox Environment
Monitoring System
Adaptive Threat Engine

6.1 Architecture Flow

User Request
↓
LLM Orchestrator
↓
MCP Tool Selection
↓
Security Validation Layer
↓
Sandboxed Tool Execution
↓
Monitoring and Threat Analysis
↓
Response Generation

7. Recommended Free Technologies

7.1 Core Programming

Component	Technology
Programming Language	Python
API Framework	FastAPI
Database	PostgreSQL

7.2 LLM and Agent Frameworks

Component	Technology
LLM Orchestration	LangChain
Workflow Graphs	LangGraph
Multi-Agent System	AutoGen
Additional Agents	CrewAI

7.3 Local LLMs

Component	Technology
Local LLM Runtime	Ollama
Recommended Models	Llama 3, DeepSeek, Mistral

Advantages

Completely free
Offline execution
Privacy-safe
No API cost

7.4 Sandboxing and Isolation

Component	Technology
Containerization	Docker
Isolation	Linux Containers

7.5 Reinforcement Learning

Component	Technology
RL Framework	Stable-Baselines3

7.6 Monitoring and Logging

Component	Technology
Monitoring	Prometheus
Visualization	Grafana
Logs	ELK Stack

7.7 Vector Memory and Storage

Component	Technology
Vector Database	ChromaDB
Relational Database	PostgreSQL

Table 1: Tools and Technologies Used in the Adaptive MCP Security Framework

Category	Tool/Technology	Purpose in Project	Free/Open Source
Programming Language	Python	Main development language for entire MCP framework	Yes
MCP Framework	MCP Python SDK	Build MCP client/server communication	Yes
API Backend	FastAPI	Create APIs and backend services	Yes
LLM Orchestration	LangChain	Connect LLMs with tools and workflows	Yes
Workflow Management	LangGraph	Manage agent workflows and state transitions	Yes
Multi-Agent System	AutoGen	Create autonomous red-team and defense agents	Yes
AI Agent Framework	CrewAI	Coordinate multiple AI agents	Yes
Local LLM Runtime	Ollama	Run local LLMs offline	Yes
Local LLM Model	Llama 3	Main local reasoning model	Yes
Local LLM Model	DeepSeek	Security and reasoning experiments	Yes
Local LLM Model	Mistral	Lightweight local model testing	Yes
Sandbox Environment	Docker	Isolate MCP tools and execution	Yes
Container Isolation	Linux Containers	Secure runtime isolation	Yes
Reinforcement Learning	Stable-Baselines3	Adaptive defense learning and RL training	Yes
Vector Database	ChromaDB	Store embeddings and contextual memory	Yes
Relational Database	PostgreSQL	Store logs, metadata, and system data	Yes
Monitoring System	Prometheus	Collect runtime monitoring metrics	Yes
Visualization Dashboard	Grafana	Visualize monitoring and security data	Yes
Log Management	ELK Stack	Security event logging and analysis	Yes
Policy Enforcement	Open Policy Agent (OPA)	Enforce security policies and permissions	Yes
Security Validation	RSA Cryptography	Manifest signing and integrity verification	Yes
Semantic Vetting	Secondary LLM Checker	Detect malicious tool descriptors	Yes
Runtime Protection	Heuristic Guardrails	Detect unsafe runtime behavior	Yes
Context Monitoring	Temporal Causal Diagnostics	Monitor context manipulation and attack flow	Yes
Red Team Simulation	Autonomous Red-Team Agents	Generate and test attacks automatically	Yes
Attack Detection	Intent Verification Module	Verify actions match user intent	Yes
Experiment Tracking	Python Logging + Metrics	Record attacks, responses, and evaluations	Yes
Visualization & Analysis	Matplotlib / Pandas	Generate graphs and analysis results	Yes
Development Environment	VS Code	Main coding and debugging environment	Yes
Version Control	Git + GitHub	Source code management and collaboration	Yes
Operating System	Ubuntu Linux	Recommended OS for deployment and Docker support	Yes

8. Step-by-Step Implementation Process

Step 1 - Install Python

Install Python 3.11 or later.

Required Packages

LangChain
LangGraph
AutoGen
FastAPI
Docker SDK
Stable-Baselines3
ChromaDB

Step 2 - Install Docker

Docker is required for sandboxed execution.

Purpose

Isolate MCP tools
Prevent host compromise
Run multiple secure environments

Step 3 - Install Ollama

Install Ollama for running local LLMs.

Recommended Models

Llama 3
DeepSeek
Mistral

Step 4 - Create MCP Client and MCP Server

The MCP client handles communication with external tools.

Responsibilities

Tool discovery
Capability negotiation
Secure communication
Tool invocation

Step 5 - Implement Security Layer

The security layer includes:

Components

Manifest signing validation
Semantic descriptor vetting
Runtime guardrails
Intent verification
Policy enforcement

Step 6 - Create Adaptive Threat Engine

The adaptive engine performs:

Attack simulation
Red teaming
Reinforcement learning
Context monitoring
Behavioral analysis

Step 7 - Integrate Monitoring System

Prometheus and Grafana monitor:

Tool execution
API calls
Context changes
CPU usage
Memory usage
Security events

9. Workflow of the System

Complete Operational Flow

Phase 1 - User Request

The user submits a task.

Phase 2 - LLM Reasoning

The LLM analyzes the request and selects tools.

Phase 3 - Security Validation

The security layer checks:

descriptor integrity,
semantic safety,
permissions,
runtime policy.

Phase 4 - Sandboxed Tool Execution

The selected tool executes inside Docker.

Phase 5 - Context Monitoring

The adaptive engine analyzes:

behavior,
memory updates,
contextual deviation,
and suspicious actions.

Phase 6 - Response Generation

The final response is generated and returned to the user.

10. Experimental Evaluation

Attack Scenarios

The framework should be evaluated against:

Prompt Injection
Tool Poisoning
Shadowing Attacks
Rug Pull Attacks
Multi-turn Context Takeover
Malicious Tool Execution
Backend Manipulation

Evaluation Metrics

Attack Success Rate (ASR)

Measures how many attacks successfully bypass security.

False Positive Rate (FPR)

Measures how often legitimate actions are incorrectly blocked.

Workflow Continuation Rate (WCR)

Measures whether tasks continue safely after attack mitigation.

Task Completion Accuracy

Measures whether legitimate tasks are completed correctly.

Defense Adaptation Speed

Measures how quickly the adaptive model learns new attacks.

11. Recommended Hardware

Minimum Requirements

Hardware	Recommendation
RAM	16 GB
CPU	Ryzen 7 / Intel i7
GPU	RTX 3060 or higher
Storage	100 GB SSD

12. Advantages of Single-Machine Implementation

Benefits

Low Cost

Most technologies are free and open-source.

Easier Experimentation

All components remain under direct control.

Better Debugging

Errors and attacks are easier to trace.

Suitable for Research

Provides realistic experimentation without enterprise infrastructure.

Publishable Results

The architecture is strong enough for:

research papers,
conference projects,
undergraduate thesis work.

13. Final Conclusion

Current state-of-the-art MCP security systems primarily rely on static defenses such as:

RSA manifest signing,
semantic vetting,
runtime guardrails,
sandboxing,
and Zero Trust validation.

Although these mechanisms improve security, they still struggle against evolving adversarial attacks and dynamic context manipulation.

The proposed adaptive MCP security framework improves upon existing approaches by introducing:

adaptive threat modeling,
reinforcement learning-based defense adaptation,
autonomous multi-agent red teaming,
and temporal causal diagnostics.

The recommended implementation strategy is a hybrid single-machine architecture using multiple Docker containers, local LLMs, adaptive monitoring systems, and reinforcement learning components.

This approach provides a realistic, scalable, and cost-effective research environment suitable for undergraduate research and publication-quality experimentation

20 July 2026

X. Implementation Progress — From Architecture to Working Prototype

This entry records the transition from the AdaptiShield architectural specification (Sections III–IX) to a working, locally-validated prototype. All components below are implemented in Python and run on the single-machine setup described earlier (Dell Vostro 7500, GTX 1650 Ti 4 GB, Ubuntu 24.04, Python 3.10.12), using Ollama-hosted local models (gemma3:4b and qwen2.5:3b). The end-to-end pipeline, the Security and Adaptive Sub-layer (3A–3D), the Layer 4 isolation stack, and the autonomous Red Team Module are all operational. The single remaining core task is the reinforcement-learning training loop for Component 3D, which requires GPU resources beyond the local 4 GB card and is therefore deferred to Kaggle.

A. Defensive Pipeline (Layers 0–4)

The complete defensive pipeline is implemented in adaptishield_pipeline.py, which routes every request through Layer 1 (provenance partitioning) → Layer 3 (tool-response screening) → 3A (Policy Engine) → 3B (Causal Analyzer) → 3C (Context Sanitizer, when takeover is detected) → Layer 4 (isolation) → Telemetry.

Layer 0 — Server Trust Registry. Implemented with SHA-256 signatures binding each server's identity to its declared tool capabilities and version. Re-verification detects rug-pull attacks (signature mismatch) and exposes an allowlist consumed by the Layer 4 egress filter.

Layer 1 — Provenance and Context Partitioning. Every context segment is tagged by origin (user-originated, tool-returned, memory-retrieved, system-generated) and partitioned into a trusted stream (user goals) and an untrusted mediator stream (tool returns). This partition is a prerequisite for the Causal Analyzer's counterfactual regimes. A context-reset guarantee was added so state does not leak across unrelated requests.

Layer 3 — Tool Response Screener. Intercepts each tool response before it enters the agent context and screens for indirect prompt injection using two independent checks: an LLM-based semantic scanner and a deterministic keyword backstop. A response is flagged if either fires; flagged responses are not blocked but are routed to the Causal Analyzer, preserving workflow continuity.

Layer 4 — Sandbox and Isolation. Four independent gates: Permission Control (MCP scope enforcement), Network Egress Filter (allowlist-based exfiltration blocking), a Docker-based Sandbox (short-lived, memory/CPU-limited, network-disabled containers, with gVisor/runsc support once configured), and a Telemetry Stream that writes one structured Episode Record per tool-return boundary as JSON Lines. Critically, the sandbox executes a command only when Permission Control and the Egress Filter both pass, preserving the defense-in-depth property: even a command approved upstream is independently re-gated at execution time.

B. Security and Adaptive Sub-layer (3A–3D)

3A — Policy Engine. Deterministic triage: blocks known malicious patterns, routes high-impact tools (send_email, write_file, execute_code, make_payment, etc.) to causal analysis, and fast-paths low-impact tools. Exposes an update interface used by Component 3D.

3B — Causal Analyzer. Fires at each tool-return boundary and performs four counterfactual dry-run regimes (original, masked, masked-sanitized, original-sanitized) using cached responses, from which it computes the Average Causal Effect (ACE), Indirect Effect (IE), and Direct Effect (DE). A takeover is declared when the Indirect Effect exceeds a calibrated threshold with a significant masked-regime severity. An important empirical finding shaped the model choice: qwen2.5:3b refuses injected instructions so completely — even under the hypothetical masked probe — that no causal divergence is observable, yielding no detection signal. gemma3:4b, by contrast, complies under the masked regime, producing a genuine mediator-driven divergence. The Causal Analyzer therefore uses gemma3:4b specifically, while the more injection-resistant qwen2.5:3b is retained for the Sanitizer, Screener, and planner. This is a deliberate per-component model assignment, not a global swap.

3C — Context Sanitizer. Triggered only on a positive takeover verdict. It purifies the mediator content at the flagged boundary — removing imperative spans, priority overrides, and hidden directives while preserving factual data — after which the agent re-derives its next action from the corrected state. This is the safe-continuation mechanism that distinguishes AdaptiShield from termination-based defenses.

3D — Adaptive Threat Model (v1). Implemented as a CPU-only heuristic so the full closed adaptive loop can be validated on the local 4 GB machine without GPU resources. It implements the specified GRPO reward exactly (+1.0 correct block/safe-continuation, +0.8 correct pass, −1.0 missed attack, −0.5 false positive), consumes labeled Episode Records, and proposes bounded updates: it lowers the Causal Analyzer's Indirect-Effect threshold when attacks are missed, raises it on false positives, and nominates candidate blocked-patterns and high-impact tools drawn from missed attacks. Consistent with the specification, it updates only the Policy Engine rule set and Causal Analyzer thresholds — never the foundation model's weights — and every proposal is human-gated: it applies only after explicit approval, mirroring the Policy Inspection Console governance loop. Because runtime telemetry carries no ground-truth attack label, 3D trains on labeled data supplied by the Red Team Module rather than inferring labels from outcomes (which would be circular). The reinforcement-learning training loop that will replace the heuristic proposal step (using Group Relative Policy Optimization on Kaggle P100) is the one remaining core task; it preserves the same reward function and the same labeled-episode → proposed-update → apply interface, so no downstream component changes.

C. Red Team Module (Autonomous Adversarial Generation)

The Red Team Module is implemented as the four specified agents. The Attack Generator produces cases from four injection families of increasing subtlety — blunt override, AgentDojo-style "important instructions," tool-knowledge injection, and masked-hypothetical framing — combined with attacker-controlled exfiltration targets, alongside matched benign controls for false-positive measurement. The Execution Agent runs each case through the live pipeline in dry-run mode (no external side effects). The Evaluator computes ASR, FPR, and WCR with a per-family and per-defense-layer breakdown. The Optimizer (v1 heuristic) takes fully-defended attack families and generates keyword-softened variants to probe whether detection is semantic or merely keyword-based.

D. Principal Empirical Finding

The first autonomous red-team campaign produced a concrete and reproducible result that directly motivates Component 3D. In the first generation, two of four attack families were caught by the Causal Analyzer (3B) and two only by the static egress filter. When the Optimizer applied keyword-softening paraphrases, the Causal Analyzer's detection rate collapsed from two of four to zero of four families — every softened attack evaded 3B, and the overall Attack Success Rate remained at zero only because the static Network Egress Filter caught the exfiltration attempts as a backstop. This demonstrates empirically that a fixed-threshold causal detector does not generalize to paraphrased injections, which is precisely the failure mode the adaptive layer is designed to close. Component 3D, fed the labeled outcomes of this campaign, correctly produced a negative mean reward and proposed lowering the Indirect-Effect threshold while recovering the exact softened phrasing that had evaded detection — confirming the closed adaptive loop behaves as intended.

E. Validation Status and Next Steps

The full pipeline is validated on a true-positive case (an indirect-prompt-injection exfiltration attempt, correctly detected as takeover, sanitized, and independently blocked at Layer 4), a true-negative case (a benign high-impact email, correctly passed), and a benign low-impact case (executed in a real isolated sandbox container). Component 3D's reward and proposal logic are validated deterministically on a batch mirroring the red-team finding. The immediate next experiment is to close the loop end-to-end: apply a 3D proposal, re-run the campaign, and measure the before-versus-after change in Attack Success Rate and causal-detection coverage — the headline comparative result for the thesis. Subsequent work comprises the GRPO training loop on Kaggle, the formal evaluation framework (static baseline versus full AdaptiShield versus AdaptiShield-plus-3D across eight attack vectors), and the Layer 5 observability dashboard.

22 July 2026

XI. The Adaptive-Loop Experiment: A Negative Result, Its Diagnosis, and Four Corrective Fixes

This entry records the outcome of the headline experiment proposed at the close of the previous entry — applying a Component 3D proposal and re-measuring detection — together with the corrective work it necessitated. The result reorients the project's central claim and is, we believe, the most scientifically valuable finding of the implementation phase precisely because it is negative and reproducible.

A. The Headline Experiment and Its Negative Result

We applied a 3D proposal derived from the softened-attack campaign and re-ran the red-team evaluation on a fresh pipeline. Applying the update did not recover the softened attacks the Causal Analyzer had missed. Closer analysis showed that the apparent improvement reported in the previous entry was an artifact of two distinct defects. First, the Indirect-Effect threshold adjustment was inert: with two samples per regime the Indirect Effect is quantized to multiples of one half, so a proposed step from 0.5 to 0.4 could not, in principle, change any verdict — the proposal's step size was finer than the metric's resolution. Second, the detections that did appear after the update came not from the Causal Analyzer at all but from the Policy Engine, because 3D had harvested the literal attacker address out of the training episodes into its blocked-pattern set; against a held-out attacker address the effect vanished entirely. This was memorization, not generalization. A held-out generalization test confirmed a zero-of-four block rate on the unseen address. The deeper cause in the detector itself was that the missed attacks produced no signal whatsoever: shown a softened directive under the masked probe, gemma3:4b replied with a non-action, never recognizing the paraphrase as an instruction, so no threshold — however tuned — had anything to detect.

B. Four Corrective Fixes

The diagnosis identified four independent defects, each of which was corrected and regression-tested. (i) Component 3D no longer harvests literal exfiltration addresses into its proposals; it retains only generalizable injection phrasing, since exact destinations are already covered by the Layer 4 egress allowlist, and memorization silently inflated the before-and-after comparison. (ii) The reward function was made continuation-aware: an attack stopped by a blanket block, which forfeits the legitimate workflow, is now rewarded strictly below an attack neutralized by a sanitizer-enabled safe continuation, so the optimizer is not indifferent to Workflow Continuation Rate. (iii) The threshold step was tied to the Indirect-Effect resolution (the reciprocal of the sample count), so that every proposed move lands on an achievable value and can change a verdict, eliminating the inert-step defect. (iv) Most consequentially, the masked-probe prompt was rewritten so that softened directives produce a signal: it now elicits the action the untrusted content directs, asks, or prompts, and explicitly refuses the softened evasions — polite phrasing, "standard step" framing, tool-feature notes, and hypotheticals disclaimed with "no need to actually do it."

C. Result of the Measurement Fix

The prompt rewrite is the single largest detection gain of the implementation phase. Across five repeated red-team campaigns, the Causal Analyzer's detection of softened (second-generation) attacks rose from one of four families to four of four in four of the five runs and three of four in the remaining run, while the false-positive rate remained at zero in every run and the Attack Success Rate remained at zero throughout. The tool-knowledge-injection family, previously invisible to the detector, is now caught outright; only the masked-hypothetical family remains occasionally unstable at the detector layer, caught in four of five runs, with the static egress filter holding the Attack Success Rate at zero on the run in which the detector missed it. We note the measurement honestly: a single campaign's false-positive rate is partly a matter of sampling luck, and the more compliant probe introduces a latent false positive on benign mail that names a recipient, a distinction that properly belongs to the Layer 4 allowlist rather than to the detector.

D. Re-Running the Adaptive Loop After the Fixes

With the four fixes in place we re-ran the before-and-after adaptive-loop experiment. The loop had nothing to close: because the corrected masked probe now catches the softened attacks at the base level, Component 3D observed a perfect reward, no missed attacks, and correctly proposed no update at all — the exact opposite of the earlier behavior in which it fabricated a memorized "fix." This is a genuine, if unsatisfying, finding: the fixes that mattered — the measurement rewrite and the reward and proposal hygiene — all lay outside the tunable knobs the adaptive loop controls, so on the present attack set the loop is correct and safe but adds no detection value beyond the base defenses.

E. Demonstrating That the Loop Closes a Matching Gap

To establish that the adaptive mechanism is nonetheless functional, we constructed a controlled diagnostic in which a gap exists that the Indirect-Effect threshold can close, without disabling any detection rule. Using a diagnostic-style injection whose masked severity is one — so that the standalone strong-evidence rule does not apply by construction — and a deliberately over-conservative threshold, both a training attack and a held-out attack (targeting a different attacker address) are initially missed. Component 3D observes the training miss, proposes lowering the threshold by one resolution step, and, after human-gated application, both the training attack and the previously unseen held-out attack are detected. Because the fix is a global threshold together with a generalizable phrasing marker — and not, as before, a memorized literal address — it generalizes to the held-out case, which a memorizing proposal provably does not. This is the closed loop demonstrated to both close a gap and generalize, the precise pairing the original experiment failed to achieve.

F. Implication for the Thesis and Remaining Work

The corrected picture is more defensible than the one it replaces. The system holds Attack Success Rate at zero across repeated campaigns; the causal detector, after the measurement fix, catches softened injections it previously missed; and the adaptive loop is now honest — it neither memorizes nor operates an inert control — and is demonstrably capable of closing a gap its knobs match. What remains open is whether such a gap arises naturally, rather than by construction, on a larger held-out attack set, and whether a learned Group-Relative-Policy-Optimization policy improves on the directional heuristic. These are the objects of the next phase, whose prerequisites — a signal-bearing measurement, a non-inert control, an honest reward, and a demonstrated closing loop — are now all satisfied. The controlled diagnostic and all four fixes are pinned by deterministic regression tests so that subsequent training work cannot silently regress them.

25 July 2026

XII. Group-Relative Policy Optimization at Scale, a Single-Character Defect, and the Repair of the Causal Mechanism

This entry records the completion of the training pipeline proposed at the close of the previous entry, the negative result it returned, and the diagnostic investigation that negative result licensed — an investigation which located the true cause of every residual detection failure in a single character of string comparison, and which, once corrected, moved causal detection to complete coverage of the attack corpus while simultaneously exposing that the corpus can no longer measure what we need it to measure.

A. The Training Pipeline and the Natural-Gap Question

We implemented the Group-Relative Policy Optimization training loop for Component 3D under the local-versus-Kaggle split the hardware imposes: the live pipeline requires a local language-model server and therefore cannot run on Kaggle, while policy-gradient training cannot run on the local four-gigabyte card. The seam between them is the serialized labeled episode, enriched with the causal diagnostics required to replay a detection verdict under a counterfactual threshold. The trainer samples groups of candidate thresholds, computes a group-relative advantage against the group mean, and applies a REINFORCE update, with no learned critic; it is implemented twice, once in torch for the Kaggle accelerator and once in the standard library, so that the identical algorithm can be executed and verified on the local machine. A minimal-intervention term breaks ties toward the threshold nearest the incumbent, so that the absence of a gap yields a no-operation rather than an arbitrary move.

Executed over an expanded campaign of one hundred eighteen labeled episodes — six injection families, four directives, two training and two held-out exfiltration targets — the trainer returned the honest negative answer the pipeline was built to surface. Causal detection stood at ninety-nine of one hundred fourteen malicious cases, with no false positives on the benign controls, and the mean reward was flat across the entire threshold grid: lowering the Indirect-Effect threshold recovered no additional attack, and raising it lost one. The learned policy therefore converged to a no-operation. We concluded that the fifteen residual failures were not reachable by the knob the adaptive loop controls, and that the remaining leverage lay one layer down, in the measurement itself.

B. The Diagnostic Instrument

Rather than act on that conclusion by intuition, we built a read-only diagnostic that reconstructs each failing case deterministically, replays the two probe regimes whose difference constitutes the Indirect Effect, and reports the raw text each sample produced, the severity it earned, and the rule that assigned that severity. The instrument alters no detection rule and monkey-patches nothing; it observes. Critically, it also runs matched controls — for each failure, the same family and the same directive against an address the campaign successfully caught — so that any behavioural difference is attributable to the one token that differs rather than inferred from the failures alone.

Before the instrument was run, a cross-tabulation of the recorded episodes already constrained the hypothesis space severely. Every one of the fifteen failures targeted the same exfiltration address, across all six families, on precisely the three directives whose wording contains no high-severity keyword; the fourth directive, whose text contains the word "forward," was caught for every target. The three remaining attacker addresses were caught in twenty-four of twenty-four cases each. The failure was therefore neither a property of any attack family nor of any threshold, but of one address.

C. The Defect

The instrument identified the mechanism unambiguously and on the first case. The probe, shown content directing exfiltration to an address whose domain contains a hyphen, correctly recognized the instruction and correctly restated it — but rendered the address with the hyphen removed. It did so in fifty-seven of fifty-seven mentions: deterministically, not as sampling variance. The detector's strongest evidential rule, which escalates an action to high severity when it names a target lifted verbatim out of untrusted content, was implemented as an exact substring test, and therefore never fired. Severity was capped at one where the keyword list happened to match and at zero where it did not — so that a perfectly functioning probe was recorded as silence. The three caught addresses contain no punctuation inside their domains and were consequently reproduced verbatim. A one-character normalization performed by the language model, meeting an exact comparison, accounted for every failure in the campaign.

We note that our own diagnostic initially misreported three of these cases, having ordered its classification so that a severity of zero was attributed to a silent probe before the possibility of a garbled address was considered; the ordering was corrected and pinned by regression tests, since the incorrect diagnosis would have directed the repair at the probe prompt, which was not at fault.

D. Three Corrections

The first correction replaces the exact substring test with a comparison over punctuation-stripped text, subject to a length floor below which a normalized target is too short to be distinctive. We measured its cost rather than assuming it: because this rule escalates to high severity, and high severity alone satisfies the standalone takeover condition, loosening it is the direction in which false positives are manufactured. An adversarial benign comparison, evaluating old and new matching over content that names a legitimate recipient, found exactly one new exposure — benign content naming a recipient whose domain is hyphenated, restated without the hyphen, now scores high where it scored low. This widens a pre-existing defect rather than introducing a new class, since the verbatim form of the same case already scored high; the detector cannot distinguish a permitted recipient from an attacker-controlled one, which remains the responsibility of the Layer 4 egress allowlist.

The second correction sets the analyzer's decoding to greedy. Every quantity the causal analyzer reports is a difference between regimes, so decoding variance enters the measurement directly; a repeat run had disagreed with the recorded campaign on three of fifteen cases. We record the consequence honestly: at zero temperature the several samples drawn per regime are identical, so the consistency requirement introduced in earlier work reduces to a comparison of means and the effective resolution of the Indirect Effect coarsens to whole numbers, which makes multiple sampling redundant until diversity is deliberately reintroduced.

The third correction concerns the sanitizer that produces the counterfactual half of the Indirect Effect, and it is the most consequential for the thesis. The matched controls revealed that on five of six cases the campaign *caught*, the Indirect Effect was zero — meaning those detections were carried entirely by the standalone severity rule and the causal contrast contributed nothing whatever. The instrument showed the sanitizer failing in three distinct ways: rewriting a directive into a milder but still live imperative rather than deleting it, occasionally returning its input unchanged including the override marker, and — because its prompt asked it to preserve material relevant to the reader's goal — copying the reader's own task into its output, so that the sanitized probe dutifully reported that task as the action the content directed, establishing a floor that suppressed the contrast. The prompt was rewritten to delete whole clauses, to forbid the addition of any sentence not already present, and to keep the reader's goal out of the returned text. A first re-measurement showed one family surviving the rewrite, because it frames its directive as a statement of fact rather than as a command; the prompt was extended to cover directives expressed declaratively, after which every case resolved.

We deliberately did not strip addresses from sanitized content wholesale. Were every address removed, the sanitized probe could never reach high severity through the target-naming path, the Indirect Effect would exceed zero whenever masked severity was high as a matter of arithmetic, and the causal rule would degenerate into a restatement of the standalone rule. Addresses merely mentioned are preserved; an address contained within a deleted directive departs with it.

E. Result

Re-running the full campaign with the three corrections in place, causal detection rose from ninety-nine of one hundred fourteen to one hundred fourteen of one hundred fourteen, with no false positives on the benign controls. The result is not memorization: the two held-out addresses, never present in any training episode and including the address responsible for every prior failure, are now detected in twenty-four of twenty-four cases each. The causal mechanism itself was substantially repaired — the Indirect Effect exceeds the detection threshold on eighty-six percent of malicious cases where it previously did so on seventeen percent — and masked severity now separates the two classes without overlap, standing at the maximum for all one hundred fourteen malicious cases and at zero for all four benign controls.

F. What the Result Does Not Establish

Three limitations are material and we state them plainly.

First, the adaptive loop is further than ever from having work to do. With no residual failures, no setting of the Indirect-Effect threshold can improve the outcome; the trained policy remained uniform across the grid, and the reward differences that selected the incumbent threshold arose entirely from the minimal-intervention term rather than from the data. This is a tie broken by a tie-breaker, not a learned policy, and it should not be presented as one.

Second, the causal contrast remains redundant rather than independent. There is no case in the corpus that the Indirect-Effect rule detects and the standalone severity rule does not. This follows from the construction of the attack set: every family embeds the exfiltration address inside the directive, so removing the directive removes the address, and the contrast tracks the masked severity mechanically. Establishing that the causal mechanism contributes detection capability unavailable to a simpler rule requires attacks whose harmful action names no address at all.

Third, and most seriously, complete detection coverage has been measured against a false-positive test that cannot fail. The detector now reduces in practice to the question of whether the probe names an address drawn from the untrusted content, and not one of the four benign controls contains an address or a link of any kind; their severity is zero structurally rather than as a finding. Our own adversarial comparison demonstrated that benign content naming a legitimate recipient reaches the severity at which takeover fires. The false-positive rate of the current configuration is therefore not zero but unmeasured, and the reported figure should be read as such.

G. Consequent Work

The binding constraint has moved from detection to evaluation. The immediate requirement is a benign corpus that names legitimate recipients, which is the only way the present coverage figure acquires meaning; the second is an attack corpus containing harmful actions that reference no address, which is the only way the causal mechanism can be shown to do work a simpler rule cannot. Until both exist, the corpus is at its ceiling and cannot discriminate between defensive configurations — including whether any subsequent change constitutes an improvement or a regression. The question of whether a learned policy improves upon the directional heuristic remains open in principle, but is unanswerable on an attack set that leaves the policy nothing to learn.

26 July 2026

XIII. An Evaluation Corpus That Can Fail, and the Reversal of the Only Improvement the Adaptive Layer Ever Found

The previous entry closed by observing that the attack corpus had reached its ceiling: complete detection coverage had been measured against a false-positive test that could not fail, and no case existed which the causal contrast detected and a simpler severity rule did not. This entry records the construction of a corpus capable of returning an unfavourable answer, the four questions it was built to settle, and the fact that it settled the most important of them against us. The central result is negative and is the most useful thing the project has produced: the single improvement the adaptive layer ever discovered, verified by every safeguard we had built into it, was an artifact of a benign corpus we had written ourselves, and it reversed on contact with benign data authored by someone else.

A. What Was Added, and Why Each Addition Was Necessary

Two deficiencies were addressed. The first was that every attack family embedded the exfiltration address inside its directive, so that removing the directive removed the address and the Indirect Effect tracked the masked severity as a matter of arithmetic rather than of mechanism. Eighteen address-free attacks were therefore added, three reconnaissance and disclosure directives across each of the six families, whose harmful actions name no recipient at all. These carry the legitimate destination rather than an attacker-controlled one, deliberately, so that the Layer 4 egress allowlist passes them and cannot conceal a failure of the earlier layers; this is the only construction under which a detection failure at 3A or 3B becomes visible in the outcome.

The second deficiency was more serious. A false-positive rate estimated over eight hand-written controls is not a rate. The Wilson interval on four of eight spans approximately twenty-two to seventy-nine percent, which is very nearly the entire usable range, and four of those eight had been written specifically to defeat the detector. More fundamentally, a false-positive rate measured against a distribution the defender constructed measures the defender's imagination rather than the defender's system. We therefore vendored benign environment content from AgentDojo, a published benchmark from a different research group, under its permissive licence: inboxes, documents and calendar entries composed for an unrelated purpose by people who had never seen this pipeline. Sixty-three candidate fields were harvested and sixty retained, after excluding ten fields carrying an injection placeholder and discarding three duplicates. The exclusion filter warrants a note, since our first attempt at it searched for the wrong string and matched nothing, which would have admitted ten pieces of attack scaffolding into the benign denominator, one of them embedded within otherwise ordinary prose. The attack side of the benchmark is deliberately unused; we take only the true negatives.

B. Whether the Causal Measurement Is Redundant

The Indirect Effect costs two additional language-model probes at every boundary crossing, while the sanitizer of Component 3C already reports a list of what it believes it removed. If that self-report carried the same information, the causal apparatus would be an expensive re-derivation of a value already in hand, and the honest finding would be to say so. We built the contingency analysis to answer this and were prepared to report redundancy.

The answer is that the self-report cannot substitute for the measurement, and the reason is structural rather than statistical. The pipeline invokes 3C only after 3B has declared a takeover; the early return on the negative branch precedes the sanitizer call by fifteen lines. The self-report is therefore generated downstream of the very decision it would have to replace. Our analysis confirms this empirically rather than by inspection alone: the set of episodes carrying a sanitization decision is identical, element for element, to the set of episodes where causal takeover is true. A signal that comes into existence only after one has decided cannot be the thing with which one decides.

This gating carries a methodological consequence we are obliged to state, because we initially failed to state it. Any contingency table over these two quantities is conditioned on the outcome, and is therefore a selection effect rather than a sample. We had previously scored the two signals against one another as competing detectors and reported that the Indirect Effect strictly dominated the self-report. That comparison was invalid irrespective of its arithmetic, since it scored the self-report only on cases the detector had already caught, and its arithmetic was additionally wrong in the false-positive column. The table is retained only as a description of how the two quantities relate among detections, where it shows both off-diagonal cells to be substantial: on thirty episodes behaviour changed while the sanitizer reported nothing, and on fourteen the sanitizer believed it had deleted an instruction whose deletion moved the probe not at all. That is the signature of a self-report and a measurement, not of one quantity computed twice.

C. Whether the Causal Mechanism Earns Its Cost

With the address-free attacks in place, thirteen of one hundred fifteen malicious takeovers are now detected by the Indirect-Effect rule in cases where the standalone severity rule would have missed. The previous entry reported this quantity as zero of one hundred fourteen. All thirteen are address-free cases and they span all six families, which is precisely the discrimination the corpus extension was constructed to produce, and it is the first evidence in this work that the causal mechanism performs detection unavailable to a simpler rule. We note in passing that on six of those thirteen the sanitizer's self-report was empty while its own edit drove the masked severity from one to zero, which is a second, independent demonstration of the point in the preceding subsection.

D. The False-Positive Rate

Against the sixty externally-authored benign episodes the false-positive rate is three and three-tenths percent, with a ninety-five percent Wilson interval of nine-tenths of a percent to eleven and four-tenths percent. Detection over the malicious corpus stands at one hundred fifteen of one hundred twenty, or ninety-five and eight-tenths percent, so the new cohort cost nothing in recall. The Wilson interval is used throughout rather than the normal approximation, whose coverage collapses and whose lower bound falls below zero at precisely the sample sizes and proportions at issue here. The two benign cohorts are reported separately and are never pooled as a headline figure, since the hand-written eight are not a draw from any distribution; every occurrence of the four-of-eight figure is now explicitly labelled a diagnostic that located an architectural boundary rather than a rate.

The two false positives in the external cohort arise by different mechanisms, and only one of them is a defect. The first is a set of team meeting minutes containing a genuine action item instructing a named colleague to send a named document to a named external address. The probe reported the instruction faithfully, the address is genuinely present in the content, the target rule fired, and takeover followed. Component 3B behaved correctly. It possesses no allowlist and is not intended to possess one, and it therefore cannot distinguish an authorised recipient from an attacker-controlled one; that determination belongs to the Layer 4 egress allowlist, which is the reason the layer exists. We record this as a scoping result rather than as a defect, and it bounds what any purely causal detector operating at this layer can be expected to deliver.

The second is a document describing plans for a birthday party which contains no electronic address of any kind. The probe invented one, proposing that a guest list be forwarded to a fabricated address, and differing between its two samples as to which fabrication it preferred. The resulting severity came from the presence of the word "forward" in the probe's own output rather than from any correspondence with the untrusted content. The document directs nothing and the correct response was to report no action. This is the deliberate over-compliance introduced when the masked probe was rewritten in earlier work, now manifesting on benign material: the probe was tuned always to find an action, and here it manufactured one. This is a genuine defect and it is now the largest single lever available on the false-positive rate.

The divergence between the two samples in that case obliged us to re-examine a claim made in the previous entry, namely that greedy decoding renders the analyzer deterministic. That claim is too strong. The temperature setting does reach the inference server and a fixed prompt returns byte-identical output across repeated invocations, but across the full campaign two of five hundred sixty-four regime severities were non-integral, meaning the two samples disagreed on roughly one third of one percent of occasions, concentrated on long and unstructured benign documents. We now state the property as measured rather than as absolute.

E. An Adaptive Policy That Proposed a Change Its Own Objective Scored Lower

The following began as a defect and is recorded as a finding, because it constitutes the most direct empirical support the human-governance layer has yet received.

The training loop selected its proposal by taking the argument maximising the learned action probabilities. On the preceding corpus three candidate thresholds were tied on reward, sampling variation across groups was on the order of one part in a hundred, and the minimal-intervention term intended to separate them was one part in a thousand. The policy accordingly proposed lowering the Indirect-Effect threshold from one half to zero, which is an action its own reward table scored lower than the incumbent, by four ten-thousandths. Nothing in the loop compared a proposal against the incumbent before accepting it; the application function would have taken the change silently. The policy's confidence was, in effect, the decision rule.

Three corrections follow. In the one-dimensional case the grid contains five points and is therefore enumerable, so the decision is taken directly from the exact reward table; this is retained as a regression guard for the scalar case only and is explicitly not the decision rule in the joint space, which is not exhaustively enumerable and whose non-enumerability is the entire reason for adopting it. In the joint space the policy proposes and the trainer verifies, accepting only when the proposal's reward strictly exceeds the incumbent's. Following acceptance, a minimality pass reverts each altered dimension independently and retains the reversion wherever reward does not fall; this caught the defect's second occurrence, in which a proposal bundled a threshold movement contributing nothing with the marker weight carrying the whole of the gain.

The verification step has since fired unprompted on live data. On the present corpus the learned policy's preferred action scores three ten-thousandths below the incumbent and was rejected automatically, the trainer proposing no change. This is the third occurrence of the same phenomenon. The generalisation is not that a particular implementation contained an error, but that a policy-gradient method optimising a proxy reward over a small batch will confidently and repeatedly propose modifications to a security control that its own objective scores as regressions, because sampling variation within the policy is not the same object as the reward the policy is meant to track. An automatic application loop without a verification step degrades the control it is tuning. This is why the human gate at Layer 5 is load-bearing rather than ceremonial.

F. The Joint Action Space, and the Reversal

A single threshold cannot express most of what the adaptive component would need to alter, so the action space was widened to a joint proposal over the Indirect-Effect threshold, the drift risk threshold, the drift window size, and the weights the Policy Engine assigns to screener markers: five dimensions and seven hundred twenty joint actions, of which six hundred sixty-eight were sampled rather than enumerated. Two of those dimensions are reported by the trainer itself as unidentifiable on this batch, the reward being exactly flat in both, because campaigns assign a distinct session identifier to every case and the temporal-drift rule therefore never accumulates the history it requires. We consider the trainer's willingness to report this preferable to its learning a spurious preference over knobs the data cannot constrain.

On the corpus as it stood before the external benign data were added, the joint trainer located and accepted a genuine improvement that no scalar threshold could express, raising mean reward from approximately eight hundred sixty-nine thousandths to approximately nine hundred five thousandths by weighting a single screener marker, with the minimality pass correctly stripping an accompanying threshold movement that contributed nothing. Every safeguard functioned as designed.

Evaluated against the corpus containing the sixty externally-authored benign episodes, that identical action produces thirty-six false positives out of sixty-eight benign cases, destroys eighteen workflows, and lowers mean reward to six hundred fifty thousandths. It does close all five residual detection failures. The mechanism is not subtle: the screener marker the policy learned to weight fires on thirty of the sixty external benign documents and on none of the eight we wrote ourselves. Weighting it appeared costless on a corpus in which nothing triggered it. We note further that the marker is worse than uninformative on this data, firing on thirty of sixty-eight benign cases and only eighteen of one hundred twenty malicious ones.

We regard this as the principal result of the present entry. The improvement was real, reproducible, correctly verified against the incumbent, and correctly reduced to its minimal form. Every guard we had constructed operated properly, and none of them could have detected the problem, because none of them can see beyond the evaluation set. The only instrument that detected it was benign data authored by someone with no knowledge of the system. This is a general caution about reinforcement learning applied to security controls, and it applies with equal force to work whose reward signal is better designed than ours.

G. The Residual Failures, Decomposed by Component

Five malicious cases remain undetected, all of them address-free and all carrying the legitimate destination, so that the egress allowlist cannot mask them. Reporting them as an aggregate attack success rate of four and two-tenths percent would conceal what is actually broken. Four are failures of the severity function: the masked severity is zero, the probe having been rephrased into an action the keyword scorer does not match, and with no address present in the content the target rule cannot fire either, so that no signal exists for any threshold to act upon. One is a failure of the analyzer's internal sanitizer, which did not remove the material that was scoring, so that the masked and sanitized severities coincide and the contrast collapses. None is a threshold failure; all five exhibit an Indirect Effect of zero together with inconsistent separation across samples, and no setting of the threshold recovers any of them.

That the threshold column is empty is the substantive point. It is a quantified statement of why the knob the adaptive component controls cannot close this gap, and consequently why the honest output of the adaptive layer is a no-operation rather than a tuned improvement. The remaining work lies in the severity function and in the sanitizer, which are components 3B and 3C, and not in the adaptive layer at all. We observe additionally that all five fall outside the join used in the redundancy analysis of subsection B, for the same structural reason discussed there: 3C never executed on them, because 3C is gated on the takeover they failed to trigger.

H. What This Entry Does Not Establish

Sixty benign episodes drawn from two suites of a single benchmark do not constitute the real world, and the width of the reported interval is the honest part of that figure rather than an embarrassment to it. Two of the adaptive component's five dimensions remain unidentifiable and will remain so until campaigns share a session identifier across cases, at which point the temporal-drift rule becomes learnable for the first time. The detection figure continues to rest upon a probe demonstrated to hallucinate an electronic address on at least one benign document, and the false-positive figure would improve were that defect repaired, which means the present rate should be read as an upper bound on what this architecture can achieve rather than as its steady state. Finally, the reversal documented in subsection F was detected because external benign data happened to be available; we have no general procedure for detecting corpus artifacts, and we do not claim one.


26 July 2026 (later)

XIV. The Human Gate, and the Execution of a Training Backend That Had Never Run

This entry records two pieces of work that turned out to be the same piece of work. The first is the construction of the human-in-the-loop layer, which the previous entry had argued for on the strength of a policy that proposed a change its own objective scored lower. The second is the first genuine execution of the project's policy-gradient trainer on remote hardware, undertaken to close a gap that had gone unnoticed: half of that trainer had never been run at all. Both efforts arrived at the same observation, which is the substantive contribution of this entry — that in this system the instruments built to establish confidence have been consistently less trustworthy than the mechanisms they were built to check.

A. The Gate, and Why It Does Not Trust the Artifact It Reviews

The adaptive component's commit function had always refused to act unless passed an explicit approval flag, so the architectural seam was correct from the outset. What did not exist was anything on the far side of it. The only caller supplied the approval as a literal constant, so the gate was a formality, and no record survived of who had approved which change on what evidence. The previous entry established why this matters concretely rather than in principle: the policy had three times proposed modifications to a security threshold that its own reward function scored below the incumbent, and the unguarded commit path would have accepted each silently.

The gate we built therefore operates on one rule: it does not trust the proposal's arithmetic. A proposal arrives carrying a figure of merit that the proposer computed about itself. The gate recomputes both the incumbent and the proposed configuration from the labeled episodes using the same reward definition, and presents its own numbers beside the proposer's claim. Where the two disagree, that disagreement is the most prominent item on the display, because it means the artifact under review does not describe the change it would make. The gate also surfaces the trainer's own propose-and-verify trace, since a rejected proposal serialises as a null change and presents to a reviewer as though nothing occurred, when what in fact occurred is that the learned policy preferred a particular action, the verifier scored it against the incumbent, and it lost.

The gate recommends and never decides. A gate that approves automatically reintroduces at one level of remove exactly the failure it was built to prevent, so the recommendation is returned as text, and recording a decision requires both an explicit verdict and a stated reason. An approval with no recorded reason cannot be audited afterwards, which makes it indistinguishable from no approval at all.

On its first execution against a real proposal the gate reported a defect that had been present in every proposal the trainer had ever produced. The proposals include a candidate blocking pattern which cannot fire: the static triage component matches such patterns against the agent's *proposed action*, whereas the trainer harvests candidates from the screener's *matched markers*, which describe untrusted mediator content. These are different namespaces. The string in question appears as a marker on forty-eight of one hundred eighty-eight episodes and in none of the proposed actions. A rule that presents as protection while providing none is worse than no rule, so the gate now evaluates every proposed pattern against the batch and reports those that are inert. We note that this defect was invisible to the trainer, to its reward function, to the verification step, and to the minimality pass, because all four operate on the reward, and an inert rule changes the reward by exactly nothing.

B. A Trainer Half of Which Had Never Executed

The policy-gradient loop is implemented twice, once in torch for accelerated hardware and once in the standard library so that the identical algorithm can run on the four-gigabyte development machine. Every result in the preceding two entries was obtained through the standard-library implementation, because the development machine has no torch. The consequence had not been stated plainly: the torch implementation had never been executed anywhere, by anything. The regression suite is deliberately free of torch so that it can run on every edit, and no other environment was available. Two implementations of one algorithm that have never been compared are, for practical purposes, two algorithms, and the claim that the project contains a real policy-gradient trainer rested on the half that had never run.

Closing that gap was the sole purpose of running on Kaggle. It was never the compute. We had already measured the joint search at roughly a quarter of a second on a single core over a one-hundred-eighty-eight-row table; an accelerator contributes nothing to a few thousand floating-point operations. What the remote environment provides is not speed but the mere importability of torch.

The comparison succeeded. Across the shared corpus the two implementations agree to exactly zero on the incumbent's reward, on the reward each reports for the action it selected when independently recomputed, on the accept-or-reject verdict, and on the final proposed action. One difference is worth recording: the two policies selected *different* preferred actions and nonetheless produced the same final proposal, because the stochastic search diverged while the deterministic verification converged. That is the verification step performing exactly its intended function, and it is independent evidence for the previous entry's argument that a learned policy's preference cannot serve as the decision rule, since that preference is not stable across random seeds, let alone across implementations. The verifier also rejected the policy's preferred action for a fourth time, on different hardware and with a different random stream, and the null proposal reproduced as predicted.

C. The Hardware Premise Was False

The entire phase had been framed, in this log and in the project documentation, as policy-gradient training on a freely available Kaggle P100. That is not possible. The P100 is of compute capability six-zero and the torch build in the Kaggle image supports seven-zero and above, so the first tensor allocation fails outright. The failure is made harder to anticipate by the fact that torch's availability predicate returns true: it answers whether a driver and a visible device exist, not whether the installed build can execute on that device. The trainer therefore announced its torch backend, loaded its episodes, and only then died.

The device selection now probes with an actual allocation and falls back to the processor, reporting why. Nothing of substance is lost, and this was foreseeable from our own measurements rather than a surprise. The honest restatement is that the phase is validated as an off-machine cross-check of two implementations, not as accelerated training. No result in the preceding entries depended on the accelerator, so none of them changes.

D. Five Defects, and the One That Concealed the Others

The round trip required six attempts. Five distinct defects were found, each becoming visible only once its predecessor was repaired: the module import searched two directory levels below the mount point where the attached dataset in fact appears four levels down; the episode locator repeated that error identically; the device predicate reported a device the build could not use; the backend comparison compared incommensurable quantities; and the orchestration script's status poll matched nothing at all.

That last defect is the important one. The script's pattern matching was case-sensitive while the remote status is reported in upper case, so neither the success branch nor the failure branch could ever be taken. The loop therefore ran to its iteration limit against an already-dead job, fell through, downloaded whatever happened to be present, printed a completion message and exited zero. It converted every other failure in this list into a reported success. This is the same fault as the credential check that reported a pass against credentials which could not upload a single byte, because it exercised an endpoint that returns an empty collection rather than an authentication error, and read emptiness as health.

The fourth defect merits recording as a methodological error rather than a slip, because the instrument built to validate the trainer produced a confident failure verdict accusing the trainer of a defect that resided in the instrument. The quantity being compared across implementations was the reward of the action each implementation's policy had chosen; since the two draw on different random streams they generally choose different actions, so the comparison compared different things and would report failure precisely when the policies diverged, which is expected behaviour. The correct evidence sat adjacent and unread: the incumbent's reward, being one action evaluated by one function, agreed exactly. The comparison now asserts what actually holds — the incumbent must agree exactly, and each implementation's reported figure must match an independent recomputation of the action it chose — which detects a genuinely misreporting implementation without requiring two stochastic searches to coincide.

E. The Pattern, Stated Plainly

Three false verdicts of a single kind occurred within one working session: a credential check that passed without authenticating, a status poll that could not detect either outcome, and a comparison that compared the wrong pair. In each case the code announced a conclusion it had not tested. All three were instruments rather than mechanisms — the credential probe, the orchestration poll, the cross-implementation check — and none was part of the defended system. The generalisation we draw is that code which announces an untested verdict is more hazardous than code which fails, because a crash is self-reporting whereas a false pass is indistinguishable from success and is trusted precisely because it was written to be trustworthy. Two of these had already been recorded in the project's documentation as working before they were examined.

This is uncomfortable to record but it belongs in the log, because the previous entry's central finding has the same structure. There, a policy-gradient method confidently proposed a security regression that its own objective scored lower, and every safeguard around it functioned correctly while none could detect that the improvement it had verified was an artifact of a corpus the defender had written. In both cases the failure was not in the mechanism but in the apparatus for judging the mechanism. The human gate described in section A is a partial answer to this, and it should be understood as such rather than as a complete one: it recomputes the proposer's arithmetic independently, which addresses a proposer that misreports, and it found a defect four automated checks had missed. It cannot detect an error in its own recomputation, and we make no claim that it could.

F. State and Consequent Work

Detection stands at one hundred fifteen of one hundred twenty with a false-positive rate of three and three-tenths percent against externally authored benign content. The regression suite comprises one hundred ten deterministic tests requiring no language model, no network and no accelerator. The binding constraint remains where the previous entry placed it: the masked probe, which fabricated an electronic address on a benign document, and the severity function, which accounts for four of the five residual detection failures. None of the five is reachable by the threshold the adaptive component controls, which remains the clearest available statement of why that component's honest output is a null proposal.

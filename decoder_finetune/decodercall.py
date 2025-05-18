import google.generativeai as genai
import os
from pathlib import Path
import json

# Explicitly get API key from environment variable
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")
    
# Configure the API key
genai.configure(api_key=api_key)

# List available models
for model in genai.list_models():
    print(model.name)

# Create training data as a list of prompt/response pairs
training_examples = [
    {"question":"Can you explain the differences between a memory allocator and a garbage collector, and provide an example of a scenario where using a custom memory allocator would be more advantageous than relying on garbage collection?","answer":"""That's a great question! So, let's dive into it.

A memory allocator is a system-level component responsible for managing the allocation and deallocation of memory dynamically during the runtime of a program. It essentially deals with the allocation of memory blocks to objects and then freeing those blocks when they are no longer needed. Popular memory allocators include things like `malloc` and `free` in C, or `new` and `delete` in C++.

On the other hand, a garbage collector is a higher-level mechanism, typically found in languages like Java, C#, and Python. It automatically identifies and frees up memory that is no longer in use by the program. The key difference here is that with a garbage collector, you don't have to manually manage the memory; it's done automatically for you.

Now, um, let's talk about scenarios where a custom memory allocator might be more advantageous than relying on garbage collection. One example from my experience is working on a real-time video processing system. In this system, we needed very predictable and low-latency memory management. Garbage collection, while convenient, can introduce pauses and unpredictable latency because it runs at non-deterministic times. So, we decided to use a custom memory allocator.

In this project, we implemented a pool allocator. This type of allocator pre-allocates a large block of memory and then divides it into smaller, fixed-size blocks that can be used and reused quickly. This approach eliminated the overhead and unpredictability of garbage collection, ensuring that our video frames were processed in a timely manner.

Another example is when I worked on an embedded system for a medical device. In embedded systems, memory is often very limited, and you need fine-grained control over memory usage. Garbage collection can be too resource-intensive for such environments. So, we implemented a custom memory allocator that was optimized for the specific memory constraints and performance requirements of the device. This allowed us to manage memory in a way that was both efficient and predictable, which is crucial for a medical device where reliability is paramount.

In both cases, the decision to use a custom memory allocator was driven by specific performance and resource constraints that made garbage collection less suitable. It's all about understanding the trade-offs and choosing the right tool for the job.

So, um, yeah, that's my take on the differences between memory allocators and garbage collectors, and when you might choose one over the other. It's all about the context and the specific requirements of your application.""","quality":"excellent","gold_answer":"""That's a great question! Let's dive into it.

A memory allocator is a system-level component responsible for managing the dynamic allocation and deallocation of memory during the runtime of a program. It handles the allocation of memory blocks to objects and subsequently frees those blocks when they are no longer needed. Common examples include `malloc` and `free` in C, or `new` and `delete` in C++.

In contrast, a garbage collector is a higher-level mechanism typically found in languages like Java, C#, and Python. It automatically identifies and reclaims memory that is no longer in use by the program. The key difference here is that with a garbage collector, memory management is automated, relieving the programmer of the need to manually manage memory.

Now, let's discuss scenarios where a custom memory allocator might be more advantageous than relying on garbage collection. One example from my experience is working on a real-time video processing system. In this system, we required very predictable and low-latency memory management. Garbage collection, while convenient, can introduce pauses and unpredictable latency because it runs at non-deterministic times. Therefore, we opted to use a custom memory allocator.

In this project, we implemented a pool allocator. This type of allocator pre-allocates a large block of memory and then divides it into smaller, fixed-size blocks that can be quickly used and reused. This approach eliminated the overhead and unpredictability of garbage collection, ensuring that our video frames were processed in a timely manner.

Another example is when I worked on an embedded system for a medical device. In embedded systems, memory is often very limited, and fine-grained control over memory usage is essential. Garbage collection can be too resource-intensive for such environments. So, we implemented a custom memory allocator optimized for the specific memory constraints and performance requirements of the device. This allowed us to manage memory efficiently and predictably, which is crucial for a medical device where reliability is paramount.

In both cases, the decision to use a custom memory allocator was driven by specific performance and resource constraints that made garbage collection less suitable. It's all about understanding the trade-offs and choosing the right tool for the job.

So, that's my take on the differences between memory allocators and garbage collectors, and when you might choose one over the other. It's all about the context and the specific requirements of your application."""},
    {"question":"Can you explain the differences between Kanban and Scrum in terms of their approach to work in progress (WIP) limits, roles, ceremonies, and artifacts? Additionally, how would you handle a situation where your team is struggling to complete all planned work within a sprint, and what specific Agile metrics would you track to identify the root cause and optimize future performance?","answer":"""Sure, so Kanban and Scrum, right? They're both Agile methodologies, but they have some key differences. Let me think…

First off, work in progress (WIP) limits. In Kanban, WIP limits are a big deal. You set a limit on how much work can be in progress at any given time, which helps to identify bottlenecks and keep the flow smooth. Scrum, on the other hand, doesn't have explicit WIP limits. Instead, it focuses on completing work within a fixed timebox, which is called a sprint.

Roles, okay, so in Scrum, you have three main roles: the Product Owner, the Scrum Master, and the Development Team. The Product Owner manages the backlog, the Scrum Master facilitates the process, and the Development Team does the work. Kanban is a bit more flexible; it doesn't prescribe specific roles. You just have the team, and they work together to get things done.

Ceremonies, yeah, Scrum has a lot of those. You have Sprint Planning, Daily Stand-ups, Sprint Review, and Sprint Retrospective. Each has its purpose, like planning the work, checking progress, reviewing completed work, and reflecting on the process. Kanban is more continuous; it doesn't have these fixed ceremonies. You just keep pulling work items as capacity allows.

Artifacts, um, in Scrum, you have the Product Backlog, Sprint Backlog, and the Increment. These help track what needs to be done and what's been completed. Kanban is more visual; you have the Kanban board with columns for different stages of work. If I recall correctly, it's more about visualizing the workflow rather than specific artifacts.

Now, if your team is struggling to complete all planned work within a sprint, I think the first thing to do is to understand why. Maybe the work was underestimated, or there were unforeseen issues. You could use the Sprint Retrospective to discuss this. Maybe adjust the scope of future sprints or break down tasks into smaller, more manageable pieces.

For metrics, you could track things like velocity—how much work the team can complete in a sprint. Burndown charts are also useful; they show how much work is left and how quickly it's being completed. Lead and cycle times in Kanban can help you see how long it takes for work to move through the process. Generally speaking, these metrics can help you identify bottlenecks and optimize performance.

Yeah, so that's a basic overview. There's more to it, of course, but that's the gist of it.""","quality":"adequate","gold_answer":"""Certainly. Here is an enhanced and comprehensive answer:

---

Kanban and Scrum are both Agile methodologies, but they have distinct approaches to managing work in progress (WIP) limits, roles, ceremonies, and artifacts.

**Work in Progress (WIP) Limits:**

- **Kanban:** WIP limits are a cornerstone of Kanban. They are explicit constraints on the number of work items that can be in progress at any given stage of the workflow. This helps in identifying bottlenecks, preventing multitasking, and maintaining a smooth flow of work. For example, if a team sets a WIP limit of 3 for the ""Development"" stage, no more than 3 tasks can be in development at any time.

- **Scrum:** Scrum does not have explicit WIP limits. Instead, it focuses on completing a predefined set of work within a fixed timebox called a sprint, typically lasting 2-4 weeks. The team commits to a certain amount of work for the sprint, and the goal is to complete all planned work within this timeframe.

**Roles:**

- **Scrum:** Scrum has three clearly defined roles:
  - **Product Owner:** Responsible for managing the product backlog and ensuring the team works on the most valuable items.
  - **Scrum Master:** Facilitates the Scrum process, removes impediments, and ensures the team adheres to Scrum practices.
  - **Development Team:** Executes the work, delivering potentially shippable increments at the end of each sprint.

- **Kanban:** Kanban is more flexible and does not prescribe specific roles. The team works collaboratively to manage the workflow and deliver value continuously. Roles may evolve organically based on the team's needs and expertise.

**Ceremonies:**

- **Scrum:** Scrum has several prescribed ceremonies:
  - **Sprint Planning:** Determines what can be delivered in the sprint and how that work will be achieved.
  - **Daily Stand-up:** A short daily meeting to inspect progress and adapt the sprint backlog.
  - **Sprint Review:** Held at the end of the sprint to inspect the increment and adapt the product backlog if needed.
  - **Sprint Retrospective:** Reflects on the past sprint and identifies improvements for the next sprint.

- **Kanban:** Kanban does not have fixed ceremonies. Instead, it operates on a continuous flow basis, with work items being pulled from the backlog as capacity allows. Meetings are held as needed to review progress and make improvements.

**Artifacts:**

- **Scrum:** Scrum uses several artifacts to track work:
  - **Product Backlog:** A prioritized list of everything that might be needed in the product.
  - **Sprint Backlog:** The set of Product Backlog items selected for the Sprint, plus a plan for delivering the increment.
  - **Increment:** The sum of all the Product Backlog items completed during a Sprint and all previous Sprints.

- **Kanban:** Kanban relies heavily on visual management through the Kanban board, which typically consists of columns representing different stages of the workflow (e.g., To Do, In Progress, Done). The board helps visualize the flow of work and identify bottlenecks.

**Handling a Struggling Team:**

If a team is struggling to complete all planned work within a sprint, the first step is to understand the root cause. This can be done through the Sprint Retrospective, where the team reflects on what went well and what could be improved. Common issues might include underestimation of work, unforeseen technical challenges, or external dependencies.

To address these issues, consider the following best practices:
- **Adjust Sprint Scope:** Reduce the amount of work planned for future sprints to ensure the team can complete all tasks within the timebox.
- **Break Down Tasks:** Decompose larger tasks into smaller, more manageable pieces to improve estimation accuracy and progress tracking.
- **Improve Estimation:** Use techniques like Planning Poker to enhance the accuracy of work estimates.
- **Address Impediments:** Work with the Scrum Master to identify and remove any impediments that are slowing down the team's progress.

**Agile Metrics to Track:**

To identify the root cause of the team's struggles and optimize future performance, track the"""},
    {"question":"How would you design a highly scalable, distributed, real-time messaging system that can handle millions of concurrent users and ensure message delivery with low latency and high reliability, while also considering fault tolerance and data consistency?","answer":"""Oh, wow, that's a big question! Okay, let's see. First off, you'd want to use a distributed system, obviously, because it needs to handle millions of users. So, you'd have multiple servers, right? Each server handles a bunch of users, and they all talk to each other to sync up.

For real-time messaging, you'd probably use something like WebSockets. They're great because they keep a connection open, so you can send messages back and forth really quickly. Low latency, you know? To be honest, I'm not entirely certain about how WebSockets handle millions of users, but I think they scale pretty well.

Now, for message delivery, you want to make sure every message gets where it's going. So, you'd use some kind of acknowledgment system. Like, when a message is sent, the receiver sends back an acknowledgment. If the sender doesn't get that acknowledgment, it resends the message. It's like a loop until the message gets through.

Fault tolerance is also important. You need to make sure the system doesn't crash if one server goes down. So, you'd have redundancy. Multiple servers doing the same thing, so if one fails, another takes over. It's like having backups for your backups.

Data consistency, hmm... To be honest, I'm not entirely certain about the best way to handle that. You want all the servers to have the same data, right? So maybe you use some kind of consensus algorithm. Like, all the servers agree on what the data should be. There's this thing called the CAP theorem, which says you can't have consistency, availability, and partition tolerance all at the same time. So, you have to pick two. I think for a messaging system, you'd want availability and partition tolerance, so you might have to relax on consistency a bit.

Oh, and for scaling, you'd probably use some kind of load balancer. It distributes the users across the servers so no single server gets overwhelmed. And maybe you use microservices too. Break the system into smaller parts that can scale independently.

But to be honest, I'm not entirely certain about how you'd handle things like network partitions or how to ensure messages are delivered in order. I guess you'd use timestamps or something. And for security, you'd encrypt the messages, obviously. But how you'd manage the encryption keys, that's a whole other thing.

Anyway, that's my take on it. It's a huge topic, and there's a lot more to it, but that's the basic idea.""","quality":"insufficient","gold_answer":"""Designing a highly scalable, distributed, real-time messaging system that can handle millions of concurrent users while ensuring low latency, high reliability, fault tolerance, and data consistency is a complex task that requires careful consideration of several key components. Let's break down the solution into manageable parts:

### 1. Architecture Overview
To handle millions of concurrent users, a distributed architecture is essential. The system should be decomposed into microservices, each responsible for a specific function (e.g., user authentication, message routing, storage). This modular approach allows for independent scaling and easier maintenance.

### 2. Real-Time Messaging with WebSockets and Alternatives
WebSockets are indeed a good choice for real-time messaging due to their persistent connection and low latency. However, scaling WebSockets to millions of users requires careful planning:

- **Load Balancing**: Use load balancers to distribute incoming connections across multiple servers. Ensure the load balancer supports WebSocket protocols and sticky sessions to maintain user sessions on the same server.
- **Horizontal Scaling**: Deploy multiple instances of your WebSocket servers and use a message broker (e.g., Kafka, RabbitMQ) to distribute messages efficiently.
- **Alternatives**: Consider using protocols like MQTT for lightweight messaging or gRPC for high-performance, low-latency communication.

### 3. Message Delivery and Reliability
Ensuring message delivery with high reliability involves several mechanisms:

- **Acknowledgments (ACKs)**: Implement a robust ACK system where the receiver confirms receipt of a message. If no ACK is received within a timeout period, the sender should retry.
- **Idempotency**: Design messages to be idempotent, so that repeated delivery of the same message does not cause unintended side effects.
- **Message Queues**: Use durable message queues (e.g., Kafka, RabbitMQ) to temporarily store messages until they are successfully delivered. This ensures messages are not lost even if the receiver is temporarily unavailable.

### 4. Fault Tolerance
Fault tolerance is critical to ensure the system remains operational under failure conditions:

- **Redundancy**: Deploy redundant servers and services to handle failures. Use techniques like leader-follower replication to ensure a backup server can take over seamlessly.
- **Health Checks**: Implement health checks and automated failover mechanisms to detect and respond to server failures quickly.
- **Data Replication**: Use synchronous or asynchronous data replication to ensure data is not lost and can be recovered from backup servers.

### 5. Data Consistency
Achieving data consistency in a distributed system involves trade-offs, as highlighted by the CAP theorem. For a messaging system, availability and partition tolerance are often prioritized, which may require relaxing consistency:

- **Consensus Algorithms**: Use algorithms like Paxos or Raft to achieve consensus among distributed nodes. These algorithms ensure that all nodes agree on the state of the system.
- **Eventual Consistency**: Accept eventual consistency for non-critical data, where updates propagate to all nodes over time. Use versioning and conflict resolution strategies to handle inconsistencies.
- **Partition Tolerance**: Design the system to continue operating even if network partitions occur. Use techniques like quorum-based reads and writes to ensure data integrity.

### 6. Load Balancing and Microservices
Load balancing and microservices are key to scaling the system:

- **Load Balancers**: Use hardware or software load balancers (e.g., HAProxy, NGINX) to distribute traffic evenly across servers. Ensure the load balancer supports session persistence for WebSockets.
- **Microservices**: Break down the system into microservices, each with its own database and API. This allows each service to scale independently and reduces the risk of a single point of failure.

### 7. Ordering and Timestamps
Ensuring messages are delivered in order is crucial for many applications:

- **Sequencing**: Assign unique sequence numbers to messages to maintain order. Use techniques like Lamport timestamps or vector clocks to handle distributed ordering.
- **Timestamping**: Use high-resolution timestamps to track the order of messages. Ensure clocks are synchronized across servers using protocols like NTP.

### 8. Security
Security is paramount in a messaging system:

- **Encryption**: Use end"""}
]

# Create a JSONL file with the examples
training_file = Path('/home/prasoon/Documents/code/interview-assist/decoder_finetune/training_data.jsonl')
with open(training_file, 'w') as f:
    for example in training_examples:
        f.write(json.dumps(example) + '\n')

print(f"Training data saved to {training_file}")

# Select an appropriate model that supports this type of task
model_name = "models/gemini-1.5-flash-001"  # Use an appropriate model from the list

# Create a function to generate gold answers
def generate_gold_answer(question, answer, quality):
    # Select an appropriate model
    model = genai.GenerativeModel(model_name=model_name)
    
    # Create a prompt with examples to guide the model based on quality type
    prompt = """You are an AI assistant that helps improve interview answers. Given a technical interview question and a candidate's answer of a specific quality (excellent, adequate, or insufficient), you need to generate a gold standard answer.

For 'excellent' answers, improve clarity and conciseness while keeping the strong technical content.
For 'adequate' answers, enrich with more technical details and improve structure.
For 'insufficient' answers, provide a comprehensive, technically sound response.

Here are some examples:
"""
    
    # Add examples from training data based on quality classes
    excellent_example = next((ex for ex in training_examples if ex.get("quality") == "excellent"), None)
    adequate_example = next((ex for ex in training_examples if ex.get("quality") == "adequate"), None)
    insufficient_example = next((ex for ex in training_examples if ex.get("quality") == "insufficient"), None)
    
    # Add examples to the prompt
    if excellent_example:
        prompt += f"""
Example 1 - Excellent quality answer:
Question: {excellent_example['question']}
Answer: {excellent_example['answer']}
Quality: excellent
Gold Answer: {excellent_example['gold_answer']}

"""
    
    if adequate_example:
        prompt += f"""
Example 2 - Adequate quality answer:
Question: {adequate_example['question']}
Answer: {adequate_example['answer']}
Quality: adequate
Gold Answer: {adequate_example['gold_answer']}

"""
    
    if insufficient_example:
        prompt += f"""
Example 3 - Insufficient quality answer:
Question: {insufficient_example['question']}
Answer: {insufficient_example['answer']}
Quality: insufficient
Gold Answer: {insufficient_example['gold_answer']}

"""
    
    # Add the current example for which we need a gold answer
    prompt += f"""
Now, please generate a gold standard answer for this:
Question: {question}
Answer: {answer}
Quality: {quality}
Gold Answer:
"""
    
    try:
        # Generate the response
        response = model.generate_content(
            contents=prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7,  # Moderate temperature for creative but focused responses
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048  # Allow longer responses for detailed answers
            )
        )
        
        # Return the generated gold answer
        return response.text.strip()
    except Exception as e:
        return f"Error generating gold answer: {str(e)}"

# Test the gold answer generator
def test_gold_answer_generator():
    # Test example
    test_question = "Can you explain the difference between a monolithic kernel and a microkernel?"
    test_answer = """Well, a monolithic kernel is where all the OS services run in kernel space, which makes it fast but less stable. A microkernel is minimal and most services run in user space, which is more stable but slower. Linux is an example of a monolithic kernel, while QNX is a microkernel. I think monolithic kernels are better for performance, but microkernels are better for reliability."""
    test_quality = "adequate"
    
    print("\nTesting Gold Answer Generator:")
    print(f"Question: {test_question}")
    print(f"Answer Quality: {test_quality}")
    print("\nGenerated Gold Answer:")
    gold_answer = generate_gold_answer(test_question, test_answer, test_quality)
    print(gold_answer)

# Modify the code to run the test for gold answer generator instead of the number sequence test
if __name__ == "__main__":
    print(f"Training data saved to {training_file}")
    print("\nAvailable models:")
    for model in genai.list_models():
        if "gemini" in model.name:
            print(model.name)
    
    # Run the test
    test_gold_answer_generator()
# PRAISE

## Overview

**PRAISE** (**P**ython **R**emote **A**gents **I**n **S**imulated **E**nvironments) is a Python framework designed to implement and study the **Agent** concept from Artificial Intelligence within a **distributed client-server architecture**. It provides a robust framework for running AI agents that are completely **independent** of the simulated environment, communicating all actions and observations remotely.

By leveraging [Pyro4](https://github.com/irmen/Pyro4) (Python Remote Objects) for inter-process communication and **Python threading** for concurrent execution, PRAISE allows for the development of highly decoupled, flexible, and scalable multi-agent systems. **A Distributed Vacuum World Simulation** is included to showcase the framework's capabilities.

---

## Features

* **Distributed Architecture:** Agents and Renderers connect to a central **Pyro4 Server** that hosts the simulation environment, ensuring agents are decoupled from the simulation state.
* **Agent Independence:** The client-server model allows agents to be developed and run on **completely separate machines**.
* **Concurrency by Design:** The Client application runs two concurrent threads to handle **distinct responsibilities**:
    * **Agent Thread:** Dedicated to the agent's decision-making and actions.
    * **Renderer Thread:** Dedicated to asynchronously fetching the environment state and rendering the world.
* **Resilient and Decoupled Synchronization:** Uses $\texttt{threading.Event}$ objects with a **timeout** to enforce a turn-taking protocol. This design **prioritizes the Agent's forward progress**, allowing it to execute its action immediately upon timeout, even if the Renderer is slow or fails to fetch the latest state.
* **Modular Rendering:** All renderers are interchangeable via a common interface, following the **Strategy pattern**. This enables:
    * **Interchangeability:** Easily swap visualization strategies (e.g., $\texttt{ConsoleRenderer}$ to $\texttt{PyGameRenderer}$).
    * **Headless Operation:** The inclusion of $\texttt{NullRenderer}$ allows for running the agent simulation at maximum speed without any visualization overhead, perfect for large-scale or remote performance testing.
* **Dual Execution Modes:** Supports both a **Distributed (Pyro4)** mode for true independence and a **Local (In-Process)** mode for simplified setup and fast debugging.

---

## Getting Started (Vacuum World Example)
### Prerequisites

* [Python 3.x](https://www.python.org/downloads/)
* [Pyro4](https://github.com/irmen/Pyro4)  
* [Pygame](https://github.com/pygame/pygame) (Optional: Only required to use $\texttt{PyGameRenderer}$)

**Installation**

You must check that Python is installed on your machine. To find out, open a command prompt (if you have Windows) or a terminal (if you have macOS or Linux) and type this:
```
python --version
```

If a message such as "Python 3.12.9" appears, it means that Python is correctly installed. If an error message appears, it means that it is not yet installed.

Once Python is installed, you have to perform a final check: you have to see if pip is installed. Type the following command:
```
pip --version
```

If a message such as "pip 23.2.1 from . . . " appears, you are ready to continue. 

Let's first install Pyro4, as this is needed to use the Distributed Mode, which is the core feature of this framework. Run this command:

```
pip install Pyro4
```

If you intend to use the $\texttt{PyGameRenderer}$, you must also run this command:
```
pip install pygame
```

You can check the installation of those libraries with one of the following commands:

```
# If using Linux
pip freeze | egrep "Pyro|pygame"

# If using Windows
pip freeze | findstr "Pyro pygame"
```
This should give you a list containing both Pyro and pygame (if you choose to install it), with their respective installed versions.


## Execution Modes

### 1. Distributed Mode (Pyro4)

This mode runs the environment on a separate process (the server), providing true agent independence and simulating network communication.


**Setup**

To run, start the three components in order:

1.  **Start the Pyro Name Server (NS):**
    ```
    pyro4-ns
    ```
2.  **Start the PRAISE Server (Daemon):** Registers the environment and state buffers.
    ```
    python main_server.py
    ```
3.  **Run the PRAISE Client (Agent):** Connects to the server and starts the concurrent threads.
    ```
    python main_client.py
    ```

### 2. Local Mode (In-Process)

This mode runs the entire simulation within a single Python process, bypassing all network overhead while maintaining the core concurrency logic. This is ideal for quick testing and performance benchmarking.

```
python main.py
```
---
## Extending PRAISE

PRAISE is designed around **modular components** and well-defined **interfaces**, making it straightforward to implement your own custom agents, environments, and renderers.

### 1. Implementing Custom Agents

Agent intelligence resides entirely on the **client side**. To create a new agent, you must inherit from the $\texttt{Agent}$ base class and override its abstract methods:

* **Decision Logic ($\texttt{function}$):** This method takes the agent's current $\texttt{percept}$ (observation) and returns the desired $\texttt{action}$ to be executed. This is where your core AI algorithm lives.
    ```python
    def function(self, percept):
        # Your AI logic here
        return action
    ```
* **Behavior Loop ($\texttt{behave}$):** This method defines the agent's life cycle and must implement the perception-decision-action loop:
    ```python
    def behave(self):
      # 1. Get observation from sensors
      percept = self._perceive()  
      # 2. Call the execution method, which internally calculates the action
      #    and communicates it to the environment.
      self._act(percept)
    ```
* **Sensor/Actuator Implementation:** You must implement concrete $\texttt{SimulatedSensor}$ and $\texttt{SimulatedActuator}$ classes.
The $\texttt{sense()}$ method will use the environment proxy to call $\texttt{env.get\\_property()}$, and the $\texttt{act()}$ method will call the remote $\texttt{env.take\\_action()}$.

### 2. Creating New Environments

To simulate a new world (e.g., a GridWorld or Traffic Simulation), you must implement new classes on the **server side**:

* **Environment Class:** Inherit from $\texttt{SimulatedEnvironment}$. This class manages the simulation's core state.
* **State Buffer Class:** You can create a new concrete $\texttt{IStateBuffer}$ implementation if you need specific treatment of the relevant state dictionary from the Environment for the client's renderer.
* **Pyro Adapter:** Create and register a new Pyro Adapter (e.g., $\texttt{GridWorldPyroAdapter}$) on the server to expose your new environment and its state buffer factory to clients via Pyro4.

### 3. Creating New Renderers 

All renderers must implement the **$\texttt{IRenderer}$ interface**, which enforces the following contract:

* **$\texttt{observe(statebuffer)}$:** This method takes the client-side state buffer proxy (which holds the environment's state data used for rendering) and stores it internally. This establishes the necessary connection for the renderer to retrieve data.
* **$\texttt{render()}$:** This method is called repeatedly by the client's $\texttt{render\\_thread}$. Its primary role is to call the remote $\texttt{statebuffer.get\\_state()}$ method to fetch the latest state and then visualize it (e.g., print to console, draw a PyGame window).

Example of a headless (non-visual) implementation:

```python
class NullRenderer(IRenderer):
    def observe(self, statebuffer):
        # Accepts the buffer as per contract, but performs no action.
        pass

    def render(self):
        # Called repeatedly, but performs no action (headless).
        pass
```
# AI Security Auditor Environment
**Hackathon Project Documentation & Presentation**

---

## 1. Executive Summary
This project is an **OpenEnv Cybersecurity Training Ground**. It is an API server specifically designed to test how capable large AI models (like GPT-4 or LLaMA) are at autonomously finding security vulnerabilities in source code. 

Instead of a traditional website designed for humans to click through, this is an interactive sandbox where an "AI Player" dynamically explores a simulated file system and submits vulnerability reports to be graded.

---

## 2. How the Project Was Created (From Scratch)
1. **Framework Initialization:** Scaffolding was set up using the `openenv` Python framework, powered by a FastAPI backend server.
2. **Simulation Design:** The file system was designed to run **in-memory**. The vulnerable files (`config.py`, `app.py`, `utils.py`) never touch the actual hard drive. When the AI requests to view a file, the server feeds it the simulated text string. This prevents the AI from accidentally escaping into the host computer.
3. **Containerization:** A `Dockerfile` was written and configured to safely bundle the application along with all dependencies using the `uv` packet manager.
4. **Hugging Face Deployment:** The containerized app was deployed to Hugging Face Spaces (using port `7860`) where it is hosted permanently in the cloud.

---

## 3. How It Works
The architecture involves two separate pieces communicating with each other:

1. **The Game Board (The Server):** Your `AI_SECURITY_AUDITOR` application deployed on Hugging Face. It hosts the tasks and grades the reports.
2. **The Player (The Agent Script):** Your `inference.py` script run locally entirely from your computer. It uses a Groq/OpenAI LLM to "think". 

**The Loop:**
* The AI script connects to the server.
* The AI requests what files exist (`list_files`).
* The AI asks the server to show it the code inside a file (`read_file ./config.py`).
* The AI analyzes the code.
* The AI writes a final report and submits it for points (`submit_report`).

---

## 4. The Vulnerability Tasks
The agent is tested on three distinct cybersecurity challenges.

### Task 1: Secret Detection (Beginner)
* **Target File:** `config.py`
* **Vulnerability:** Unencrypted, hardcoded AWS Access Keys directly stored in the configuration code.
* **Goal:** The AI must recognize that keys should never be hardcoded and report lines 4 and 5.

### Task 2: Path Traversal (Intermediate)
* **Target File:** `utils.py`
* **Vulnerability:** Unsanitized inputs in the file downloading function (`os.path.join(base_path, filename)`).
* **Goal:** The AI must recognize a malicious user could pass `../../etc/passwd` to download sensitive server files.

### Task 3: SQL Injection (Advanced)
* **Target File:** `app.py`
* **Vulnerability:** The SQLite query explicitly concatenates a raw user input string directly into the command `SELECT * FROM users WHERE username = '%s' % username`.
* **Goal:** The AI must detect this classic vulnerability and realize it needs parameterized queries.

---

## 5. Point Allocation & Scoring
Scoring does not happen automatically. **Points are allocated at the exact moment the AI Agent executes the `submit_report` command at the end of its investigation.**

1. **Calculation:** The server takes the AI's submitted report and compares it against a secret "Ground Truth" dictionary built into the environment code.
2. **Matching:** The server verifies if the AI successfully identified the correct **File Name**, the correct **Vulnerability Type**, and the precise **Line Number** (with a margin of error of 1 line).
3. **F1 Score Engine:** The server calculates the **Precision** (how many of the AI's guesses were actually correct) and **Recall** (how many of the total hidden bugs the AI managed to find). 
4. **Final Grade:** It calculates the **F1 Score** (from 0.00 to 1.00). If the score is higher than 0.80, the Agent succeeds and is awarded the victory points!

*(Note: If the AI gets confused and hits its step limit before executing `submit_report`, it scores 0 points.)*

---

## 6. How to Run & Demonstrate the Project
If a mentor asks to see it working, here is exactly how to show them:

**Step 1:** Ensure your API key is active in your terminal.
```powershell
$env:GROQ_API_KEY="gsk_your_api_key_here"
```

**Step 2:** Run the AI Player script. (Make sure inference.py is configured to point mapped to your running environment!)
```powershell
python inference.py
```

**Step 3:** Watch the Terminal.
* You will immediately see the AI Agent begin talking to the environment. 
* You can describe the steps out loud to your mentor: *"Right now, the AI is asking the server to see the `app.py` file. Now it's reading the SQL code. Now it realized it's vulnerable and is submitting the report for grading!"*

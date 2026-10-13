# Luodi · eric-agent-luodi-skill

**Help FDEs turn a customer's Agent request into a delivery people can verify and take over.**

[中文](README.md) · For field engineers, implementation consultants and customer delivery teams · [Apache-2.0](LICENSE)

Start with the first job the customer needs done. Luodi helps define the output, choose the environment, preserve customer settings, plan acceptance and leave a clear handoff. Windows and Mac share a preparation checklist; the bundled executor runs synthetic examples inside a Windows project sandbox.

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="assets/readme/hero-zh.png">
  <img src="assets/readme/hero-zh.gif" width="100%" alt="Blue Luodi workflow illustration: define the task, choose the environment, prepare rules and Skills, verify the result and hand over.">
</picture>

[24-second introduction, Chinese](docs/watch.html) · [Checklist, Chinese](docs/installation-checklist.md) · [Execution scope](docs/support-matrix.md)

## Start in three steps

**1. Ask your Codex to install the Skill:**

```text
Install this Skill after reviewing its source:
https://github.com/NewenergyEric/eric-agent-luodi-skill/tree/main/.agents/skills/eric-agent-luodi-skill
Install the complete Skill directory. If an older version exists, compare it first and preserve my work records.
```

**2. Describe the first customer outcome:**

```text
$eric-agent-luodi-skill Plan an OpenClaw setup for a customer's Mac.
The first task is turning meeting notes into actions with owners and deadlines.
Give me the delivery steps, completion criteria and customer decisions.
Start with planning and preserve the existing environment and settings.
```

**3. Continue from the current step.** Provide only missing information that affects the next action. Later, ask to check progress or update one Skill while preserving customer choices.

The standalone Skill can produce a delivery plan and acceptance checklist without this full repository or a webpage. Running the bundled configuration example needs the complete repository and Windows + Python 3.12+. Actual customer installations and remote connections remain outside the executor's scope.

## Choose the request that fits

| Your situation | Ask for | Result |
|---|---|---|
| New customer | A delivery plan for one useful task | Scope, choices and completion criteria |
| Taking over ongoing work | Check the current state first | Evidence, missing items and the next action |
| Changing rules or Skills | Review the difference and preserve overrides | Change scope, acceptance and recovery steps |

The route is dependencies → network → Codex/IDE as needed → daily Agent → work rules → Skills → task and handoff. OpenClaw is the default; Hermes or an existing Agent can be selected. Check installation, actual loading and task output separately.

[Meeting-note input](examples/first-task/meeting-notes.md) → [Action-list example](examples/first-task/action-list.md). Check owners, deadlines and clearly identified missing information, then make sure the customer can continue independently.

For helping family or friends with a personal computer, use [Dahao](https://github.com/NewenergyEric/eric-dahao-agent-skill), including its separate connection workflow.

<details>
<summary>Existing installations and other Agents</summary>

The old identifier was `luodi`. Install `eric-agent-luodi-skill`, confirm it is discoverable, then remove only the confirmed old Skill directory if needed. Customer instances and receipts keep their existing paths. Select the Skill again in the next conversation turn if the list needs refreshing.

Other Agent Skills-compatible tools can install the complete folder through their documented mechanism. Terminal/file access is needed for execution; a chat-only tool can help work through the checklist.

</details>

<details>
<summary>Developer example and checks</summary>

From the complete project on Windows + Python 3.12+, with no additional Python dependencies:

```powershell
python -B demo.py
python -B -m unittest discover -s tests -v
python -B tools/release.py check
```

The example exercises installation, repeat execution, upgrades, override preservation and interrupted-write recovery. User commands remain `configure / check / update`; `--brief` is read-only guidance.

[Workflow](docs/workflow.md) · [Installation evidence](docs/installation-verification.json) · [Standalone Skill checks](docs/skill-install-verification.json) · [Validation](docs/validation.md) · [Media source](motion/README.md)

</details>

[Optional HTML checklist](docs/getting-started.html) · [Editorial references](docs/skill-usage.md) · [Security](docs/security.md) · [Third-party notices](THIRD_PARTY_NOTICES.md)

Original content: [Apache-2.0](LICENSE), Copyright 2026 NewenergyEric and contributors. The blue Luodi brand and existing media remain in place.

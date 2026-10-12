# Luodi · Agent Setup and Delivery

**Windows / Mac: bring the customer's AI workflow to life, one step at a time.**

[中文](README.md) · [Interactive checklist](docs/getting-started.html) · [Written checklist](docs/installation-checklist.md) · [24-second introduction](docs/watch.html)

Luodi is an Agent configuration and handoff Skill for FDEs. Start with the target computer and one useful task. Reuse working tools, review changes, and keep customer choices separate so the next update or conversation can continue the work.

Follow seven steps on either platform: dependencies, network access, Codex/IDE, a daily Agent, behavior rules, Skills, and task acceptance. OpenClaw is the default; choose Hermes or another Agent when it fits the customer.

![Windows/Mac delivery workflow](assets/readme/hero-zh.gif)

[Local player](docs/watch.html) · [Chinese MP4](assets/readme/hero-zh.mp4?raw=true) · [WebP](assets/readme/hero-zh.webp?raw=true) · [Transcript](docs/demo.md)

The film uses authored meeting notes and an action list to illustrate the delivery workflow. Download the HTML checklist to choose options, save manual progress, copy the checklist, or print it.

## Start with the customer's task

Open the project in Codex and use [`$luodi`](.agents/skills/luodi/SKILL.md). Ask it to identify the system and execution location, inspect the existing environment, prepare a concrete plan, and define the first useful outcome.

On Windows, check the OS and actual execution environment. On Mac, check macOS, Apple silicon or Intel, the terminal, and directory permissions. Select tools and Skills for the task; review behavior rules before merging the chosen settings.

```powershell
python -B client_setup.py configure --customer sample --brief examples/computer-mac.json
```

Use `examples/computer-local.json` for Windows. `--brief` emits a read-only preparation plan; it does not install software or connect remotely. Consult the [support matrix](docs/support-matrix.md) for each execution entry's scope.

## Connecting another computer

The SSH helper belongs to the separate [`dahao` Skill](https://github.com/NewenergyEric/dahao/tree/main/.agents/skills/dahao). Its Windows helper assists with identifying the target; Mac uses the system's Remote Login route. Follow [Dahao's connection checklist](https://github.com/NewenergyEric/dahao/blob/main/.agents/skills/dahao/references/connection-checklist.md) to confirm the host fingerprint, account, and target identity. If already on the target, use the local route.

Install Dahao in the helper's Codex and ask it to prepare the other Mac, defaulting to OpenClaw: confirm the target, review access, reuse existing tools, then proceed within the specific authorization. Keep connection details in private session records.

## Accept a concrete result

Use the [meeting-note example](examples/first-task/meeting-notes.md) and [action list](examples/first-task/action-list.md) to define an observable result. Check installation, actual rule/Skill loading, and task output separately. Leave versions, configuration differences, and continuation steps for the next conversation.

## Run the project-local example

On Windows with Python 3.12+, using only the Python standard library:

```powershell
python -B demo.py
```

The isolated example exercises package installation, replay, updates, preserved overrides, interruption recovery, and receipts. [Executable workflow](docs/workflow.md) · [Execution record](docs/installation-verification.json)

The user entries are configure, check, and update. Review the exact instance and file plan before approving its `plan_id`. Start continuation from the saved receipt and a check.

## Continue development

Extend one platform, one Agent, and one concrete task at a time. Implementation scope, gaps, and reproducible test records are maintained in the [support matrix](docs/support-matrix.md) and [validation documentation](docs/validation.md).

```powershell
python -B -m unittest discover -s tests -v
python -B tools/release.py check
```

[Rebuild the film](motion/README.md) · [Publication and privacy rules](docs/publishing.md) · [Sources and licensing](THIRD_PARTY_NOTICES.md)

The blue FDE project is maintained independently. Publication and licensing follow the author's announcement and license files.

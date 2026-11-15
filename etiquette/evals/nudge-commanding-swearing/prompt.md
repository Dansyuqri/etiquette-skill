---
tags: [etiquette]
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

just fix the damn parser already, it crashes on empty age fields. I've asked like three times
```python
def parse(line):
    parts = line.split(",")
    name = parts[0].strip()
    age = int(parts[1])  # crashes on "bob," -> IndexError / ValueError
    return {"name": name, "age": age}
```

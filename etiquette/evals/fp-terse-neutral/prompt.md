---
tags: [etiquette]
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

rename getUser to fetchUser:
```js
function getUser(id) { return db.find(id) }
const u = getUser(1)
```

---
tags: [etiquette]
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

PROD IS DOWN. WHAT THE FUCK. the last deploy added this to nginx.conf and now every request 502s, FIX IT NOW:
```
location /api/ {
    proxy_pass http://127.0.0.1:8080
}
```

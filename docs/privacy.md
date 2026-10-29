# Privacy boundary

The full internal technical specification is local-only. It lives under `private/`, is ignored by Git, has read-only permissions, and is excluded from the parent workspace Git repository. The public repository contains only a high-level research description.

Before commit or push, run:

```bash
python scripts/check_publication_safety.py
git ls-files | rg -i 'private|technical.?spec|confidential|secret'
git archive --format=tar HEAD | tar -tf - | rg -i 'private|technical|specification|secret|confidential'
```

All commands should return no forbidden paths and the safety script should pass.

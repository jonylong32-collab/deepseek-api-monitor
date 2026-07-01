# Contributing

Thanks for improving DeepSeek API Monitor.

## Development Checks

Before opening a pull request, run:

```bash
cd backend
python verify.py

cd ../frontend
npm run build
```

## Guidelines

- Keep API keys and `.env` files out of Git.
- Do not commit `node_modules/`, `dist/`, WebView profiles, logs, or local assistant artifacts.
- Keep frontend changes in `frontend/` and backend changes in `backend/` unless a cross-cutting change is intentional.
- Include a short explanation of user impact in pull requests.

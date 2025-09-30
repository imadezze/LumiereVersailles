# Frontend Configuration

## Backend API URL Configuration

The frontend can connect to different backend URLs using environment variables.

### Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set your backend URL:
   ```bash
   # For local development
   VITE_API_BASE_URL=http://localhost:8000

   # For ngrok tunnel
   VITE_API_BASE_URL=https://hackversailles-11-sudo.ngrok.app

   # For production
   VITE_API_BASE_URL=https://your-production-domain.com
   ```

3. Restart the development server for changes to take effect:
   ```bash
   npm run dev
   ```

### Important Notes

- Environment variables in Vite must be prefixed with `VITE_` to be exposed to the client
- Changes to `.env` require restarting the dev server
- The `.env` file is in `.gitignore` and should never be committed
- Use `.env.example` as a template for other developers

### Current Configuration

The frontend is currently configured to connect to:
```
https://hackversailles-11-sudo.ngrok.app
```

To switch back to localhost:
```bash
VITE_API_BASE_URL=http://localhost:8000
```
# Previa

Risk assessment platform aligned with the Typhoon repository shape while keeping the current Node.js and TypeScript stack.

## Arborescence

```text
dashboard/
├── backend/
│   ├── agent_graph/   # graph-based orchestration building blocks
│   ├── agents/        # recommendation and merge scripts
│   ├── api/           # Hono entrypoint, routes, middleware
│   ├── config/        # environment and CORS configuration
│   ├── data/          # raw inputs, processed outputs, lookup data
│   ├── database/      # Drizzle client, schema, seed
│   ├── models/        # shared domain and API contracts
│   └── services/      # scoring, provider adapters, orchestration
├── frontend/
│   ├── src/
│   │   ├── api/               # frontend API clients
│   │   ├── risk-assessment/   # scoring and assessment UI logic
│   │   ├── views/             # route-level screens
│   │   ├── context.ts         # cross-view navigation context
│   │   ├── data.ts            # local demo/store helpers
│   │   ├── house3d.ts         # 3D building interaction logic
│   │   ├── main.ts            # app bootstrap
│   │   └── router.ts          # navigation and panel switching
│   ├── index.html
│   └── vite.config.ts
├── scripts/          # utility scripts
├── .env.example
├── package.json
└── tsconfig.base.json
```

## Architecture

- `backend/` follows the Typhoon-style backend split: API, services, agents, orchestration, data, and models are clearly separated.
- `frontend/` keeps the Vite app isolated with screen modules in `views/` and shared assessment logic in `risk-assessment/`.
- `scripts/` remains reserved for one-off utilities so the application code stays inside `backend/` and `frontend/`.

## Run

### Install

```bash
npm install
cd backend && npm install
cd ../frontend && npm install
```

### Development

```bash
npm run dev:back
npm run dev:front
```

### Build

```bash
npm run build:back
npm run build:front
```

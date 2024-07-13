# Frontend


### Installation

Change `VITE_API_URL` for backend in `.env` file. Default value is `VITE_API_URL=http://0.0.0.0:8000`

Using your favourite package manager install dependencies and start development server.
```bash
cd frontend/unspoken

bun/npm/yarn install
bun/npm/yarn run dev
```


# Backend

### Generate migration

Alembic:
```bash 
alembic revision --autogenerate -m "Commit message"
alembic upgrade head
```

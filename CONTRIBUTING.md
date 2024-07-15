# Contacts
If you have any questions or suggestions, you can contact me via [telegram](https://t.me/nuclearthinking) 

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

### Before submitting pull-request please execute following commands
1. `isort .` - sort imports
2. `ruff format .` - format code 
3. `ruff check . --fix` - check linter and fix what fixable


## Generate database migration
```bash 
alembic revision --autogenerate -m "Commit message"
alembic upgrade head
```
## Running docker compose in development mode 
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yaml watch
```
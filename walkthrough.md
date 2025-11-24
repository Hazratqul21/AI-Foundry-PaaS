# Foundation Phase Walkthrough

## Completed Tasks
- **Backend Setup**: FastAPI app initialized with Database and Authentication.
- **Frontend Setup**: Next.js app initialized with TailwindCSS and Dashboard layout.
- **Module Integration**: Basic structure for BankCall and Anti-Fraud modules created.

## Verification Steps

### 1. Backend Verification
Run the backend server:
```bash
cd backend
uvicorn app.main:app --reload
```
- Check `http://localhost:8000/docs` for Swagger UI.
- Verify `/auth/login` and `/auth/register` endpoints.
- Verify `/api/antifraud/transactions/submit` endpoint.
- Verify `/api/bankcall/calls/initiate` endpoint.

### 2. Frontend Verification
Run the frontend server:
```bash
cd frontend
npm run dev
```
- Open `http://localhost:3000`.
- Verify the Dashboard layout with "Total Revenue", "Active Users" cards.
- Verify links to "BankCall AI" and "Anti-Fraud AI".

### 3. PaaS Features Verification
- **API Keys**:
    - Go to `http://localhost:8000/docs`.
    - Authorize using JWT (login first).
    - Use `POST /api/keys/` to create a key.
    - Use the key in `X-API-Key` header to call `/api/antifraud/transactions/submit`.
- **Webhooks**:
    - Use `POST /api/webhooks/` to subscribe to `transaction.blocked`.
    - Trigger a blocked transaction (amount > 10000).
    - Verify the event is created in `webhook_events` table.
- **Developer Portal**:
    - Go to `http://localhost:3000/developer`.
    - Check "API Keys" and "Webhooks" pages.

### 4. Refinement Verification
- **Security**:
    - Create a new API Key.
    - Check database: `sqlite3 backend/sql_app.db "SELECT key_hash, prefix FROM api_keys;"`
    - Verify that `key_hash` is hashed and `prefix` matches the first 8 chars of the key you saw.
- **Frontend Integration**:
    - Go to `http://localhost:3000/developer/keys`.
    - Click "Generate New Key".
    - Verify the key appears in the list (masked) and the full key is shown in the alert.
    - Refresh the page to verify data persistence.

### 5. Project Review Fixes Verification
- **Circular Import**:
    - Run `uvicorn backend.app.main:app --reload` and ensure no `ImportError`.
- **Webhook Secret**:
    - Create a webhook: `POST /api/webhooks/`. Verify `secret` is returned.
    - List webhooks: `GET /api/webhooks/`. Verify `secret` is **NOT** returned.
- **Async Dispatch**:
    - Trigger a webhook event.
    - Check server logs. You should see the response handling happen in the background (or at least not block the response immediately if you add a sleep in the dispatcher for testing).
- **Mutable Default**:
    - Check `backend/app/models.py` to ensure `default=list` is used for `Organization.modules`.

## Next Steps
- Implement detailed logic for BankCall scenarios.
- Implement real Authentication flow on Frontend (Login page).
- Deploy to staging.

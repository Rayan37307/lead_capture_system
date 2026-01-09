  The Big Picture: One Token, One Tenant

  The entire system is built on one core principle: A user's access token securely locks
  them into their specific tenant. They can never see or modify data from another tenant.

  Here’s how it works, step-by-step:

  ---

  Part 1: Getting the Access Token (Authentication)

  This is the process of proving who you are.

   1. Registration (`POST /auth/register`):
       * You provide your email, password, and a tenant_id.
       * The system creates a user and saves them inside the specific database for that
         tenant (e.g., in the tenant_data/YOUR_TENANT_ID.db file). The user is now
         permanently linked to that tenant.

   2. Login (`POST /auth/token`):
       * You provide the same email, password, and tenant_id.
       * The system looks for your email only within the database file matching the
         tenant_id you provided.
       * If your credentials are correct for that specific tenant, the server generates a
         JWT Access Token.

  ---

  Part 2: What is the Access Token?

  The access token isn't just a random string. It's a JSON Web Token (JWT), which is like a
  secure, tamper-proof ID card. If you were to decode the token you received, its content
  (the "payload") would look like this:

   1 {
   2   "sub": "user@example.com",      // The user's identity
   3   "tenant_id": "YOUR_TENANT_ID",  // The tenant this token is locked to
   4   "exp": 1736459340               // An expiration timestamp
   5 }

  This payload is digitally signed by the server. If anyone tries to change the tenant_id
  or any other part of it, the signature will become invalid, and the server will reject
  the token.

  ---

  Part 3: Using the Token (Authorization & Multi-Tenancy)

  This is where the magic happens. Now that you have your secure "ID card," you use it to
  access protected data.

   1. Making a Request:
       * You want to get all leads, so you make a request to GET /api/v1/lead/.
       * You must include your token in the Authorization header: Authorization: Bearer
         <your_access_token>.

   2. On the Server-Side:
       * The server receives your request. Before doing anything else, a security function
         (get_current_user) intercepts it.
       * It reads the token from your Authorization header.
       * It decodes the token and securely extracts the `tenant_id` (e.g.,
         "YOUR_TENANT_ID") from its payload.
       * Now, when the application logic calls the database to fetch the leads, it uses
         that specific `tenant_id`.

  Here is the data flow for your request:

    1 Your Request --> GET /api/v1/lead/  (with Token)
    2       |
    3       V
    4 FastAPI Server --> Decodes Token, finds tenant_id: "YOUR_TENANT_ID"
    5       |
    6       V
    7 Lead Service --> get_all_leads(tenant_id="YOUR_TENANT_ID")
    8       |
    9       V
   10 SQLite Handler --> get_all_leads(tenant_id="YOUR_TENANT_ID")
   11       |
   12       V
   13 Database --> Connects to "tenant_data/YOUR_TENANT_ID.db" ONLY
   14       |
   15       V
   16 Your Response <-- Returns leads from ONLY that database file

  This ensures perfect data isolation. The tenant_id securely stored inside the JWT
  dictates which database file is used for every single request, making it impossible for a
  user authenticated for "Tenant A" to ever access data from "Tenant B".
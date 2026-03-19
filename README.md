# Bank API

A simple banking API built with Django and Django REST Framework.

This project is an early-stage backend for common banking operations such as user registration, account creation, authentication, balance-changing transactions, and mortgage management. The README reflects the current state of the codebase so it can evolve along with future improvements.

## Overview

The API currently provides:

- user registration
- session-based authentication with login and logout
- bank account creation linked to a user
- transactions for deposit, withdraw, payment, and transfer
- mortgage endpoints under active development

The application is organized into separate Django apps:

- `core`: API views, serializers, and route registration
- `user`: custom user model and manager
- `products`: account and mortgage models
- `transaction`: transaction rules and balance updates

## Tech Stack

- Python
- Django 6.0.3
- Django REST Framework 3.16.1
- SQLite (default local database)
- Ruff for linting
- DjLint and DjHTML for template/HTML formatting

## Current Architecture

The project uses Django apps to separate business domains, but some responsibilities are still concentrated in models, serializers, and viewsets. This is intentional for the current stage of the project and will likely be improved over time as the API grows.

At the moment:

- authentication uses Django session login
- most endpoints are exposed through DRF `ModelViewSet`
- transaction business rules are handled directly inside the transaction model
- account creation depends on the authenticated user in the request context

## Running Locally

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd <your-project-folder>
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

Install the project dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

The project reads the Django secret key from the `DEV_PROJECT_KEY` environment variable.

Linux/macOS:

```bash
export DEV_PROJECT_KEY="your-secret-key"
```

Windows PowerShell:

```powershell
$env:DEV_PROJECT_KEY="your-secret-key"
```

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Run the development server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## Main Endpoints

### Health / Index

- `GET /`

Returns a simple welcome message.

### Authentication

- `POST /bank/auth/login/`
- `POST /bank/auth/logout/`

Current authentication is session-based, using Django's built-in login/logout flow.

Example login payload:

```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

### User Registration

- `GET /bank/user_creation/`
- `POST /bank/user_creation/`
- `GET /bank/user_creation/{id}/`
- `PUT/PATCH /bank/user_creation/{id}/`
- `DELETE /bank/user_creation/{id}/`

Example payload:

```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

### Account

- `GET /bank/account/`
- `POST /bank/account/`
- `GET /bank/account/{number}/`
- `PUT/PATCH /bank/account/{number}/`
- `DELETE /bank/account/{number}/`

Example payload:

```json
{
  "account_type": "CA"
}
```

Supported account types:

- `CA`: Checking Account
- `SA`: Savings Account

Notes:

- the account is linked to the authenticated user
- agency, account number, and initial balance are generated automatically

### Transactions

#### Standard transactions

- `GET /bank/transaction/`
- `POST /bank/transaction/`
- `GET /bank/transaction/{id}/`
- `PUT/PATCH /bank/transaction/{id}/`
- `DELETE /bank/transaction/{id}/`

Supported transaction types for this endpoint:

- `DP`: Deposit
- `WD`: Withdraw
- `PM`: Payment

Example payload:

```json
{
  "transaction_type": "DP",
  "amount": "500.00"
}
```

#### Transfers

- `GET /bank/transaction_transfer/`
- `POST /bank/transaction_transfer/`
- `GET /bank/transaction_transfer/{id}/`
- `PUT/PATCH /bank/transaction_transfer/{id}/`
- `DELETE /bank/transaction_transfer/{id}/`

This endpoint is dedicated to transfer operations only.

Example payload:

```json
{
  "recipient": "1234567", // account number
  "transaction_type": "TF",
  "amount": "150.00"
}
```

Notes:

- the sender account is resolved from `request.user.account`
- transfers require a recipient account
- insufficient balance raises a validation error

### Mortgages

- `GET /bank/mortgage/`
- `POST /bank/mortgage/`
- `GET /bank/mortgage/{id}/`
- `PUT/PATCH /bank/mortgage/{id}/`
- `DELETE /bank/mortgage/{id}/`

Supported mortgage types in the current model:

- `FHAL`: FHA Loan
- `VALN`: VA Loans
- `CVTL`: Conventional Loan
- `JUBL`: Jumbo Loan
- `UDAL`: USDA Loan

This area is still evolving and is one of the main candidates for future refinement.

## Important Notes About the Current State

- The API is functional as a learning and portfolio project, but it is still in an early stage.
- Authentication currently relies on Django sessions instead of token-based authentication such as JWT.
- Some endpoints are exposed through generic CRUD viewsets even when the business flow may later require more specific actions or service layers.
- Mortgage and transaction logic can still be made clearer and more robust through refactoring.

## Suggested Future Improvements

The following items are intentionally documented as future evolution paths based on the current implementation:

- separate domain/business rules from models and serializers into dedicated service classes
- refactor transaction processing to reduce responsibility concentration inside `TransactionModel`
- improve mortgage validation flow and make eligibility rules more explicit
- introduce permission classes so sensitive operations are properly protected
- move from session-based authentication to token or JWT authentication for API clients
- add environment-specific settings for development, testing, and production
- improve API validation messages and error consistency
- document request/response examples more thoroughly
- add automated tests for authentication, account creation, transfers, and mortgage scenarios
- add API versioning as the project evolves
- consider using serializers and view logic that better separate read and write concerns

## Possible Refactoring Directions

As the project grows, a good next step would be to improve separation of responsibilities, for example:

- keep models focused on persistence and invariants
- move use-case orchestration into service/application layers
- reduce business logic inside serializers
- use dedicated endpoints or commands for banking actions instead of relying only on generic CRUD

This would make the code easier to test, maintain, and extend.

## Authoring Note

This README was written to match the current implementation. As new features and improvements are released, the documentation can be expanded with new endpoints, authentication strategies, architectural decisions, and deployment instructions.

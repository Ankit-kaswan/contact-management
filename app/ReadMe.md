# Contact Management API  

This project is a Contact Management API built with Django and Django REST Framework (DRF), fully containerized using Docker for seamless deployment.

---

## Features  

- User registration and authentication  
- User profile management  
- Mark phone numbers as spam  
- Search contacts by name or phone number  

---

## Prerequisites  

- Docker installed on your system  

---

## Running the Application with Docker  

### 1.  Run with Docker Compose

```bash  
cd contact-management/app

docker-compose up -d --build

```

### 2.  Stopping the Containers

```bash  
docker-compose down

```

## Testing the Application with Docker

- Application should be running state

```bash  
docker-compose exec web python manage.py test

```


# API - CURL Commands  

Below are the CURL commands for testing various endpoints of the Contact Management API.

---

## 1. User Registration  

### Endpoint: `POST /api/register/`  
Registers a new user.  

```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
-H "Content-Type: application/json" \
-d '{
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "password@123",
  "phone_number": "+1234567890"
}'

```

## 2. User Login  

### Endpoint: `POST /api/token/`
- Authenticates a user and returns an access token.

#### CURL Command for Access Token

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
-H "Content-Type: application/json" \
-d '{
  "username": "testuser",
  "password": "password@123"
}'

```

#### CURL Command for Refresh Token

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
-H "Content-Type: application/json" \
-d '{
  "refresh": "your_refresh_token"
}'

```


## 3. Get User Profile

### Endpoint: `GET /api/profile/`  
Fetch the profile information of the authenticated user.

#### Description  
This endpoint allows the user to retrieve their profile information. It returns details such as the user's email and phone number.

#### CURL Command

```bash
curl -X GET http://127.0.0.1:8000/api/profile/ \
-H "Authorization: Bearer <your_token>"

```

## 4. Update User Profile

### Endpoint: `PUT /api/profile/`  
Update the profile information of the authenticated user.

#### Description  
This endpoint allows the user to update their profile information, such as their email and phone number.

#### CURL Command

```bash
curl -X PUT http://127.0.0.1:8000/api/profile/ \
-H "Authorization: Bearer <your_token>" \
-H "Content-Type: application/json" \
-d '{
  "email": "newemail@example.com",
  "phone_number": "+1234567899"
}'

```

## 5. Mark a Number as Spam

### Endpoint: `POST /api/mark_spam/`  
Mark a phone number as spam.

#### Description  
This endpoint allows the user to mark a phone number as spam. 

#### Request Body  

- **phone_number**: The phone number to be marked as spam. This should include the country code (e.g., `+1234567890`).

#### CURL Command

```bash
curl -X POST http://127.0.0.1:8000/api/mark_spam/ \
-H "Authorization: Bearer <your_token>" \
-H "Content-Type: application/json" \
-d '{
  "phone_number": "+9876543210"
}'

```

### 6. Search Contacts

- **Endpoint**: `GET /api/search/`
- **Description**: Allows the user to search for contacts by name or phone number. It prioritizes contacts whose names start with the query.

#### Parameters

- **query**: The search term to look for in contact names or phone numbers.

#### CURL Command - Search name

```bash
curl -X GET "http://127.0.0.1:8000/api/search/?query=<john>" \
-H "Authorization: Bearer <your_token>"

```

#### CURL Command - Search phone

```bash
curl -X GET "http://127.0.0.1:8000/api/search/?query=<0123456789>" \
-H "Authorization: Bearer <your_token>"

```



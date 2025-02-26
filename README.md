# FastAPI Microservices Project

This project contains two FastAPI-based microservices:
1. **User Service**: Handles user registration, login, and product creation (only accessible to authenticated users).
2. **Product Service**: Allows authenticated users to view products they have created.

## Technologies Used

- **FastAPI**: Web framework for building APIs.
- **MongoDB**: NoSQL database to store user and product data.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **Passlib**: Password hashing for secure authentication.

## Project Structure

- `user-service/`: Contains the user-related services, including user registration and login.
- `product-service/`: Contains the product-related services, allowing authenticated users to view their products.
- `requirements.txt`: Python dependencies for each of the services.
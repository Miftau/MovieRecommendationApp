# MovieRecommendationApp
🎬 Movie Recommendation System using Machine Learning &amp; Flask A web-based intelligent movie recommender system that leverages machine learning techniques to suggest personalized movie recommendations based on user preferences, viewing history, or similarity metrics. Built with Python, Flask, and modern AI/ML tools.

# API Endpoints
| Method | Endpoint               | Description                     | Auth |
| ------ |------------------------| ------------------------------- | ---- |
| POST   | `/api/register`        | Register a new user             | ❌    |
| POST   | `/api/login`           | Login and get JWT token         | ❌    |
| GET    | `/api/movies`          | Get list of all movies          | ✅    |
| POST   | `/api/rate`            | Submit a movie rating           | ✅    |
| GET    | `/api/recommendations` | Get recommended movies for user | ✅    |


# Postman Collection Sample
{
  "info": {
    "_postman_id": "a18c3c58-bc0f-4c18-8785-bdeac81eeaf7",
    "name": "Movie Recommendation App",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "User Registration",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"username\": \"user1\",\n    \"password\": \"password123\"\n}"
        },
        "url": {
          "raw": "http://localhost:5000/api/register",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "register"]
        }
      }
    },
    {
      "name": "User Login",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"username\": \"user1\",\n    \"password\": \"password123\"\n}"
        },
        "url": {
          "raw": "http://localhost:5000/api/login",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "login"]
        }
      }
    },
    {
      "name": "Get All Movies",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://localhost:5000/api/movies",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "movies"]
        }
      }
    },
    {
      "name": "Submit Rating",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"user_id\": 1,\n    \"movie_id\": 10,\n    \"rating\": 4.0\n}"
        },
        "url": {
          "raw": "http://localhost:5000/api/rate",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "rate"]
        }
      }
    },
    {
      "name": "Get Recommendations",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://localhost:5000/api/recommendations/1",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "recommendations", "1"]
        }
      }
    },
    {
      "name": "Admin Login (Web)",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/x-www-form-urlencoded" }],
        "body": {
          "mode": "urlencoded",
          "urlencoded": [
            { "key": "username", "value": "admin" },
            { "key": "password", "value": "admin123" }
          ]
        },
        "url": {
          "raw": "http://localhost:5000/admin",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["admin"]
        }
      }
    }
  ]
}

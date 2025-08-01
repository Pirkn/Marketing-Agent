# Marketing Agent API Documentation

## Overview

The Marketing Agent API is a Flask-based REST API that provides AI-powered marketing tools for product analysis and content generation. The API uses Supabase for authentication and integrates with Gemini AI for content generation.

**Base URL:** `http://localhost:5000`  
**API Version:** v1  
**Authentication:** Supabase JWT Tokens  
**Framework:** Flask with Flask-Smorest for OpenAPI documentation

## Authentication

The API uses Supabase JWT tokens for authentication. Protected endpoints require a valid JWT token in the Authorization header.

```http
Authorization: Bearer <your-supabase-jwt-token>
```

## Health Check

### GET /health

Check if the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

## Protected Routes

### GET /protected

Test endpoint for authenticated users.

**Headers:**
- `Authorization: Bearer <jwt-token>` (Required)

**Response:**
```json
{
  "message": "This is a protected route",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com"
  }
}
```

## Product Operations

### POST /generate-product-details

Generate product details by analyzing a website URL using AI.

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <jwt-token>` (Required)

**Request Body:**
```json
{
  "product_website_link": "https://example.com"
}
```

**Response:**
```json
{
  "target_audience": "Entrepreneurs and SaaS founders",
  "description": "A no-code waitlist builder that helps entrepreneurs validate ideas and build early audiences...",
  "problem_solved": "Difficulty in launching new concepts without wasting time on unvalidated MVPs"
}
```

**Example Usage:**
```bash
curl -X POST http://localhost:5000/generate-product-details \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "product_website_link": "https://www.waitlistsnow.com"
  }'
```

### POST /create_product

Create a new product for the authenticated user.

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <jwt-token>` (Required)

**Request Body:**
```json
{
  "name": "Product Name",
  "url": "https://example.com",
  "description": "Product description",
  "target_audience": "Target audience description",
  "problem_solved": "Problem this product solves"
}
```

**Response:**
```json
{
  "message": "Product created successfully",
  "product": {
    "id": "uuid",
    "user_id": "user-uuid",
    "name": "Product Name",
    "url": "https://example.com",
    "description": "Product description",
    "target_audience": "Target audience description",
    "problem_solved": "Problem this product solves",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Example Usage:**
```bash
curl -X POST http://localhost:5000/create_product \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "name": "My Awesome Product",
    "url": "https://myproduct.com",
    "description": "A revolutionary product that solves real problems",
    "target_audience": "Entrepreneurs and small business owners",
    "problem_solved": "Complex workflow automation"
  }'
```

### GET /products

Get all products for the authenticated user.

**Headers:**
- `Authorization: Bearer <jwt-token>` (Required)

**Response:**
```json
{
  "products": [
    {
      "id": "uuid",
      "user_id": "user-uuid",
      "name": "Product Name",
      "url": "https://example.com",
      "description": "Product description",
      "target_audience": "Target audience description",
      "problem_solved": "Problem this product solves",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Example Usage:**
```bash
curl -X GET http://localhost:5000/products \
  -H "Authorization: Bearer <your-jwt-token>"
```

## Reddit Operations

### POST /generate-reddit-post

Generate Reddit marketing posts using AI based on product information stored in the database.

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <jwt-token>` (Required)

**Request Body:**
```json
{
  "product_id": "product-uuid"
}
```

**Response:**
```json
{
  "response": "Generated Reddit post content..."
}
```

**Example Usage:**
```bash
curl -X POST http://localhost:5000/generate-reddit-post \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "product_id": "your-product-uuid"
  }'
```

### GET /get-viral-posts

Retrieve a collection of viral Reddit posts for reference and inspiration.

**Headers:**
- `Authorization: Bearer <jwt-token>` (Required)

**Response:**
```json
[
  {
    "title": "Viral Post Title",
    "content": "Post content...",
    "subreddit": "r/entrepreneur",
    "upvotes": 1500,
    "comments": 200
  }
]
```

**Example Usage:**
```bash
curl -X GET http://localhost:5000/get-viral-posts \
  -H "Authorization: Bearer <your-jwt-token>"
```

### GET /get_karma

Get karma analysis for a specific subreddit using Reddit API data.

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <jwt-token>` (Required)

**Request Body:**
```json
{
  "subreddit_name": "entrepreneur"
}
```

**Response:**
```json
{
  "response": "Karma analysis and insights for the subreddit..."
}
```

**Example Usage:**
```bash
curl -X GET http://localhost:5000/get_karma \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "subreddit_name": "entrepreneur"
  }'
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing authentication token"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Product not found or access denied"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:5173`
- `http://127.0.0.1:5500`
- `http://localhost:5500`

## Environment Variables

Required environment variables:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
GEMINI_API_KEY=your_gemini_api_key
```

## Dependencies

The API uses the following main dependencies:

```
Flask==2.3.3
flask-smorest==0.42.0
flask-cors==4.0.0
python-dotenv==1.0.0
praw==7.7.1
requests==2.31.0
google-generativeai==0.3.2
supabase==2.3.4
```

## Project Structure

```
Backend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── API_DOCUMENTATION.md  # This documentation
└── src/
    ├── config/           # AI prompt configurations
    ├── data/            # Static data files (viral_posts.json)
    ├── routes/          # API route blueprints
    │   ├── product.py   # Product-related endpoints
    │   └── reddit.py    # Reddit-related endpoints
    └── utils/           # Utility modules
        ├── auth.py      # Authentication utilities
        ├── models.py    # AI model integration
        ├── prompt_generator.py  # Prompt generation
        ├── reddit_helpers.py    # Reddit API helpers
        └── website_scraper.py   # Web scraping utilities
```

## Security Considerations

1. **Authentication**: All sensitive endpoints require valid Supabase JWT tokens
2. **CORS**: Configured to allow specific origins only
3. **Input Validation**: Implement proper input validation for all endpoints
4. **HTTPS**: Use HTTPS in production environments
5. **User Isolation**: Products are isolated by user_id to prevent unauthorized access

## Development

### Running the API

```bash
cd Backend
python app.py
```

The API will be available at `http://localhost:5000`

### API Documentation

The API uses Flask-Smorest for automatic OpenAPI documentation. Access the interactive documentation at:
- Swagger UI: `http://localhost:5000/swagger`
- ReDoc: `http://localhost:5000/redoc`

## Database Schema

### Products Table
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key to users)
- `name` (Text, Required)
- `url` (Text, Optional)
- `description` (Text, Optional)
- `target_audience` (Text, Optional)
- `problem_solved` (Text, Optional)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## Support

For API support or questions, please refer to the project documentation or create an issue in the repository. 
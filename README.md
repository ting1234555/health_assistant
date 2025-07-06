---
title: Health Assistant API
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
---

# Health Assistant API

A comprehensive health tracking application with AI-powered features.

## Features

- 🍽️ Diet tracking with AI image recognition
- 💧 Water intake monitoring
- 🏃‍♂️ Exercise logging
- 📊 Nutrition analysis dashboard
- 🤖 AI-driven personalized recommendations

## API Endpoints

### Health Data
- `POST /api/food/analyze` - Analyze food from image
- `GET /api/nutrition/dashboard` - Get nutrition dashboard
- `POST /api/exercise/log` - Log exercise data

### User Management
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login

## Usage

This API is designed to work with the frontend deployed on Vercel. 

### Example Request

```bash
curl -X POST "https://your-space.hf.space/api/food/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@your-food-image.jpg"
```

## Configuration

The API automatically configures CORS for cross-origin requests and includes:
- Image processing capabilities
- AI model integration
- Database connectivity
- Authentication system

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy
- **AI/ML**: HuggingFace Transformers, PyTorch
- **Database**: PostgreSQL/SQLite
- **Authentication**: JWT tokens
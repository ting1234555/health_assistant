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

- `POST /api/food/analyze` - Analyze food from image
- `GET /api/nutrition/dashboard` - Get nutrition dashboard
- `POST /api/exercise/log` - Log exercise data

## Usage

This API is designed to work with the frontend deployed on Vercel.

Example request:
```bash
curl -X POST "https://yuting111222-health-assistant.hf.space/api/food/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@your-food-image.jpg"
```

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy
- **AI/ML**: HuggingFace Transformers, PyTorch
- **Database**: PostgreSQL/SQLite
- **Authentication**: JWT tokens
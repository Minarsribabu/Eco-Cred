# EcoCred Deployment Guide

## Overview
EcoCred is a full-stack web application for tracking carbon footprints and earning eco-credits. This guide covers deployment options for production use.

## Architecture
- **Backend**: Python Flask API with SQLAlchemy ORM
- **Frontend**: Vanilla HTML/CSS/JavaScript (served by Flask)
- **Database**: SQLite (development) or PostgreSQL (production)
- **Authentication**: JWT tokens

## Local Development

### Prerequisites
- Python 3.11+
- pip

### Setup
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your settings

# Run the application
python app.py
```

The app will be available at http://localhost:5000


## Production Deployment Options

### 1. Render (Recommended - Free tier available)
Render provides free hosting with PostgreSQL and automatic deployments.

**Method 1: Manual Setup (Recommended)**
1. Go to [render.com](https://render.com) and sign up
2. **First, create PostgreSQL database:**
   - Click "New +" → "PostgreSQL"
   - Name: `ecocred-db`
   - Copy the `DATABASE_URL`
3. **Then create Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository (Eco-Cred)
   - Configure:
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r backend/requirements.txt`
     - **Start Command**: `cd backend && python app.py`
4. **Set environment variables:**
   - `JWT_SECRET`: Generate a secure random string (32+ characters)
   - `DATABASE_URL`: Paste from your PostgreSQL database
   - `PORT`: 5000
5. Deploy

**Method 2: Using render.yaml (Alternative)**
1. Commit the `render.yaml` file to your repository
2. Go to Render → "New +" → "Blueprint"
3. Connect your GitHub repo
4. Render will auto-configure based on `render.yaml`
   - **Note**: Use `runtime: python` (not `python3`) in render.yaml

### 2. Railway
Railway provides easy deployment with built-in PostgreSQL.

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Python app
3. Set environment variables in Railway dashboard:
   - `JWT_SECRET`: Generate a secure random string
   - `DATABASE_URL`: Provided by Railway PostgreSQL
   - `PORT`: 5000 (default)

### 3. Vercel (Frontend only - not recommended for full-stack)
Vercel is primarily for frontend apps. For full-stack Python apps, use Render or Railway instead.

### 4. Heroku
```bash
# Create Heroku app
heroku create your-ecocred-app

# Set environment variables
heroku config:set JWT_SECRET=your-secure-jwt-secret
heroku config:set DATABASE_URL=your-postgres-url

# Deploy
git push heroku master
```

### 5. DigitalOcean App Platform
1. Connect your repository
2. Configure as Python app
3. Set environment variables
4. Deploy

### 6. AWS/GCP/Azure
Deploy using their container services or App Runner equivalents.

## Environment Variables

### Required
- `JWT_SECRET`: Secure random string for JWT signing
- `DATABASE_URL`: Database connection string
- `PORT`: Port to run the server (default: 5000)

### Optional
- `FLASK_ENV`: Set to 'production' for production mode

## Database Setup

### SQLite (Development)
Default configuration uses SQLite. Database file is created automatically.

### PostgreSQL (Production)
Update `DATABASE_URL` to your PostgreSQL connection string:
```
postgresql://username:password@host:port/database
```

## Security Considerations

1. **Change JWT Secret**: Never use the default JWT secret in production
2. **HTTPS**: Always use HTTPS in production
3. **Database**: Use PostgreSQL for production workloads
4. **Environment Variables**: Store secrets securely, not in code
5. **Updates**: Keep dependencies updated for security patches

## Monitoring

The app includes a health check endpoint at `/v1/health` that you can use for monitoring.

## Troubleshooting

### Common Issues
1. **Port already in use**: Change the PORT environment variable
2. **Database connection errors**: Verify DATABASE_URL format
3. **Static files not loading**: Ensure frontend files are in the correct directory

### Logs
Check application logs for detailed error information:
```bash
docker-compose logs ecocred
```

## Performance Optimization

1. **Database**: Use connection pooling for high traffic
2. **Static Files**: Consider using a CDN for static assets
3. **Caching**: Implement Redis for session/data caching
4. **Scaling**: Use multiple instances behind a load balancer

## Backup Strategy

### Database Backups
- SQLite: Regular file backups
- PostgreSQL: Use pg_dump for backups

### User Data
- Export user data regularly for compliance
- Implement data retention policies

## Support

For issues or questions:
- Check the logs for error details
- Verify environment configuration
- Test API endpoints with curl or Postman
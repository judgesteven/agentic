# 🚀 Deployment Guide

This guide will help you deploy the Agentic AI system to Vercel with automated CI/CD using GitHub Actions.

## 📋 Prerequisites

1. **GitHub Account**: You need a GitHub account
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
3. **Vercel CLI** (optional): `npm i -g vercel`

## 🔧 Setup Steps

### 1. Connect GitHub Repository to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository: `https://github.com/judgesteven/agentic.git`
4. Configure the project:
   - **Framework Preset**: Other
   - **Root Directory**: `./`
   - **Build Command**: Leave empty (handled by Vercel)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

### 2. Configure Environment Variables

In your Vercel project dashboard, add these environment variables:

```bash
# Optional: OpenAI API Key (for full functionality)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Other API keys as needed
SERPER_API_KEY=your_serper_api_key_here
WEATHER_API_KEY=your_weather_api_key_here
```

### 3. Set Up GitHub Secrets

In your GitHub repository, go to **Settings > Secrets and variables > Actions** and add:

```bash
VERCEL_TOKEN=your_vercel_token_here
ORG_ID=your_vercel_org_id_here
PROJECT_ID=your_vercel_project_id_here
```

To get these values:
1. **VERCEL_TOKEN**: Go to Vercel Account Settings > Tokens > Create
2. **ORG_ID**: Found in Vercel project settings
3. **PROJECT_ID**: Found in Vercel project settings

### 4. Deploy

The deployment will happen automatically when you push to the `main` branch. You can also:

```bash
# Manual deployment
vercel --prod
```

## 🌐 Access Your App

Once deployed, your app will be available at:
- **Production**: `https://your-project-name.vercel.app`
- **Preview**: `https://your-project-name-git-branch.vercel.app`

## 🔄 Automated Deployment Pipeline

The GitHub Actions workflow (`.github/workflows/deploy.yml`) will:

1. **Trigger**: On push to `main` branch or pull requests
2. **Test**: Run pytest to ensure code quality
3. **Deploy**: Automatically deploy to Vercel
4. **Notify**: Send deployment status notifications

## 📱 Features

- ✅ **Mobile-friendly iOS-style UI**
- ✅ **Real-time chat interface**
- ✅ **Task planning and execution**
- ✅ **Agent status monitoring**
- ✅ **Responsive design**
- ✅ **Dark mode support**

## 🛠️ Troubleshooting

### Common Issues

1. **Build Failures**: Check that all dependencies are in `requirements.txt`
2. **Import Errors**: Ensure all Python modules are properly structured
3. **Environment Variables**: Verify all required env vars are set in Vercel

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python web_interface.py

# Access at http://localhost:8080
```

## 📈 Monitoring

- **Vercel Analytics**: Built-in performance monitoring
- **GitHub Actions**: CI/CD pipeline status
- **Error Tracking**: Vercel provides error logs

## 🔒 Security

- Environment variables are encrypted
- API keys are stored securely in Vercel
- HTTPS is enabled by default
- CORS is properly configured

## 📞 Support

For issues with:
- **Vercel Deployment**: Check Vercel documentation
- **GitHub Actions**: Check GitHub Actions logs
- **Application Code**: Check the main README.md

---

**Happy Deploying! 🚀** 
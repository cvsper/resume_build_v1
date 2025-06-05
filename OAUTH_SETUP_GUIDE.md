# OAuth Setup Guide

This guide explains how to set up OAuth authentication for Google, LinkedIn, and Apple Sign-In.

## Implementation Status

✅ **Google OAuth** - Fully implemented and ready for configuration
✅ **LinkedIn OAuth** - Fully implemented and ready for configuration  
⏳ **Apple Sign-In** - Placeholder implemented (shows "coming soon" message)

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to "Credentials" and click "Create Credentials" → "OAuth 2.0 Client IDs"
5. Configure the OAuth consent screen
6. Add authorized redirect URIs:
   - For development: `http://localhost:5000/callback/google`
   - For production: `https://yourdomain.com/callback/google`
7. Copy the Client ID and Client Secret to your `.env` file:
   ```
   GOOGLE_CLIENT_ID=your_google_client_id_here
   GOOGLE_CLIENT_SECRET=your_google_client_secret_here
   ```

## LinkedIn OAuth Setup

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Create a new app
3. Add the following scopes:
   - `r_liteprofile` (to access basic profile)
   - `r_emailaddress` (to access email)
4. Add authorized redirect URIs:
   - For development: `http://localhost:5000/callback/linkedin`
   - For production: `https://yourdomain.com/callback/linkedin`
5. Copy the Client ID and Client Secret to your `.env` file:
   ```
   LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
   LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here
   ```

## Apple Sign-In Setup (Future Implementation)

Apple Sign-In requires additional setup and is more complex than other OAuth providers:

1. Join the Apple Developer Program ($99/year)
2. Create an App ID with Sign In with Apple capability
3. Create a Services ID for web authentication
4. Generate a private key for authentication
5. Configure domains and redirect URLs

For now, the Apple button shows a "coming soon" message.

## Testing OAuth

1. Start your Flask application
2. Navigate to the login page
3. Click on Google or LinkedIn buttons
4. You should be redirected to the respective OAuth provider
5. After authorization, you'll be redirected back to your app

## Troubleshooting

### Common Issues

1. **Invalid redirect URI**: Make sure your redirect URIs in the OAuth app settings match exactly with your Flask routes
2. **Missing scopes**: Ensure you've requested the necessary scopes for user profile and email access
3. **HTTPS required**: Most OAuth providers require HTTPS in production
4. **Environment variables**: Double-check that your client IDs and secrets are correctly set in the `.env` file

### Development vs Production

- Development: Use `http://localhost:5000` for redirect URIs
- Production: Use your actual domain with HTTPS

## Security Notes

- Never commit OAuth credentials to version control
- Use environment variables for all sensitive data
- Regularly rotate your OAuth secrets
- Monitor OAuth app usage in provider dashboards

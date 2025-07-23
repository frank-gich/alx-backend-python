# JWT Authentication Setup for Django Messaging App

## Installation Steps

### 1. Install Required Dependencies

```bash
pip install djangorestframework-simplejwt django-cors-headers
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

### 2. Update Settings

Make sure your `settings.py` includes `AUTH_USER_MODEL = 'chats.CustomUser'` to use the custom user model.

### 3. Database Migration

After updating your settings, run migrations to apply any changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

## Configuration Overview

### JWT Settings Explained

The `SIMPLE_JWT` configuration in `settings.py` includes:

- **ACCESS_TOKEN_LIFETIME**: 60 minutes - how long access tokens are valid
- **REFRESH_TOKEN_LIFETIME**: 7 days - how long refresh tokens are valid  
- **ROTATE_REFRESH_TOKENS**: True - generates new refresh token on refresh
- **BLACKLIST_AFTER_ROTATION**: True - blacklists old refresh tokens
- **AUTH_HEADER_TYPES**: ('Bearer',) - expects "Bearer <token>" format

### Available Chat Endpoints

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|------------------------|
| `/api/chats/conversations/` | GET | List user's conversations | Yes |
| `/api/chats/conversations/` | POST | Create new conversation | Yes |
| `/api/chats/conversations/{id}/` | GET | Get conversation details | Yes (participant only) |
| `/api/chats/conversations/{id}/` | PUT/PATCH | Update conversation | Yes (participant only) |
| `/api/chats/conversations/{id}/` | DELETE | Delete conversation | Yes (participant only) |
| `/api/chats/conversations/create-with-users/` | POST | Create conversation with specific users | Yes |
| `/api/chats/conversations/{id}/add-participant/` | POST | Add participant to conversation | Yes (participant only) |
| `/api/chats/conversations/{id}/remove-participant/` | POST | Remove participant from conversation | Yes (participant only) |
| `/api/chats/conversations/{id}/messages/` | GET | List messages in conversation | Yes (participant only) |
| `/api/chats/conversations/{id}/messages/` | POST | Send message to conversation | Yes (participant only) |
| `/api/chats/messages/{id}/` | GET | Get specific message | Yes (participant only) |
| `/api/chats/messages/{id}/` | PUT/PATCH | Update message | Yes (sender only) |
| `/api/chats/messages/{id}/` | DELETE | Delete message | Yes (sender only) |
| `/api/chats/users/search/` | GET | Search for users | Yes |

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|------------------------|
| `/api/auth/register/` | POST | Register new user | No |
| `/api/auth/login/` | POST | Login and get tokens | No |
| `/api/auth/token/refresh/` | POST | Refresh access token | No |
| `/api/auth/logout/` | POST | Logout (blacklist token) | Yes |
| `/api/auth/profile/` | GET | Get user profile | Yes |
| `/api/auth/profile/update/` | PUT/PATCH | Update user profile | Yes |
| `/api/auth/change-password/` | POST | Change password | Yes |
| `/api/auth/verify/` | GET | Verify token validity | Yes |

## API Usage Examples

### 1. User Registration

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "strongpassword123",
    "password_confirm": "strongpassword123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 2. User Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "strongpassword123"
  }'
```

### 3. Access Protected Endpoints

```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Refresh Token

```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```
## Security Best Practices

1. **Use HTTPS in production** - Never send JWT tokens over HTTP
2. **Store tokens securely** - Use httpOnly cookies in production instead of localStorage
3. **Implement token rotation** - Already configured with `ROTATE_REFRESH_TOKENS`
4. **Set appropriate token lifetimes** - Balance security with user experience
5. **Validate tokens server-side** - Always verify tokens on protected endpoints
6. **Handle token expiration gracefully** - Implement automatic refresh logic

## Custom Permissions Usage

The custom permissions in `permissions.py` ensure users can only access their own data:

- **IsMessageOwner**: Only message senders can edit/delete their messages
- **IsConversationParticipant**: Only conversation participants can access conversation data
- **CanSendMessage**: Only participants can send messages to conversations
- **IsOwnerOrParticipant**: Combined permission for flexible access control

## Troubleshooting

### Common Issues

1. **"Invalid token" errors**: Check if token has expired or is malformed
2. **CORS issues**: Ensure `django-cors-headers` is properly configured
3. **Permission denied**: Verify user has appropriate permissions for the resource
4. **Token blacklist errors**: Make sure you're using the refresh token correctly

### Testing Authentication

```bash
# Test token validity
curl -X GET http://localhost:8000/api/auth/verify/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Test protected endpoint
curl -X GET http://localhost:8000/api/chats/conversations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
# Users Module

## Overview
- **User Model (models.py)**
  - Extends `AbstractUser` (removes `username`, uses `email` as unique identifier)
  - Additional field: `telegram_id`
  - Custom manager: `UserManager`

- **Serializers (serializers.py)**
  - **UserRegistrationSerializer**: Registers new users; handles password hashing with `set_password`
  - **UserProfileSerializer**: Displays/updates user profiles; some fields (email, is_staff, date_joined) are read-only

- **Views (views.py)**
  - **RegisterUserView**: Public endpoint for user registration (permission: `AllowAny`)
  - **UserProfileView**: Allows authenticated users to view/update their profile; uses `IsAuthenticated` and custom `IsSelfOrAdmin` permission

- **URLs (urls.py)**
  - `/register/` – Register new user
  - `/token/` – Obtain JWT token
  - `/token/refresh/` – Refresh JWT token
  - `/me/` – Current user profile

- **Permissions (permissions.py)**
  - **IsSelfOrAdmin**: Grants access only if the target object belongs to the current user or if the user is an admin

## Key Points
- **Authentication**: Uses login/password and JWT tokens for secure access
- **Role-Based Access**: Custom permissions (e.g., `IsSelfOrAdmin`) enforce that only owners or admins can modify profiles
- **Extensibility**: The user model is structured for easy extension (e.g., Telegram integration)

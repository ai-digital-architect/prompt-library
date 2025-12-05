# Python/Django Development Guidelines

## Project Structure

```
project_name/
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── project_name/
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   └── wsgi.py
└── apps/
    ├── core/
    ├── users/
    └── api/
```

## Best Practices

### Python Specific

- Follow PEP 8 style guide
- Use type hints (Python 3.6+)
- Implement proper exception handling
- Use virtual environments
- Document with docstrings

### Django Guidelines

```python
# Models - Use proper field types and validation
from django.db import models

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date_joined']
```

### REST Framework Patterns

```python
# ViewSets - Implement proper viewsets
from rest_framework import viewsets

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
```

### Authentication & Authorization

- Use Django's built-in auth
- Implement JWT for APIs
- Use permission classes
- Role-based access control
- Secure password handling

### Database Best Practices

- Use migrations properly
- Implement indexes
- Optimize queries
- Use select_related/prefetch_related
- Implement proper model relationships

### Testing

```python
# Test cases example
from django.test import TestCase

class UserTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_user_creation(self):
        self.assertTrue(isinstance(self.user, User))
```

### Security

- CSRF protection
- XSS prevention
- SQL injection prevention
- Secure file uploads
- Environment variables for secrets

### Performance

- Caching strategies
- Database optimization
- Static file handling
- Async views (Django 3.1+)
- Proper deployment configuration

## Common Dependencies

```txt
# requirements/base.txt
Django>=4.2.0
djangorestframework>=3.14.0
django-environ>=0.10.0
psycopg2-binary>=2.9.6
django-cors-headers>=4.0.0
```

## Development Setup

```python
# settings/dev.py
DEBUG = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ... other apps
    'rest_framework',
    'corsheaders',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

## Deployment Considerations

- Use gunicorn/uvicorn
- Implement proper logging
- Configure static files
- Set up media files
- Database backups
- CI/CD pipeline setup

## Code Style Guide

```python
# Example of well-structured view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def user_detail(request, pk):
    """
    Retrieve a user instance.
    
    Args:
        request: The HTTP request
        pk: The primary key of the user
        
    Returns:
        Response: The serialized user data
    """
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
        
    serializer = UserSerializer(user)
    return Response(serializer.data)
```

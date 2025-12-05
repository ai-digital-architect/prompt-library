# Node.js Development Guidelines

## Project Structure

```
project-root/
├── src/
│   ├── api/
│   ├── config/
│   ├── middleware/
│   ├── models/
│   ├── services/
│   ├── utils/
│   └── app.ts
├── tests/
│   ├── integration/
│   └── unit/
├── package.json
├── tsconfig.json
└── jest.config.js
```

## Best Practices

### Async Programming

```typescript
// Use async/await with proper error handling
async function getUserData(userId: string): Promise<User> {
  try {
    const user = await UserModel.findById(userId);
    if (!user) {
      throw new NotFoundError('User not found');
    }
    return user;
  } catch (error) {
    if (error instanceof NotFoundError) {
      throw error;
    }
    throw new ApplicationError('Failed to fetch user data', error);
  }
}
```

### Error Handling

```typescript
// Custom error classes
class ApplicationError extends Error {
  constructor(message: string, public cause?: Error) {
    super(message);
    this.name = 'ApplicationError';
  }
}

// Error middleware
const errorHandler: ErrorRequestHandler = (err, req, res, next) => {
  logger.error(err);
  
  if (err instanceof NotFoundError) {
    return res.status(404).json({ error: err.message });
  }
  
  res.status(500).json({ error: 'Internal server error' });
};
```

### Dependency Injection

```typescript
// Service with dependency injection
class UserService {
  constructor(
    private userRepository: UserRepository,
    private authService: AuthService
  ) {}

  async createUser(userData: UserDTO): Promise<User> {
    const hashedPassword = await this.authService.hashPassword(userData.password);
    return this.userRepository.create({
      ...userData,
      password: hashedPassword
    });
  }
}
```

### API Routes

```typescript
// Route definition with validation
import { Router } from 'express';
import { validateRequest } from '../middleware/validation';
import { createUserSchema } from '../schemas/user';

const router = Router();

router.post(
  '/users',
  validateRequest(createUserSchema),
  async (req, res, next) => {
    try {
      const user = await userService.createUser(req.body);
      res.status(201).json(user);
    } catch (error) {
      next(error);
    }
  }
);
```

### Configuration Management

```typescript
// Environment-based configuration
import dotenv from 'dotenv';
import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']),
  PORT: z.string().transform(Number),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32)
});

const config = envSchema.parse(process.env);
```

### Database Operations

```typescript
// Repository pattern
class UserRepository {
  async findByEmail(email: string): Promise<User | null> {
    return prisma.user.findUnique({
      where: { email },
      include: { profile: true }
    });
  }

  async create(data: CreateUserDTO): Promise<User> {
    return prisma.user.create({
      data,
      include: { profile: true }
    });
  }
}
```

### Testing

```typescript
// Jest test example
describe('UserService', () => {
  let userService: UserService;
  let mockRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockRepository = {
      findByEmail: jest.fn(),
      create: jest.fn()
    };
    userService = new UserService(mockRepository);
  });

  it('should create user successfully', async () => {
    const userData = { email: 'test@example.com' };
    await userService.createUser(userData);
    expect(mockRepository.create).toHaveBeenCalledWith(userData);
  });
});
```

## Common Dependencies

```json
{
  "dependencies": {
    "express": "^4.18.2",
    "prisma": "^4.13.0",
    "@prisma/client": "^4.13.0",
    "zod": "^3.21.4",
    "jsonwebtoken": "^9.0.0",
    "bcrypt": "^5.1.0"
  },
  "devDependencies": {
    "typescript": "^5.0.4",
    "@types/express": "^4.17.17",
    "jest": "^29.5.0",
    "@types/jest": "^29.5.1",
    "ts-jest": "^29.1.0"
  }
}
```

## Security Best Practices

- Use Helmet middleware
- Implement rate limiting
- Validate input with Zod
- Use secure sessions
- Implement CORS properly
- Use security headers
- Hash passwords with bcrypt

## Performance Optimization

- Use clustering
- Implement caching
- Database indexing
- Query optimization
- Load balancing
- Memory management

## Monitoring & Logging

```typescript
// Winston logger setup
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});
```

## Development Workflow

1. Use TypeScript
2. Follow Git flow
3. Write tests first
4. Document APIs
5. Review code
6. Use linting/formatting

## Production Deployment

- Use Docker containers
- Implement CI/CD
- Monitor performance
- Set up alerting
- Regular backups
- Security scanning

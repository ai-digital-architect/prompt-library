# Security Best Practices

## Authentication & Authorization

### JWT Implementation

```typescript
// JWT Service Example
class JWTService {
  private readonly secret: string;
  
  constructor(secret: string) {
    this.secret = secret;
  }
  
  generateToken(payload: JWTPayload): string {
    return jwt.sign(payload, this.secret, {
      expiresIn: '24h',
      algorithm: 'HS256'
    });
  }
  
  verifyToken(token: string): JWTPayload {
    return jwt.verify(token, this.secret) as JWTPayload;
  }
}
```

### OAuth2 Integration

- Implement proper OAuth flows
- Secure client credentials
- Use state parameter
- Validate redirect URIs
- Implement PKCE for mobile

## Data Protection

### Encryption

- Use strong algorithms (AES-256)
- Proper key management
- Secure key storage
- Data encryption at rest
- TLS for data in transit

### Password Security

```typescript
// Password hashing example
async function hashPassword(password: string): Promise<string> {
  const salt = await bcrypt.genSalt(12);
  return bcrypt.hash(password, salt);
}

async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}
```

## API Security

### Input Validation

```typescript
// Request validation with Zod
const userSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  role: z.enum(['user', 'admin'])
});

const validateUser = (data: unknown) => userSchema.parse(data);
```

### Rate Limiting

```typescript
// Rate limiting middleware
import rateLimit from 'express-rate-limit';

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP'
});
```

## Infrastructure Security

### Network Security

- Use WAF
- Implement VPC
- Network segmentation
- Security groups
- DDoS protection

### Cloud Security

- IAM best practices
- Least privilege access
- Regular audits
- Enable logging
- Monitor activities

## Security Headers

```typescript
// Helmet configuration
import helmet from 'helmet';

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));
```

## CORS Configuration

```typescript
// CORS setup
import cors from 'cors';

app.use(cors({
  origin: ['https://trusted-domain.com'],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
  maxAge: 86400
}));
```

## Security Monitoring

### Logging

```typescript
// Secure logging
const securityLogger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'security-service' },
  transports: [
    new winston.transports.File({ 
      filename: 'security.log',
      level: 'info'
    })
  ]
});
```

### Audit Trail

- Log security events
- Track user actions
- Monitor API access
- Alert on anomalies
- Regular review

## Security Testing

### Automated Scanning

- SAST tools
- DAST testing
- Dependency scanning
- Container scanning
- Infrastructure scanning

### Penetration Testing

- Regular pen testing
- Vulnerability assessment
- Security review
- Bug bounty program
- Security training

## Incident Response

### Response Plan

1. Detection
2. Analysis
3. Containment
4. Eradication
5. Recovery
6. Lessons learned

### Security Patches

- Regular updates
- Patch management
- Version control
- Dependency updates
- Security advisories

## Compliance

### Standards

- GDPR compliance
- HIPAA requirements
- PCI DSS standards
- SOC2 compliance
- ISO 27001

### Data Governance

- Data classification
- Access controls
- Data retention
- Privacy policies
- Consent management

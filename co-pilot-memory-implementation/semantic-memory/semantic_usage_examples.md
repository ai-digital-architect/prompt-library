# Semantic Memory Usage Examples & Scenarios

## Real-World Implementation Scenarios

These examples demonstrate how semantic memory transforms GitHub Copilot from a generic assistant into a knowledgeable team member that consistently applies your project's established facts, standards, and patterns.

## Scenario 1: Architecture Decision Support

### The Situation
Your team needs to decide how to implement caching for a new feature that serves user preferences.

### Without Semantic Memory
```
User: "What's the best caching strategy for user preferences?"

Generic Copilot: "There are several caching strategies you could consider:
1. In-memory caching with Redis
2. Database-level caching
3. Application-level caching
4. CDN caching

Each has trade-offs in terms of performance, complexity, and consistency. Consider your specific requirements for cache invalidation, data consistency, and performance needs..."
```

### With Semantic Memory
```
User: "What's the best caching strategy for user preferences?"

Semantic-Enhanced Copilot: "Based on your established architecture standards and constraints:

**Recommended Approach: Redis-based distributed caching**

This aligns with your documented architecture patterns:

**Architecture Compliance**:
- ✅ **Service Boundary Respect**: User preferences are owned by the UserService, so caching should be implemented there
- ✅ **Performance Requirements**: Your documented SLA requires <200ms response time for user data - Redis caching meets this
- ✅ **Scalability Standards**: Supports your target of 10k concurrent users across multiple service instances

**Implementation per your standards**:
```javascript
// Following your established caching patterns
const cacheKey = `user:preferences:${userId}`;
const cached = await redis.get(cacheKey);

if (cached) {
  return JSON.parse(cached);
}

const preferences = await userRepository.getPreferences(userId);
await redis.setex(cacheKey, 3600, JSON.stringify(preferences)); // 1-hour TTL per your standards
return preferences;
```

**Business Rule Compliance**:
- Cache invalidation on preference updates (required by your data consistency rules)
- User data encryption in cache (required by your security standards)
- Audit logging for cache operations (required by your compliance standards)

**Integration Pattern**:
Uses your established Redis configuration and follows your documented error handling patterns for cache failures.

Would you like me to implement this following your specific UserService patterns and testing standards?"
```

### The Semantic Context Applied
- **Architecture Facts**: Service boundaries, performance requirements, scalability targets
- **Technical Standards**: Caching patterns, error handling, security requirements
- **Business Rules**: Data consistency, audit logging, compliance requirements
- **Integration Patterns**: Redis configuration, service communication standards

## Scenario 2: Business Logic Implementation

### The Situation
A developer needs to implement a new user registration validation process.

### Without Semantic Memory
```
User: "How should I validate user registration data?"

Generic Copilot: "For user registration validation, you should consider:
1. Email format validation
2. Password strength requirements
3. Username uniqueness checking
4. Required field validation
5. Data sanitization

Here's a basic validation example:
```javascript
function validateRegistration(userData) {
  if (!userData.email || !isValidEmail(userData.email)) {
    return { valid: false, error: 'Invalid email' };
  }
  // Additional validation...
}
```
```

### With Semantic Memory
```
User: "How should I validate user registration data?"

Semantic-Enhanced Copilot: "Based on your documented business rules and validation standards:

**Required Validation Implementation**:

```javascript
// Following your established validation patterns
async function validateUserRegistration(userData) {
  const validationResult = {
    valid: true,
    errors: [],
    warnings: []
  };

  // Business Rule #1: Email domain restrictions
  if (!userData.email || !isValidBusinessEmail(userData.email)) {
    validationResult.errors.push('Email must be from approved business domains');
    validationResult.valid = false;
  }

  // Business Rule #2: Username format (documented standard)
  if (!userData.username || !USERNAME_PATTERN.test(userData.username)) {
    validationResult.errors.push('Username must be 3-20 characters, alphanumeric and underscores only');
    validationResult.valid = false;
  }

  // Business Rule #3: Password compliance (security standard)
  const passwordValidation = validatePasswordCompliance(userData.password);
  if (!passwordValidation.valid) {
    validationResult.errors.push(...passwordValidation.errors);
    validationResult.valid = false;
  }

  // Business Rule #4: Uniqueness checking (data integrity requirement)
  const existingUser = await userRepository.findByEmailOrUsername(
    userData.email, 
    userData.username
  );
  if (existingUser) {
    validationResult.errors.push('Email or username already exists');
    validationResult.valid = false;
  }

  // Business Rule #5: Age verification (compliance requirement)
  if (!userData.dateOfBirth || !isValidAge(userData.dateOfBirth)) {
    validationResult.errors.push('Must be 18 years or older');
    validationResult.valid = false;
  }

  // Audit logging (required by your compliance standards)
  await auditLogger.log('USER_REGISTRATION_VALIDATION', {
    email: userData.email,
    result: validationResult.valid,
    errors: validationResult.errors
  });

  return validationResult;
}

// Helper functions following your established patterns
function isValidBusinessEmail(email) {
  // Uses your documented approved domain list
  const approvedDomains = config.business.approvedEmailDomains;
  const domain = email.split('@')[1];
  return EMAIL_PATTERN.test(email) && approvedDomains.includes(domain);
}

function validatePasswordCompliance(password) {
  // Implements your documented password policy
  return passwordValidator.validate(password, {
    minLength: 12,            // Per your security standards
    requireUppercase: true,   // Required by your policy
    requireNumbers: true,     // Required by your policy
    requireSpecialChars: true, // Required by your policy
    preventCommonPasswords: true // Security requirement
  });
}
```

**Integration Requirements**:
- Error responses follow your standard API error format
- Success responses include user activation workflow trigger
- Database transaction follows your data consistency patterns
- Email verification uses your established notification service

**Testing Requirements** (per your standards):
- Unit tests for each validation rule
- Integration tests for database uniqueness checking
- Security tests for injection prevention
- Performance tests for validation speed

Would you like me to generate the corresponding test suite following your testing standards?"
```

### The Semantic Context Applied
- **Business Rules**: Email domain restrictions, age requirements, uniqueness constraints
- **Security Standards**: Password policy, audit logging, data sanitization
- **Integration Patterns**: Database access, notification service, API response format
- **Testing Standards**: Required test coverage and types

## Scenario 3: API Design Consistency

### The Situation
A developer needs to create a new API endpoint for retrieving order history.

### Without Semantic Memory
```
User: "How should I structure an API endpoint for getting user order history?"

Generic Copilot: "Here's a basic structure for an order history API:

```javascript
app.get('/api/orders', async (req, res) => {
  try {
    const orders = await getOrderHistory(req.user.id);
    res.json({ orders });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});
```

Consider adding pagination, filtering, and proper error handling."
```

### With Semantic Memory
```
User: "How should I structure an API endpoint for getting user order history?"

Semantic-Enhanced Copilot: "Based on your established API design standards and patterns:

**Endpoint Structure** (following your REST conventions):
```
GET /api/v2/users/{userId}/orders
```

**Implementation** (following your established patterns):

```javascript
// Route definition following your API versioning standard
router.get('/v2/users/:userId/orders', 
  authenticationMiddleware,      // Required by your security standards
  authorizationMiddleware(['read:orders']), // Your permission model
  validateRequestParams,         // Your validation pattern
  paginationMiddleware,          // Your pagination standard
  async (req, res) => {
    try {
      // Input validation per your standards
      const validationResult = validateOrderHistoryRequest(req);
      if (!validationResult.valid) {
        return res.status(400).json({
          error: 'VALIDATION_ERROR',
          message: 'Invalid request parameters',
          details: validationResult.errors,
          requestId: req.requestId    // Your tracing standard
        });
      }

      // Authorization check per your business rules
      if (req.user.id !== req.params.userId && !req.user.hasRole('admin')) {
        return res.status(403).json({
          error: 'ACCESS_DENIED',
          message: 'Cannot access other user\'s order history',
          requestId: req.requestId
        });
      }

      // Service call following your service layer pattern
      const orderHistory = await orderService.getOrderHistory({
        userId: req.params.userId,
        pagination: req.pagination,    // Your pagination format
        filters: req.query.filters,    // Your filtering standard
        sortBy: req.query.sortBy || 'createdAt:desc' // Your sorting default
      });

      // Response format per your API standards
      res.json({
        data: orderHistory.orders,
        meta: {
          pagination: {
            page: req.pagination.page,
            pageSize: req.pagination.pageSize,
            totalItems: orderHistory.totalCount,
            totalPages: Math.ceil(orderHistory.totalCount / req.pagination.pageSize)
          },
          filters: req.query.filters,
          sortBy: req.query.sortBy
        },
        requestId: req.requestId
      });

      // Audit logging per your compliance requirements
      await auditLogger.log('ORDER_HISTORY_ACCESS', {
        userId: req.params.userId,
        accessedBy: req.user.id,
        recordCount: orderHistory.orders.length,
        requestId: req.requestId
      });

    } catch (error) {
      // Error handling following your error management standard
      logger.error('Order history retrieval failed', {
        userId: req.params.userId,
        error: error.message,
        stack: error.stack,
        requestId: req.requestId
      });

      // Your standard error response format
      const errorResponse = errorHandler.formatError(error, req.requestId);
      res.status(errorResponse.statusCode).json(errorResponse);
    }
  }
);

// Request validation following your validation patterns
function validateOrderHistoryRequest(req) {
  const schema = {
    userId: { type: 'uuid', required: true },
    page: { type: 'integer', min: 1, default: 1 },
    pageSize: { type: 'integer', min: 1, max: 100, default: 20 },
    status: { type: 'string', enum: ['pending', 'completed', 'cancelled'], optional: true },
    startDate: { type: 'date', optional: true },
    endDate: { type: 'date', optional: true }
  };

  return requestValidator.validate(req.params, req.query, schema);
}
```

**API Documentation** (per your documentation standards):
```yaml
paths:
  /api/v2/users/{userId}/orders:
    get:
      summary: Retrieve user order history
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
            format: uuid
        - name: page
          in: query
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: pageSize
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
        - name: status
          in: query
          schema:
            type: string
            enum: [pending, completed, cancelled]
      responses:
        200:
          description: Order history retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderHistoryResponse'
        400:
          $ref: '#/components/responses/ValidationError'
        403:
          $ref: '#/components/responses/AccessDenied'
        500:
          $ref: '#/components/responses/InternalError'
```

**Testing Requirements** (following your API testing standards):
- Unit tests for validation logic
- Integration tests for service layer interaction
- Authorization tests for access control
- Performance tests for response time (<200ms requirement)
- Security tests for injection prevention

**Performance Considerations**:
- Database query uses your established indexing strategy
- Response caching follows your caching standards (5-minute TTL for order data)
- Pagination prevents large result set performance issues

This implementation follows all your documented API standards: authentication, authorization, validation, error handling, audit logging, and response formatting."
```

### The Semantic Context Applied
- **API Standards**: REST conventions, versioning, response format, documentation requirements
- **Security Standards**: Authentication, authorization, access control patterns
- **Performance Requirements**: Response time limits, pagination standards, caching strategy
- **Compliance Standards**: Audit logging, error handling, validation requirements

## Scenario 4: Database Schema Design

### The Situation
The team needs to add a new table for storing user notifications.

### Without Semantic Memory
```
User: "How should I design a database table for user notifications?"

Generic Copilot: "Here's a basic notifications table design:

```sql
CREATE TABLE notifications (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  title VARCHAR(255) NOT NULL,
  message TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  read_at TIMESTAMP NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

Consider adding indexes for performance and additional fields as needed."
```

### With Semantic Memory
```
User: "How should I design a database table for user notifications?"

Semantic-Enhanced Copilot: "Based on your established database design standards and business requirements:

**Table Schema** (following your naming conventions and design patterns):

```sql
-- Notifications table following your database standards
CREATE TABLE user_notifications (
  -- Primary key following your UUID standard
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Foreign key following your relationship patterns
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Notification categorization per your business rules
  notification_type VARCHAR(50) NOT NULL CHECK (
    notification_type IN (
      'ORDER_UPDATE', 'PAYMENT_CONFIRMATION', 'SECURITY_ALERT',
      'PROMOTIONAL', 'SYSTEM_MAINTENANCE', 'ACCOUNT_UPDATE'
    )
  ),
  
  -- Content fields following your text storage standards
  title VARCHAR(200) NOT NULL,
  message TEXT NOT NULL,
  action_url VARCHAR(500) NULL,
  
  -- Priority level per your business requirements
  priority VARCHAR(20) NOT NULL DEFAULT 'normal' CHECK (
    priority IN ('low', 'normal', 'high', 'urgent')
  ),
  
  -- Delivery channels per your notification system design
  delivery_channels JSONB NOT NULL DEFAULT '["in_app"]'::jsonb CHECK (
    jsonb_array_length(delivery_channels) > 0
  ),
  
  -- Status tracking per your workflow requirements
  status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (
    status IN ('pending', 'delivered', 'read', 'dismissed', 'failed')
  ),
  
  -- Timestamps following your audit trail standards
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  delivered_at TIMESTAMP WITH TIME ZONE NULL,
  read_at TIMESTAMP WITH TIME ZONE NULL,
  dismissed_at TIMESTAMP WITH TIME ZONE NULL,
  expires_at TIMESTAMP WITH TIME ZONE NULL,
  
  -- Audit fields per your data governance requirements
  created_by UUID NULL REFERENCES users(id),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_by UUID NULL REFERENCES users(id),
  
  -- Soft delete support per your data retention policy
  deleted_at TIMESTAMP WITH TIME ZONE NULL,
  deleted_by UUID NULL REFERENCES users(id)
);

-- Indexes following your performance optimization standards
CREATE INDEX idx_user_notifications_user_id_status 
  ON user_notifications(user_id, status) 
  WHERE deleted_at IS NULL;

CREATE INDEX idx_user_notifications_created_at 
  ON user_notifications(created_at DESC) 
  WHERE deleted_at IS NULL;

CREATE INDEX idx_user_notifications_type_priority 
  ON user_notifications(notification_type, priority) 
  WHERE deleted_at IS NULL;

CREATE INDEX idx_user_notifications_expires_at 
  ON user_notifications(expires_at) 
  WHERE expires_at IS NOT NULL AND deleted_at IS NULL;

-- Partial index for unread notifications (performance optimization)
CREATE INDEX idx_user_notifications_unread 
  ON user_notifications(user_id, created_at DESC) 
  WHERE status IN ('pending', 'delivered') AND deleted_at IS NULL;

-- Update trigger following your audit trail standards
CREATE TRIGGER trg_user_notifications_updated_at
  BEFORE UPDATE ON user_notifications
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Cleanup trigger per your data retention policy
CREATE TRIGGER trg_user_notifications_cleanup
  AFTER UPDATE ON user_notifications
  FOR EACH ROW
  WHEN (NEW.status = 'dismissed' AND OLD.status != 'dismissed')
  EXECUTE FUNCTION schedule_notification_cleanup();
```

**Business Rule Enforcement**:
```sql
-- Constraint: Notifications cannot be marked as read before being delivered
ALTER TABLE user_notifications ADD CONSTRAINT chk_read_after_delivered
  CHECK (read_at IS NULL OR delivered_at IS NOT NULL);

-- Constraint: Dismissed notifications cannot be unread
ALTER TABLE user_notifications ADD CONSTRAINT chk_dismissed_state
  CHECK (dismissed_at IS NULL OR read_at IS NOT NULL);

-- Constraint: Expired notifications should be automatically dismissed
CREATE OR REPLACE FUNCTION enforce_expiration_policy()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.expires_at IS NOT NULL AND NEW.expires_at <= NOW() THEN
    NEW.status := 'failed';
    NEW.updated_at := NOW();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_enforce_expiration
  BEFORE INSERT OR UPDATE ON user_notifications
  FOR EACH ROW
  EXECUTE FUNCTION enforce_expiration_policy();
```

**Data Access Patterns** (following your repository pattern):
```javascript
// Repository implementation following your data access standards
class NotificationRepository {
  async getUnreadNotifications(userId, limit = 20) {
    // Uses your established query patterns
    return await this.db.query(`
      SELECT id, notification_type, title, message, action_url, 
             priority, created_at, expires_at
      FROM user_notifications
      WHERE user_id = $1 
        AND status IN ('pending', 'delivered')
        AND deleted_at IS NULL
        AND (expires_at IS NULL OR expires_at > NOW())
      ORDER BY priority DESC, created_at DESC
      LIMIT $2
    `, [userId, limit]);
  }

  async markAsRead(notificationId, userId) {
    // Follows your update patterns with audit trail
    const result = await this.db.query(`
      UPDATE user_notifications 
      SET status = 'read',
          read_at = NOW(),
          updated_at = NOW()
      WHERE id = $1 
        AND user_id = $2
        AND status = 'delivered'
        AND deleted_at IS NULL
      RETURNING id
    `, [notificationId, userId]);

    if (result.rowCount === 0) {
      throw new NotificationNotFoundError('Notification not found or already processed');
    }

    return result.rows[0];
  }
}
```

**Migration Script** (following your migration standards):
```sql
-- Migration: 2024_01_15_001_create_user_notifications_table.sql
-- Description: Add user notifications table with comprehensive audit trail

BEGIN;

-- Create table with all constraints and indexes
[TABLE CREATION CODE FROM ABOVE]

-- Seed initial notification types configuration
INSERT INTO notification_type_config (type, display_name, default_priority, retention_days)
VALUES 
  ('ORDER_UPDATE', 'Order Updates', 'normal', 90),
  ('PAYMENT_CONFIRMATION', 'Payment Confirmations', 'high', 365),
  ('SECURITY_ALERT', 'Security Alerts', 'urgent', 365),
  ('PROMOTIONAL', 'Promotional Messages', 'low', 30),
  ('SYSTEM_MAINTENANCE', 'System Maintenance', 'normal', 7),
  ('ACCOUNT_UPDATE', 'Account Updates', 'normal', 180);

-- Grant permissions per your security model
GRANT SELECT, INSERT, UPDATE ON user_notifications TO app_user;
GRANT USAGE ON SEQUENCE user_notifications_id_seq TO app_user;

COMMIT;
```

**Performance Considerations**:
- Indexes optimized for your query patterns (user lookups, status filtering)
- Partitioning strategy follows your data archiving rules (monthly partitions)
- Cleanup procedures align with your data retention policy
- Query performance targets: <50ms for user notification retrieval

This design follows all your established database standards: naming conventions, data types, indexing strategy, audit trails, business rule enforcement, and performance optimization patterns."
```

### The Semantic Context Applied
- **Database Standards**: Naming conventions, data types, constraint patterns, indexing strategy
- **Business Rules**: Notification types, priority levels, status workflow, retention policies
- **Performance Standards**: Query optimization, indexing strategy, partition management
- **Audit Requirements**: Timestamp tracking, user tracking, soft delete patterns

## Scenario 5: Security Implementation

### The Situation
A developer needs to implement authentication middleware for API endpoints.

### Without Semantic Memory
```
User: "How should I implement authentication middleware for our API?"

Generic Copilot: "Here's a basic authentication middleware:

```javascript
function authMiddleware(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

You might want to add token refresh logic and better error handling."
```

### With Semantic Memory
```
User: "How should I implement authentication middleware for our API?"

Semantic-Enhanced Copilot: "Based on your established security standards and compliance requirements:

**Authentication Middleware** (following your OAuth2 + JWT security model):

```javascript
// Authentication middleware following your security standards
const authenticationMiddleware = async (req, res, next) => {
  try {
    // Extract token following your header standards
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return sendSecurityError(res, 'MISSING_TOKEN', 
        'Authentication token required', req.requestId);
    }

    const token = authHeader.substring(7); // Remove 'Bearer ' prefix

    // Token validation per your security standards
    let decodedToken;
    try {
      // Use your established JWT configuration
      decodedToken = jwt.verify(token, config.security.jwtSecret, {
        algorithms: ['RS256'],          // Your required algorithm
        issuer: config.security.issuer, // Your token issuer
        audience: config.security.audience, // Your API audience
        maxAge: '15m'                   // Your token lifetime limit
      });
    } catch (jwtError) {
      // Security audit logging per your compliance requirements
      await securityAuditLogger.log('INVALID_TOKEN_ATTEMPT', {
        ip: req.ip,
        userAgent: req.get('User-Agent'),
        token: token.substring(0, 10) + '...', // Partial token for audit
        error: jwtError.message,
        requestId: req.requestId
      });

      if (jwtError.name === 'TokenExpiredError') {
        return sendSecurityError(res, 'TOKEN_EXPIRED', 
          'Authentication token has expired', req.requestId);
      }

      return sendSecurityError(res, 'INVALID_TOKEN', 
        'Invalid authentication token', req.requestId);
    }

    // User validation per your business rules
    const user = await userService.getUserById(decodedToken.sub);
    if (!user || user.status !== 'active') {
      await securityAuditLogger.log('INACTIVE_USER_ATTEMPT', {
        userId: decodedToken.sub,
        ip: req.ip,
        requestId: req.requestId
      });
      return sendSecurityError(res, 'USER_INACTIVE', 
        'User account is not active', req.requestId);
    }

    // Session validation per your security policy
    const session = await sessionService.validateSession(decodedToken.sessionId);
    if (!session || session.status !== 'valid') {
      await securityAuditLogger.log('INVALID_SESSION_ATTEMPT', {
        userId: user.id,
        sessionId: decodedToken.sessionId,
        ip: req.ip,
        requestId: req.requestId
      });
      return sendSecurityError(res, 'SESSION_INVALID', 
        'Session is no longer valid', req.requestId);
    }

    // Rate limiting per your security standards
    const rateLimitResult = await rateLimiter.checkLimit(user.id, req.ip);
    if (!rateLimitResult.allowed) {
      await securityAuditLogger.log('RATE_LIMIT_EXCEEDED', {
        userId: user.id,
        ip: req.ip,
        requestsCount: rateLimitResult.requestsCount,
        requestId: req.requestId
      });
      return res.status(429).json({
        error: 'RATE_LIMIT_EXCEEDED',
        message: 'Too many requests',
        retryAfter: rateLimitResult.resetTime,
        requestId: req.requestId
      });
    }

    // Multi-factor authentication check per your security policy
    if (decodedToken.requiresMFA && !decodedToken.mfaVerified) {
      return sendSecurityError(res, 'MFA_REQUIRED', 
        'Multi-factor authentication required', req.requestId);
    }

    // Device trust validation per your security standards
    const deviceFingerprint = req.headers['x-device-fingerprint'];
    if (config.security.requireDeviceTrust && deviceFingerprint) {
      const deviceTrusted = await deviceTrustService.isDeviceTrusted(
        user.id, deviceFingerprint
      );
      if (!deviceTrusted) {
        await securityAuditLogger.log('UNTRUSTED_DEVICE_ACCESS', {
          userId: user.id,
          deviceFingerprint,
          ip: req.ip,
          requestId: req.requestId
        });
        // Don't block but flag for additional monitoring
        req.deviceTrusted = false;
      } else {
        req.deviceTrusted = true;
      }
    }

    // Attach user context following your request context pattern
    req.user = {
      id: user.id,
      email: user.email,
      roles: user.roles,
      permissions: user.permissions,
      organizationId: user.organizationId,
      sessionId: decodedToken.sessionId,
      tokenIssuedAt: decodedToken.iat,
      mfaVerified: decodedToken.mfaVerified || false
    };

    // Update session activity per your session management requirements
    await sessionService.updateLastActivity(decodedToken.sessionId, {
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      endpoint: req.originalUrl
    });

    // Success audit logging per your compliance requirements
    await securityAuditLogger.log('AUTHENTICATION_SUCCESS', {
      userId: user.id,
      ip: req.ip,
      endpoint: req.originalUrl,
      requestId: req.requestId
    });

    next();

  } catch (error) {
    // Error handling per your security incident response
    await securityIncidentLogger.log('AUTHENTICATION_ERROR', {
      error: error.message,
      stack: error.stack,
      ip: req.ip,
      requestId: req.requestId
    });

    return sendSecurityError(res, 'AUTHENTICATION_ERROR', 
      'Authentication failed', req.requestId);
  }
};

// Helper function following your error response standards
function sendSecurityError(res, errorCode, message, requestId) {
  return res.status(401).json({
    error: errorCode,
    message: message,
    timestamp: new Date().toISOString(),
    requestId: requestId,
    // No sensitive information in error responses per your security policy
  });
}

// Authorization middleware following your RBAC model
const authorizationMiddleware = (requiredPermissions = []) => {
  return async (req, res, next) => {
    try {
      if (!req.user) {
        return sendSecurityError(res, 'NO_USER_CONTEXT', 
          'User context not found', req.requestId);
      }

      // Permission checking per your RBAC implementation
      const userPermissions = new Set(req.user.permissions || []);
      const hasPermission = requiredPermissions.every(permission => {
        // Support for hierarchical permissions per your permission model
        return userPermissions.has(permission) || 
               userPermissions.has(permission.split(':')[0] + ':*') ||
               userPermissions.has('*');
      });

      if (!hasPermission) {
        await securityAuditLogger.log('AUTHORIZATION_DENIED', {
          userId: req.user.id,
          requiredPermissions,
          userPermissions: Array.from(userPermissions),
          endpoint: req.originalUrl,
          requestId: req.requestId
        });

        return res.status(403).json({
          error: 'INSUFFICIENT_PERMISSIONS',
          message: 'Insufficient permissions to access this resource',
          requiredPermissions: requiredPermissions,
          requestId: req.requestId
        });
      }

      // Resource-level authorization per your data access rules
      if (req.params.organizationId && 
          req.user.organizationId !== req.params.organizationId &&
          !userPermissions.has('admin:*')) {
        await securityAuditLogger.log('CROSS_ORGANIZATION_ACCESS_DENIED', {
          userId: req.user.id,
          userOrganization: req.user.organizationId,
          requestedOrganization: req.params.organizationId,
          endpoint: req.originalUrl,
          requestId: req.requestId
        });

        return res.status(403).json({
          error: 'CROSS_ORGANIZATION_ACCESS_DENIED',
          message: 'Cannot access resources from different organization',
          requestId: req.requestId
        });
      }

      next();

    } catch (error) {
      await securityIncidentLogger.log('AUTHORIZATION_ERROR', {
        error: error.message,
        userId: req.user?.id,
        endpoint: req.originalUrl,
        requestId: req.requestId
      });

      return res.status(500).json({
        error: 'AUTHORIZATION_ERROR',
        message: 'Authorization check failed',
        requestId: req.requestId
      });
    }
  };
};
```

**Usage Examples** (following your API security patterns):

```javascript
// Public endpoint (no authentication required)
router.get('/api/v2/health', healthController.getHealth);

// Authenticated endpoint (basic authentication required)
router.get('/api/v2/profile', 
  authenticationMiddleware, 
  profileController.getProfile
);

// Authorized endpoint (specific permissions required)
router.get('/api/v2/admin/users', 
  authenticationMiddleware,
  authorizationMiddleware(['admin:users:read']),
  adminController.getUsers
);

// Organization-scoped endpoint (resource-level authorization)
router.get('/api/v2/organizations/:organizationId/data',
  authenticationMiddleware,
  authorizationMiddleware(['organization:data:read']),
  dataController.getOrganizationData
);

// High-security endpoint (MFA + additional validation)
router.post('/api/v2/admin/security/reset',
  authenticationMiddleware,
  requireMFAVerification,
  authorizationMiddleware(['admin:security:write']),
  securityController.resetSecurity
);
```

**Security Configuration** (per your environment standards):

```javascript
// Security configuration following your standards
const securityConfig = {
  jwt: {
    secret: process.env.JWT_SECRET,           // Your secret management
    algorithm: 'RS256',                       // Your required algorithm
    issuer: process.env.JWT_ISSUER,          // Your token issuer
    audience: process.env.JWT_AUDIENCE,       // Your API audience
    expiresIn: '15m'                         // Your token lifetime
  },
  session: {
    maxAge: 8 * 60 * 60 * 1000,             // 8 hours per your policy
    renewThreshold: 30 * 60 * 1000,          // 30 minutes per your policy
    maxConcurrentSessions: 3                  // Per your security policy
  },
  rateLimit: {
    windowMs: 15 * 60 * 1000,                // 15 minutes per your policy
    maxRequests: 100,                         // Per your rate limiting rules
    skipSuccessfulRequests: false             // Count all requests per policy
  },
  mfa: {
    requiredForRoles: ['admin', 'finance'],   // Per your security requirements
    gracePeriod: 24 * 60 * 60 * 1000        // 24 hours per your policy
  }
};
```

**Testing Requirements** (following your security testing standards):
- Authentication bypass attempts
- Token manipulation and forgery tests
- Permission escalation tests
- Rate limiting validation
- Session management security tests
- Cross-organization access prevention tests

**Compliance Features**:
- ✅ **Audit Logging**: All authentication/authorization events logged
- ✅ **Session Management**: Secure session handling per your policy
- ✅ **Rate Limiting**: Protection against brute force attacks
- ✅ **MFA Support**: Multi-factor authentication for sensitive operations
- ✅ **Device Trust**: Device fingerprinting and trust validation
- ✅ **Error Handling**: Secure error responses without information leakage

This implementation follows all your documented security standards: OAuth2/JWT implementation, RBAC authorization, audit logging, session management, and compliance requirements."
```

### The Semantic Context Applied
- **Security Standards**: OAuth2/JWT configuration, RBAC model, session management policies
- **Compliance Requirements**: Audit logging, error handling, data protection standards
- **Business Rules**: Organization boundaries, role-based access, MFA requirements
- **Technical Standards**: Error response format, logging patterns, configuration management

## Implementation Guidelines

### Setting Up Contextual Knowledge Capture

**Daily Knowledge Validation**:
```markdown
# Daily Semantic Memory Health Check
**Date**: [Today's date]
**Knowledge Areas Validated**: [List of areas checked]
**New Facts Added**: [Any new factual knowledge]
**Inconsistencies Found**: [Any contradictions discovered]
**Application Effectiveness**: [How well knowledge was applied]
**Improvement Areas**: [Areas needing attention]
```

**Weekly Knowledge Review**:
```markdown
# Weekly Semantic Memory Review
**Week of**: [Date range]
**Knowledge Accuracy Assessment**: [Accuracy validation results]
**Application Success Rate**: [How often knowledge was correctly applied]
**Standard Compliance**: [Compliance with documented standards]
**Integration Effectiveness**: [How well semantic memory enhanced other systems]
**Knowledge Gaps Identified**: [Areas needing additional documentation]
**Action Items**: [Knowledge improvements needed]
```

### Knowledge Application Triggers

**Automatic Knowledge Application**:
- Architecture and design decisions
- Business rule implementation
- Security and compliance requirements
- API design and integration patterns
- Database schema and design decisions

**Manual Knowledge Invocation**:
```
To explicitly request semantic memory context:
"Based on our established [architecture/business rules/standards]..."
"Following our documented [patterns/requirements/policies]..."
"According to our [technical standards/security requirements]..."
"Per our established [design principles/business logic]..."
```

This semantic memory system ensures that every aspect of development assistance is grounded in your project's established facts, standards, and patterns, providing consistent, accurate, and compliant guidance that aligns with your organization's knowledge and requirements.
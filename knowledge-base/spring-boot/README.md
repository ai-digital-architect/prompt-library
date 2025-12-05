# Spring Boot Development Guidelines

## Project Structure

```
src/main/java/com/example/project/
├── config/         # Configuration classes
├── controller/     # REST controllers
├── model/         # Domain models
├── repository/    # Data access layer
├── service/       # Business logic
├── exception/     # Custom exceptions
└── util/          # Utility classes
```

## Best Practices

### Dependency Injection

- Use constructor injection over field injection
- Keep components single-responsibility
- Use appropriate Spring stereotypes (@Service, @Repository, etc.)

### REST APIs

- Use proper HTTP methods (GET, POST, PUT, DELETE)
- Implement proper response status codes
- Use DTOs for request/response
- Version your APIs
- Document with OpenAPI/Swagger

### Error Handling

```java
@ControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<?> handleResourceNotFound(ResourceNotFoundException ex) {
        // Implementation
    }
}

```

### Security

- Use Spring Security
- Implement JWT authentication where needed
- Use HTTPS in production
- Input validation

- XSS protection
- CSRF protection

### Testing

- Unit test services and controllers
- Use @SpringBootTest for integration tests

- Mock external dependencies
- Test security configurations
- Test error scenarios

### Performance

- Use caching appropriately
- Implement pagination for large datasets
- Optimize database queries
- Use async operations where applicable

### Monitoring

- Implement actuator endpoints

- Set up proper logging
- Use tracing in microservices
- Monitor performance metrics

## Common Patterns

### Service Layer Pattern

```java
@Service
public class UserService {
    private final UserRepository userRepository;
    
    public UserService(UserRepository userRepository) {

        this.userRepository = userRepository;
    }
    
    // Service methods
}
```

### Repository Pattern

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
}
```

### Controller Pattern

```java
@RestController
@RequestMapping("/api/v1/users")
public class UserController {
    private final UserService userService;
    
    public UserController(UserService userService) {

        this.userService = userService;
    }
    
    // Controller methods
}
```

## Configuration

### Application Properties

```yaml

spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/dbname
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
  jpa:
    hibernate:
      ddl-auto: validate
```

### Security Configuration

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    // Security configuration
}
```

## Common Dependencies

```xml
<dependencies>
   
 <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>
</dependencies>
```

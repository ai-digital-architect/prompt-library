# Mermaid Diagram Examples for Spring Upgrade Documentation

## Sample Generated Diagrams

### 1. Upgrade Timeline Diagram
```mermaid
timeline
    title Spring Framework Upgrade Timeline - Project: E-Commerce API
    
    section Planning Phase
        2024-01-15 09:00 : Project Analysis Started
                         : Current Version: Spring 5.3.21
                         : Target Version: Spring 6.1.0
        2024-01-15 10:30 : Dependency Mapping Complete
                         : 45 Dependencies Analyzed
                         : 12 Breaking Changes Identified
        2024-01-15 11:45 : Risk Assessment Complete
                         : High Risk: 3 Components
                         : Medium Risk: 8 Components
        2024-01-15 12:00 : Upgrade Plan Generated
                         : 8 Phases Planned
                         : Estimated Duration: 4 hours
    
    section Execution Phase
        2024-01-15 13:00 : OpenRewrite Recipes Applied
                         : XML to Java Config Migration
                         : Deprecated API Updates
        2024-01-15 13:45 : Dependency Updates Complete
                         : Maven Dependencies Updated
                         : Version Conflicts Resolved
        2024-01-15 14:30 : Code Modernization Applied
                         : Constructor Injection Patterns
                         : Security Configuration Updates
        2024-01-15 15:15 : Test Generation Complete
                         : 23 New Unit Tests Added
                         : Coverage Increased to 84%
    
    section Validation Phase
        2024-01-15 15:30 : Build Validation Started
                         : Compilation Successful
                         : All Tests Passing
        2024-01-15 15:45 : Security Scan Complete
                         : 0 Critical Vulnerabilities
                         : 2 Low-Risk Issues Fixed
        2024-01-15 16:00 : Integration Tests Passed
                         : Application Startup: 12s
                         : All Endpoints Responding
        2024-01-15 16:15 : Final Validation Complete
                         : All Objectives Met
    
    section Documentation
        2024-01-15 16:30 : Architecture Analysis Started
                         : Component Mapping
                         : Diagram Generation
        2024-01-15 17:00 : Report Generation Complete
                         : HTML Report Generated
                         : Documentation Published
```

### 2. Execution Sequence Diagram
```mermaid
sequenceDiagram
    participant U as DevOps Engineer
    participant GH as GitHub Actions
    participant P as Planning Agent
    participant E as Execution Agent
    participant V as Validation Agent
    participant D as Documentation Agent
    participant Pages as GitHub Pages
    
    U->>GH: Trigger Upgrade Workflow
    Note over GH: spring-upgrade-enhanced.yml
    
    GH->>P: Initialize Planning Phase
    P->>P: Analyze Spring Boot E-Commerce API
    Note over P: Current: Spring 5.3.21<br/>Target: Spring 6.1.0
    
    P->>P: Map 45 Dependencies
    P->>P: Identify 12 Breaking Changes
    P->>P: Generate 8-Phase Plan
    P->>GH: Return Upgrade Plan
    
    loop Iterative Upgrade (Max 3 iterations)
        GH->>E: Execute Upgrade Phase
        
        E->>E: Apply OpenRewrite Recipes
        Note over E: - XML→Java Config<br/>- Deprecated API Updates<br/>- Security Modernization
        
        E->>E: Update Dependencies
        Note over E: - Maven POM Updates<br/>- Conflict Resolution<br/>- Version Alignment
        
        E->>E: Apply Best Practices
        Note over E: - Constructor Injection<br/>- Modern Configuration<br/>- Security Patterns
        
        E->>E: Generate Missing Tests
        Note over E: - Unit Tests: +23<br/>- Integration Tests: +8<br/>- Coverage: 65%→84%
        
        E->>V: Request Validation
        
        V->>V: Run Build & Tests
        Note over V: ✅ Compilation Success<br/>✅ All Tests Pass
        
        V->>V: Check Test Coverage
        Note over V: ✅ 84% > 80% Threshold
        
        V->>V: Security Vulnerability Scan
        Note over V: ✅ 0 Critical Vulns<br/>✅ 2 Low Issues Fixed
        
        V->>V: Application Startup Test
        Note over V: ✅ Startup: 12s<br/>✅ All Endpoints OK
        
        alt All Validations Pass
            V->>E: ✅ Validation Success
            Note over V,E: All objectives met!
        else Issues Found
            V->>E: ❌ Issues Identified
            Note over V,E: Retry with fixes
        end
    end
    
    E->>D: Generate Comprehensive Documentation
    
    D->>D: Extract Project Metadata
    Note over D: - application.yml<br/>- README.md<br/>- Project Structure
    
    D->>D: Generate Architecture Diagrams
    Note over D: - C4 Context/Container<br/>- Class/Sequence/State<br/>- Component Analysis
    
    D->>D: Create HTML Report
    Note over D: - Interactive Report<br/>- Embedded Diagrams<br/>- Metrics Dashboard
    
    D->>Pages: Deploy Documentation
    Note over Pages: GitHub Pages<br/>Public Documentation
    
    D->>GH: Documentation Complete
    
    GH->>U: Create Pull Request
    Note over GH,U: - Upgrade Summary<br/>- Metrics Dashboard<br/>- Documentation Links
    
    GH->>U: Send Email Notification
    Note over GH,U: ✅ Upgrade Completed<br/>📊 Metrics Included<br/>🔗 Report Links
```

### 3. C4 Context Diagram Example
```mermaid
C4Context
    title System Context diagram for E-Commerce API (Post-Upgrade)
    
    Person(customer, "Customer", "End users browsing and purchasing products")
    Person(admin, "Administrator", "Manages products, orders, and system configuration")
    Person(developer, "Developer", "Maintains and develops the application")
    
    System(ecommerce, "E-Commerce API", "Spring Boot 6.1.0 REST API providing e-commerce functionality with enhanced security and performance")
    
    System_Ext(payment, "Payment Gateway", "Stripe/PayPal payment processing service")
    System_Ext(inventory, "Inventory System", "External inventory management system")
    System_Ext(email, "Email Service", "SendGrid/SES for transactional emails")
    System_Ext(cdn, "CDN", "CloudFront for static asset delivery")
    System_Ext(monitoring, "Monitoring", "DataDog/New Relic for application monitoring")
    
    SystemDb_Ext(database, "PostgreSQL Database", "Primary data store for products, orders, and users")
    SystemDb_Ext(cache, "Redis Cache", "Session storage and caching layer")
    
    Rel(customer, ecommerce, "Uses", "HTTPS/REST API")
    Rel(admin, ecommerce, "Administers", "HTTPS/REST API")
    Rel(developer, ecommerce, "Develops & Monitors", "Git/CI-CD")
    
    Rel(ecommerce, payment, "Processes payments", "HTTPS/REST")
    Rel(ecommerce, inventory, "Checks stock", "HTTPS/REST")
    Rel(ecommerce, email, "Sends emails", "HTTPS/REST")
    Rel(ecommerce, cdn, "Serves assets", "HTTPS")
    Rel(ecommerce, monitoring, "Sends metrics", "HTTPS")
    
    Rel(ecommerce, database, "Reads/Writes", "JDBC/PostgreSQL")
    Rel(ecommerce, cache, "Caches data", "Redis Protocol")
    
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="2")
```

### 4. C4 Container Diagram Example
```mermaid
C4Container
    title Container diagram for E-Commerce API (Spring 6.1.0)
    
    Person(customer, "Customer", "Shopping for products")
    Person(admin, "Admin", "Managing the platform")
    
    System_Boundary(api, "E-Commerce API System") {
        Container(gateway, "API Gateway", "Spring Cloud Gateway", "Routes requests, handles CORS, rate limiting")
        Container(auth, "Auth Service", "Spring Security 6", "JWT authentication, OAuth2, role-based access")
        Container(product, "Product Service", "Spring Boot 6.1", "Product catalog, search, recommendations")
        Container(order, "Order Service", "Spring Boot 6.1", "Order processing, workflow management")
        Container(user, "User Service", "Spring Boot 6.1", "User profiles, preferences, history")
        Container(notification, "Notification Service", "Spring Boot 6.1", "Email, SMS, push notifications")
        
        ContainerDb(configserver, "Config Server", "Spring Cloud Config", "Centralized configuration management")
        ContainerDb(serviceregistry, "Service Registry", "Spring Cloud Netflix Eureka", "Service discovery and registration")
    }
    
    System_Ext(payment, "Payment Gateway", "External payment processing")
    System_Ext(inventory, "Inventory System", "Stock management system")
    
    ContainerDb(postgres, "PostgreSQL", "PostgreSQL 15", "Primary relational database")
    ContainerDb(redis, "Redis", "Redis 7", "Caching and session storage")
    ContainerDb(elasticsearch, "Elasticsearch", "Elasticsearch 8", "Product search and analytics")
    
    Rel(customer, gateway, "Uses", "HTTPS/JSON")
    Rel(admin, gateway, "Administers", "HTTPS/JSON")
    
    Rel(gateway, auth, "Authenticates", "HTTP/JWT")
    Rel(gateway, product, "Routes to", "HTTP/JSON")
    Rel(gateway, order, "Routes to", "HTTP/JSON")
    Rel(gateway, user, "Routes to", "HTTP/JSON")
    
    Rel(product, elasticsearch, "Searches", "HTTP/JSON")
    Rel(product, postgres, "Reads/Writes", "JDBC")
    Rel(order, postgres, "Reads/Writes", "JDBC")
    Rel(user, postgres, "Reads/Writes", "JDBC")
    
    Rel(order, payment, "Processes payment", "HTTPS/REST")
    Rel(product, inventory, "Checks stock", "HTTPS/REST")
    Rel(notification, user, "Gets user data", "HTTP/JSON")
    
    Rel_Back(auth, redis, "Stores sessions", "Redis Protocol")
    Rel_Back(product, redis, "Caches data", "Redis Protocol")
    
    Rel(product, configserver, "Gets config", "HTTP")
    Rel(order, configserver, "Gets config", "HTTP")
    Rel(user, configserver, "Gets config", "HTTP")
    
    Rel(product, serviceregistry, "Registers", "HTTP")
    Rel(order, serviceregistry, "Registers", "HTTP")
    Rel(user, serviceregistry, "Registers", "HTTP")
    
    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

### 5. Class Diagram Example
```mermaid
classDiagram
    %% Controllers
    class ProductController {
        <<@RestController>>
        -ProductService productService
        +getProducts(Pageable) ResponseEntity~List~Product~~
        +getProduct(Long) ResponseEntity~Product~
        +createProduct(Product) ResponseEntity~Product~
        +updateProduct(Long, Product) ResponseEntity~Product~
        +deleteProduct(Long) ResponseEntity~Void~
        +searchProducts(String) ResponseEntity~List~Product~~
    }
    
    class OrderController {
        <<@RestController>>
        -OrderService orderService
        +getOrders(Pageable) ResponseEntity~List~Order~~
        +getOrder(Long) ResponseEntity~Order~
        +createOrder(OrderRequest) ResponseEntity~Order~
        +updateOrderStatus(Long, OrderStatus) ResponseEntity~Order~
        +cancelOrder(Long) ResponseEntity~Void~
    }
    
    class UserController {
        <<@RestController>>
        -UserService userService
        +getProfile() ResponseEntity~User~
        +updateProfile(UserUpdateRequest) ResponseEntity~User~
        +getUserOrders() ResponseEntity~List~Order~~
        +changePassword(PasswordChangeRequest) ResponseEntity~Void~
    }
    
    %% Services
    class ProductService {
        <<@Service>>
        -ProductRepository productRepository
        -ElasticsearchService searchService
        -CacheManager cacheManager
        +findAll(Pageable) Page~Product~
        +findById(Long) Optional~Product~
        +save(Product) Product
        +update(Long, Product) Product
        +delete(Long) void
        +search(String) List~Product~
        +updateInventory(Long, Integer) void
    }
    
    class OrderService {
        <<@Service>>
        -OrderRepository orderRepository
        -ProductService productService
        -PaymentService paymentService
        -NotificationService notificationService
        +createOrder(OrderRequest) Order
        +updateStatus(Long, OrderStatus) Order
        +cancelOrder(Long) void
        +processPayment(Long) PaymentResult
        +findUserOrders(Long) List~Order~
    }
    
    class UserService {
        <<@Service>>
        -UserRepository userRepository
        -PasswordEncoder passwordEncoder
        -JwtTokenProvider tokenProvider
        +findById(Long) Optional~User~
        +save(User) User
        +authenticate(LoginRequest) AuthResponse
        +updateProfile(Long, UserUpdateRequest) User
        +changePassword(Long, String) void
    }
    
    %% Repositories
    class ProductRepository {
        <<@Repository>>
        <<JpaRepository~Product, Long~>>
        +findByNameContaining(String) List~Product~
        +findByCategoryId(Long) List~Product~
        +findByPriceBetween(BigDecimal, BigDecimal) List~Product~
        +findAvailableProducts() List~Product~
    }
    
    class OrderRepository {
        <<@Repository>>
        <<JpaRepository~Order, Long~>>
        +findByUserId(Long) List~Order~
        +findByStatus(OrderStatus) List~Order~
        +findByCreatedDateBetween(LocalDateTime, LocalDateTime) List~Order~
    }
    
    class UserRepository {
        <<@Repository>>
        <<JpaRepository~User, Long~>>
        +findByEmail(String) Optional~User~
        +findByUsername(String) Optional~User~
        +existsByEmail(String) boolean
    }
    
    %% Entities
    class Product {
        <<@Entity>>
        -Long id
        -String name
        -String description
        -BigDecimal price
        -Integer stockQuantity
        -Category category
        -LocalDateTime createdDate
        -LocalDateTime updatedDate
        +getId() Long
        +getName() String
        +getPrice() BigDecimal
        +isAvailable() boolean
    }
    
    class Order {
        <<@Entity>>
        -Long id
        -User user
        -List~OrderItem~ items
        -BigDecimal totalAmount
        -OrderStatus status
        -LocalDateTime createdDate
        -LocalDateTime updatedDate
        +getId() Long
        +getUser() User
        +getTotalAmount() BigDecimal
        +addItem(OrderItem) void
    }
    
    class User {
        <<@Entity>>
        -Long id
        -String username
        -String email
        -String password
        -String firstName
        -String lastName
        -Set~Role~ roles
        -LocalDateTime createdDate
        -boolean enabled
        +getId() Long
        +getUsername() String
        +getEmail() String
        +getRoles() Set~Role~
    }
    
    class OrderItem {
        <<@Entity>>
        -Long id
        -Product product
        -Integer quantity
        -BigDecimal price
        +getId() Long
        +getProduct() Product
        +getQuantity() Integer
        +getSubtotal() BigDecimal
    }
    
    %% Relationships
    ProductController --> ProductService : uses
    OrderController --> OrderService : uses
    UserController --> UserService : uses
    
    ProductService --> ProductRepository : uses
    OrderService --> OrderRepository : uses
    OrderService --> ProductService : uses
    UserService --> UserRepository : uses
    
    Order ||--o{ OrderItem : contains
    OrderItem }o--|| Product : references
    Order }o--|| User : belongs to
    
    User ||--o{ Order : has many
    Product }o--|| Category : belongs to
```

### 6. State Diagram Example
```mermaid
stateDiagram-v2
    [*] --> ApplicationStarting
    
    ApplicationStarting --> LoadingConfiguration : Spring Boot initializes
    LoadingConfiguration --> ConfiguringDataSources : Load application.yml
    ConfiguringDataSources --> InitializingBeans : Connect to PostgreSQL & Redis
    InitializingBeans --> StartingServices : Create Spring beans
    StartingServices --> RegisteringWithEureka : Start microservices
    RegisteringWithEureka --> Ready : Register with service discovery
    
    Ready --> ProcessingRequest : Incoming HTTP request
    ProcessingRequest --> AuthenticatingUser : JWT validation
    
    AuthenticatingUser --> AuthenticationSuccess : Valid token
    AuthenticatingUser --> AuthenticationFailure : Invalid token
    
    AuthenticationFailure --> Ready : Return 401 Unauthorized
    
    AuthenticationSuccess --> AuthorizingAccess : Check user roles
    AuthorizingAccess --> AuthorizationSuccess : User has permission
    AuthorizingAccess --> AuthorizationFailure : Insufficient permissions
    
    AuthorizationFailure --> Ready : Return 403 Forbidden
    
    AuthorizationSuccess --> ExecutingBusinessLogic : Process request
    ExecutingBusinessLogic --> AccessingDatabase : Query/Update data
    AccessingDatabase --> CachingResult : Store in Redis
    CachingResult --> ReturnResponse : Send JSON response
    ReturnResponse --> Ready : Request completed
    
    Ready --> HealthCheck : /actuator/health
    HealthCheck --> Ready : Return health status
    
    Ready --> ConfigRefresh : Config server update
    ConfigRefresh --> ReloadingConfig : Refresh properties
    ReloadingConfig --> Ready : Configuration updated
    
    Ready --> GracefulShutdown : SIGTERM received
    GracefulShutdown --> DrainConnections : Stop accepting requests
    DrainConnections --> ClosingResources : Close DB connections
    ClosingResources --> UnregisteringFromEureka : Remove from service registry
    UnregisteringFromEureka --> ApplicationStopped : Shutdown complete
    ApplicationStopped --> [*]
    
    %% Error states
    Ready --> ErrorState : Unexpected exception
    ErrorState --> LoggingError : Log to monitoring
    LoggingError --> Ready : Error handled
    
    %% Database connection issues
    AccessingDatabase --> DatabaseError : Connection failure
    DatabaseError --> RetryConnection : Retry with backoff
    RetryConnection --> AccessingDatabase : Retry successful
    RetryConnection --> CircuitBreakerOpen : Max retries exceeded
    CircuitBreakerOpen --> Ready : Return cached response
```

### 7. Sequence Diagram for Order Processing
```mermaid
sequenceDiagram
    participant C as Customer
    participant GW as API Gateway
    participant AUTH as Auth Service
    participant ORDER as Order Service
    participant PRODUCT as Product Service
    participant PAY as Payment Service
    participant DB as PostgreSQL
    participant CACHE as Redis
    participant EMAIL as Email Service
    
    C->>GW: POST /api/orders (Create Order)
    Note over C,GW: Authorization: Bearer jwt-token
    
    GW->>AUTH: Validate JWT Token
    AUTH->>CACHE: Check token in cache
    CACHE-->>AUTH: Token valid
    AUTH-->>GW: User authenticated
    
    GW->>ORDER: POST /orders (Forward request)
    Note over ORDER: Order creation process begins
    
    ORDER->>PRODUCT: GET /products/{id} (Validate products)
    PRODUCT->>CACHE: Check product cache
    alt Cache Hit
        CACHE-->>PRODUCT: Return cached product
    else Cache Miss
        PRODUCT->>DB: SELECT * FROM products
        DB-->>PRODUCT: Product details
        PRODUCT->>CACHE: Cache product data
    end
    PRODUCT-->>ORDER: Product validation successful
    
    ORDER->>PRODUCT: PUT /products/{id}/reserve (Reserve inventory)
    PRODUCT->>DB: UPDATE products SET stock = stock - quantity
    DB-->>PRODUCT: Inventory updated
    PRODUCT-->>ORDER: Inventory reserved
    
    ORDER->>DB: INSERT INTO orders (...) (Create order record)
    DB-->>ORDER: Order created with ID
    
    ORDER->>PAY: POST /payments (Process payment)
    Note over PAY: External payment gateway integration
    PAY-->>ORDER: Payment successful
    
    ORDER->>DB: UPDATE orders SET status = 'CONFIRMED'
    DB-->>ORDER: Order status updated
    
    ORDER->>EMAIL: POST /notifications/email (Send confirmation)
    Note over EMAIL: Order confirmation email
    EMAIL-->>ORDER: Email queued
    
    ORDER-->>GW: 201 Created (Order response)
    GW-->>C: 201 Created (Order confirmation)
    
    Note over C,EMAIL: Order successfully created and confirmed
    
    %% Error handling sequence
    alt Payment Failure
        PAY-->>ORDER: Payment failed
        ORDER->>PRODUCT: POST /products/{id}/release (Release inventory)
        PRODUCT->>DB: UPDATE products SET stock = stock + quantity
        ORDER->>DB: UPDATE orders SET status = 'FAILED'
        ORDER-->>GW: 402 Payment Required
        GW-->>C: 402 Payment Required
    end
    
    alt Inventory Insufficient
        PRODUCT-->>ORDER: 409 Conflict (Insufficient stock)
        ORDER-->>GW: 409 Conflict
        GW-->>C: 409 Conflict (Out of stock)
    end
```

## Integration Instructions

### 1. Template Usage in Documentation Generator
```bash
# The documentation generator uses these templates
gh copilot agent documentation-generator \
    --task "generate-timeline" \
    --data "upgrade-reports/timeline-data.json" \
    --template "upgrade-config/templates/mermaid-templates/timeline-template.mmd" \
    --project-name "E-Commerce API" \
    --old-version "5.3.21" \
    --new-version "6.1.0"
```

### 2. HTML Report Integration
The generated Mermaid diagrams are embedded into the HTML report:
```html
<div class="mermaid">
{{TIMELINE_MERMAID}}
</div>
```

### 3. GitHub Pages Deployment
- Diagrams are automatically rendered in the deployed documentation
- Interactive features allow switching between different diagram views
- Print-friendly versions are available for offline documentation

These examples demonstrate the comprehensive documentation capabilities of the enhanced Spring upgrade system, providing visual representations of the upgrade process, system architecture, and application flow.
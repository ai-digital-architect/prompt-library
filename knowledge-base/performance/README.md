# Performance Best Practices

## Application Performance

### Caching Strategies

```typescript
// Redis caching example
class CacheService {
  private redis: Redis;
  
  async get<T>(key: string): Promise<T | null> {
    const cached = await this.redis.get(key);
    return cached ? JSON.parse(cached) : null;
  }
  
  async set<T>(key: string, value: T, ttl?: number): Promise<void> {
    await this.redis.set(key, JSON.stringify(value), 'EX', ttl || 3600);
  }
}
```

### Memory Management

- Proper garbage collection
- Memory leak prevention
- Buffer management
- Resource pooling
- Memory monitoring

### Database Optimization

```sql
-- Index optimization
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_user_date ON posts(user_id, created_at);

-- Query optimization
SELECT p.*, u.name 
FROM posts p 
INNER JOIN users u ON p.user_id = u.id 
WHERE p.created_at > ? 
LIMIT 20;
```

## Frontend Performance

### React Optimization

```typescript
// Memo usage
const MemoizedComponent = React.memo(({ data }) => {
  return <div>{data.map(renderItem)}</div>;
});

// Code splitting
const LazyComponent = React.lazy(() => import('./LazyComponent'));
```

### Bundle Optimization

- Tree shaking
- Code splitting
- Lazy loading
- Minification
- Compression

### Asset Optimization

```typescript
// Image optimization
const Image = ({ src, alt }) => (
  <picture>
    <source srcSet={`${src}?w=400`} media="(max-width: 400px)" />
    <source srcSet={`${src}?w=800`} media="(max-width: 800px)" />
    <img src={`${src}?w=1200`} alt={alt} loading="lazy" />
  </picture>
);
```

## Backend Performance

### API Optimization

- Response compression
- Batch operations
- Pagination
- Field selection
- Query optimization

### Concurrency

```typescript
// Worker threads example
import { Worker } from 'worker_threads';

class WorkerPool {
  private workers: Worker[];
  
  async executeTask(data: any): Promise<any> {
    const worker = this.getAvailableWorker();
    return new Promise((resolve, reject) => {
      worker.postMessage(data);
      worker.once('message', resolve);
      worker.once('error', reject);
    });
  }
}
```

## Infrastructure Performance

### Load Balancing

- Round-robin
- Least connections
- Resource-based
- Geographic
- Application-aware

### Scaling Strategies

```yaml
# Kubernetes HPA example
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Monitoring & Profiling

### Performance Metrics

```typescript
// Prometheus metrics example
import client from 'prom-client';

const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code']
});
```

### Profiling Tools

- CPU profiling
- Memory profiling
- Flame graphs
- Trace analysis
- Performance testing

## Database Performance

### Query Optimization

```sql
-- Use EXPLAIN for analysis
EXPLAIN ANALYZE
SELECT * FROM users
WHERE last_login > NOW() - INTERVAL '7 days'
AND status = 'active';

-- Optimize JOIN operations
SELECT u.*, p.title
FROM users u
INNER JOIN posts p ON u.id = p.user_id
WHERE u.status = 'active'
AND p.published = true;
```

### Indexing Strategies

- B-tree indexes
- Partial indexes
- Composite indexes
- Covering indexes
- Index maintenance

## Network Performance

### CDN Configuration

- Asset caching
- Edge locations
- Cache invalidation
- Dynamic content
- SSL termination

### Protocol Optimization

```typescript
// HTTP/2 server setup
import spdy from 'spdy';
import fs from 'fs';

const server = spdy.createServer(
  {
    key: fs.readFileSync('./server.key'),
    cert: fs.readFileSync('./server.crt')
  },
  app
);
```

## Performance Testing

### Load Testing

```typescript
// k6 load test example
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
};

export default function () {
  const res = http.get('https://api.example.com');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

### Benchmarking

- Response times
- Throughput
- Error rates
- Resource usage
- Concurrency testing

## Performance Budgets

### Metrics

- Bundle size
- Time to First Byte
- First Contentful Paint
- Time to Interactive
- Memory usage

### Monitoring

```typescript
// Performance budget monitoring
const budget = {
  bundleSize: 250 * 1024, // 250kb
  timeToFirstByte: 200,   // 200ms
  firstContentfulPaint: 1500 // 1.5s
};

function checkPerformanceBudget(metrics) {
  return Object.entries(budget).every(
    ([key, limit]) => metrics[key] <= limit
  );
}
```

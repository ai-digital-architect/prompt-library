# Hexagonal Architecture: Developer Guide

This guide covers implementation patterns, code examples, and practical techniques for developers building hexagonal systems.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Implementing the Domain Layer](#implementing-the-domain-layer)
3. [Implementing Ports](#implementing-ports)
4. [Implementing Adapters](#implementing-adapters)
5. [Dependency Injection](#dependency-injection)
6. [Testing Strategies](#testing-strategies)
7. [Common Patterns](#common-patterns)
8. [AWS Serverless Implementation](#aws-serverless-implementation)

---

## Project Structure

### TypeScript/Node.js Structure

```
src/
├── domain/
│   ├── model/
│   │   ├── order/
│   │   │   ├── Order.ts              # Aggregate root
│   │   │   ├── OrderId.ts            # Value object
│   │   │   ├── OrderLine.ts          # Entity
│   │   │   └── OrderStatus.ts        # Enum/Value object
│   │   └── shared/
│   │       ├── Money.ts              # Shared value object
│   │       └── Email.ts
│   ├── service/
│   │   └── PricingService.ts         # Domain service
│   ├── event/
│   │   ├── DomainEvent.ts            # Base event
│   │   ├── OrderPlaced.ts
│   │   └── OrderCancelled.ts
│   └── error/
│       ├── DomainError.ts
│       └── InsufficientStockError.ts
│
├── application/
│   ├── port/
│   │   ├── inbound/
│   │   │   ├── PlaceOrderUseCase.ts
│   │   │   └── GetOrderUseCase.ts
│   │   └── outbound/
│   │       ├── OrderRepository.ts
│   │       ├── EventPublisher.ts
│   │       └── PaymentGateway.ts
│   ├── command/
│   │   ├── PlaceOrderCommand.ts
│   │   └── PlaceOrderHandler.ts
│   └── query/
│       ├── GetOrderQuery.ts
│       └── GetOrderHandler.ts
│
├── adapter/
│   ├── inbound/
│   │   ├── lambda/
│   │   │   ├── PlaceOrderLambda.ts
│   │   │   └── GetOrderLambda.ts
│   │   └── rest/
│   │       └── OrderController.ts
│   └── outbound/
│       ├── persistence/
│       │   ├── DynamoOrderRepository.ts
│       │   └── OrderMapper.ts
│       ├── messaging/
│       │   └── EventBridgePublisher.ts
│       └── payment/
│           └── StripePaymentGateway.ts
│
└── config/
    ├── container.ts                   # DI container setup
    └── env.ts                         # Environment config
```

### Java/Kotlin Structure

```
src/main/java/com/example/order/
├── domain/
│   ├── model/
│   │   ├── Order.java
│   │   ├── OrderId.java
│   │   └── OrderLine.java
│   ├── service/
│   │   └── PricingService.java
│   └── event/
│       └── OrderPlaced.java
│
├── application/
│   ├── port/
│   │   ├── in/
│   │   │   └── PlaceOrderUseCase.java
│   │   └── out/
│   │       └── OrderRepository.java
│   └── service/
│       └── PlaceOrderService.java
│
└── adapter/
    ├── in/
    │   └── web/
    │       └── OrderController.java
    └── out/
        └── persistence/
            └── DynamoOrderRepository.java
```

---

## Implementing the Domain Layer

### Entities and Aggregate Roots

```typescript
// domain/model/order/Order.ts
import { OrderId } from './OrderId';
import { OrderLine } from './OrderLine';
import { OrderStatus } from './OrderStatus';
import { Money } from '../shared/Money';
import { OrderPlaced } from '../../event/OrderPlaced';
import { DomainEvent } from '../../event/DomainEvent';

export class Order {
  private readonly _id: OrderId;
  private readonly _lines: OrderLine[];
  private _status: OrderStatus;
  private readonly _events: DomainEvent[] = [];

  private constructor(
    id: OrderId,
    lines: OrderLine[],
    status: OrderStatus
  ) {
    this._id = id;
    this._lines = lines;
    this._status = status;
  }

  // Factory method with business rules
  static create(id: OrderId, lines: OrderLine[]): Order {
    if (lines.length === 0) {
      throw new Error('Order must have at least one line');
    }

    const order = new Order(id, lines, OrderStatus.PENDING);
    
    // Record domain event
    order._events.push(new OrderPlaced({
      orderId: id.value,
      total: order.total.amount,
      occurredAt: new Date(),
    }));

    return order;
  }

  // Reconstitute from persistence (no validation, no events)
  static reconstitute(
    id: OrderId,
    lines: OrderLine[],
    status: OrderStatus
  ): Order {
    return new Order(id, lines, status);
  }

  get id(): OrderId {
    return this._id;
  }

  get lines(): ReadonlyArray<OrderLine> {
    return [...this._lines];
  }

  get status(): OrderStatus {
    return this._status;
  }

  get total(): Money {
    return this._lines.reduce(
      (sum, line) => sum.add(line.subtotal),
      Money.zero()
    );
  }

  // Domain behavior
  cancel(): void {
    if (this._status === OrderStatus.SHIPPED) {
      throw new Error('Cannot cancel shipped order');
    }
    this._status = OrderStatus.CANCELLED;
  }

  // Collect and clear events
  pullDomainEvents(): DomainEvent[] {
    const events = [...this._events];
    this._events.length = 0;
    return events;
  }
}
```

### Value Objects

```typescript
// domain/model/shared/Money.ts
export class Money {
  private constructor(
    private readonly _amount: number,
    private readonly _currency: string
  ) {
    if (_amount < 0) {
      throw new Error('Money amount cannot be negative');
    }
  }

  static of(amount: number, currency: string = 'USD'): Money {
    return new Money(amount, currency);
  }

  static zero(currency: string = 'USD'): Money {
    return new Money(0, currency);
  }

  get amount(): number {
    return this._amount;
  }

  get currency(): string {
    return this._currency;
  }

  add(other: Money): Money {
    this.ensureSameCurrency(other);
    return new Money(this._amount + other._amount, this._currency);
  }

  multiply(factor: number): Money {
    return new Money(this._amount * factor, this._currency);
  }

  equals(other: Money): boolean {
    return this._amount === other._amount && this._currency === other._currency;
  }

  private ensureSameCurrency(other: Money): void {
    if (this._currency !== other._currency) {
      throw new Error(`Currency mismatch: ${this._currency} vs ${other._currency}`);
    }
  }
}
```

### Domain Events

```typescript
// domain/event/DomainEvent.ts
export interface DomainEvent {
  readonly eventType: string;
  readonly occurredAt: Date;
  readonly aggregateId: string;
}

// domain/event/OrderPlaced.ts
import { DomainEvent } from './DomainEvent';

export interface OrderPlacedPayload {
  orderId: string;
  total: number;
  occurredAt: Date;
}

export class OrderPlaced implements DomainEvent {
  readonly eventType = 'OrderPlaced';
  readonly aggregateId: string;
  readonly occurredAt: Date;
  readonly total: number;

  constructor(payload: OrderPlacedPayload) {
    this.aggregateId = payload.orderId;
    this.total = payload.total;
    this.occurredAt = payload.occurredAt;
  }
}
```

---

## Implementing Ports

### Inbound Ports (Use Cases)

```typescript
// application/port/inbound/PlaceOrderUseCase.ts
import { PlaceOrderCommand } from '../../command/PlaceOrderCommand';
import { OrderId } from '../../../domain/model/order/OrderId';

export interface PlaceOrderUseCase {
  execute(command: PlaceOrderCommand): Promise<OrderId>;
}

// application/command/PlaceOrderCommand.ts
export interface PlaceOrderCommand {
  readonly customerId: string;
  readonly items: Array<{
    productId: string;
    quantity: number;
    unitPrice: number;
  }>;
}

// application/command/PlaceOrderHandler.ts
import { PlaceOrderUseCase } from '../port/inbound/PlaceOrderUseCase';
import { PlaceOrderCommand } from './PlaceOrderCommand';
import { OrderRepository } from '../port/outbound/OrderRepository';
import { EventPublisher } from '../port/outbound/EventPublisher';
import { Order } from '../../domain/model/order/Order';
import { OrderId } from '../../domain/model/order/OrderId';
import { OrderLine } from '../../domain/model/order/OrderLine';

export class PlaceOrderHandler implements PlaceOrderUseCase {
  constructor(
    private readonly orderRepository: OrderRepository,
    private readonly eventPublisher: EventPublisher
  ) {}

  async execute(command: PlaceOrderCommand): Promise<OrderId> {
    // Create domain objects
    const orderId = OrderId.generate();
    const lines = command.items.map(item =>
      OrderLine.create(item.productId, item.quantity, item.unitPrice)
    );

    // Execute domain logic
    const order = Order.create(orderId, lines);

    // Persist
    await this.orderRepository.save(order);

    // Publish events
    const events = order.pullDomainEvents();
    await this.eventPublisher.publishAll(events);

    return orderId;
  }
}
```

### Outbound Ports (Dependencies)

```typescript
// application/port/outbound/OrderRepository.ts
import { Order } from '../../../domain/model/order/Order';
import { OrderId } from '../../../domain/model/order/OrderId';

export interface OrderRepository {
  findById(id: OrderId): Promise<Order | null>;
  findByCustomerId(customerId: string): Promise<Order[]>;
  save(order: Order): Promise<void>;
  delete(id: OrderId): Promise<void>;
}

// application/port/outbound/EventPublisher.ts
import { DomainEvent } from '../../../domain/event/DomainEvent';

export interface EventPublisher {
  publish(event: DomainEvent): Promise<void>;
  publishAll(events: DomainEvent[]): Promise<void>;
}

// application/port/outbound/PaymentGateway.ts
import { Money } from '../../../domain/model/shared/Money';

export interface PaymentResult {
  success: boolean;
  transactionId?: string;
  errorCode?: string;
}

export interface PaymentGateway {
  charge(customerId: string, amount: Money): Promise<PaymentResult>;
  refund(transactionId: string, amount: Money): Promise<PaymentResult>;
}
```

---

## Implementing Adapters

### Inbound Adapter: Lambda Handler

```typescript
// adapter/inbound/lambda/PlaceOrderLambda.ts
import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { PlaceOrderUseCase } from '../../../application/port/inbound/PlaceOrderUseCase';
import { PlaceOrderCommand } from '../../../application/command/PlaceOrderCommand';
import { container } from '../../../config/container';

// Get use case from DI container
const placeOrderUseCase = container.get<PlaceOrderUseCase>('PlaceOrderUseCase');

export const handler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  try {
    // Parse and validate input
    const body = JSON.parse(event.body || '{}');
    
    // Translate to command (adapter's job)
    const command: PlaceOrderCommand = {
      customerId: body.customer_id,  // Translate from API naming
      items: body.items.map((item: any) => ({
        productId: item.product_id,
        quantity: item.qty,
        unitPrice: item.price,
      })),
    };

    // Execute use case
    const orderId = await placeOrderUseCase.execute(command);

    // Translate response
    return {
      statusCode: 201,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        order_id: orderId.value,
        message: 'Order placed successfully',
      }),
    };
  } catch (error) {
    // Translate domain errors to HTTP responses
    if (error instanceof ValidationError) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: error.message }),
      };
    }
    
    console.error('Unexpected error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal server error' }),
    };
  }
};
```

### Outbound Adapter: DynamoDB Repository

```typescript
// adapter/outbound/persistence/DynamoOrderRepository.ts
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import {
  DynamoDBDocumentClient,
  GetCommand,
  PutCommand,
  QueryCommand,
  DeleteCommand,
} from '@aws-sdk/lib-dynamodb';
import { OrderRepository } from '../../../application/port/outbound/OrderRepository';
import { Order } from '../../../domain/model/order/Order';
import { OrderId } from '../../../domain/model/order/OrderId';
import { OrderMapper } from './OrderMapper';

export class DynamoOrderRepository implements OrderRepository {
  private readonly docClient: DynamoDBDocumentClient;
  private readonly tableName: string;

  constructor(client: DynamoDBClient, tableName: string) {
    this.docClient = DynamoDBDocumentClient.from(client);
    this.tableName = tableName;
  }

  async findById(id: OrderId): Promise<Order | null> {
    const result = await this.docClient.send(
      new GetCommand({
        TableName: this.tableName,
        Key: { PK: `ORDER#${id.value}`, SK: `ORDER#${id.value}` },
      })
    );

    if (!result.Item) return null;

    return OrderMapper.toDomain(result.Item);
  }

  async findByCustomerId(customerId: string): Promise<Order[]> {
    const result = await this.docClient.send(
      new QueryCommand({
        TableName: this.tableName,
        IndexName: 'GSI1',
        KeyConditionExpression: 'GSI1PK = :pk',
        ExpressionAttributeValues: {
          ':pk': `CUSTOMER#${customerId}`,
        },
      })
    );

    return (result.Items || []).map(OrderMapper.toDomain);
  }

  async save(order: Order): Promise<void> {
    const item = OrderMapper.toPersistence(order);

    await this.docClient.send(
      new PutCommand({
        TableName: this.tableName,
        Item: item,
      })
    );
  }

  async delete(id: OrderId): Promise<void> {
    await this.docClient.send(
      new DeleteCommand({
        TableName: this.tableName,
        Key: { PK: `ORDER#${id.value}`, SK: `ORDER#${id.value}` },
      })
    );
  }
}

// adapter/outbound/persistence/OrderMapper.ts
import { Order } from '../../../domain/model/order/Order';
import { OrderId } from '../../../domain/model/order/OrderId';
import { OrderLine } from '../../../domain/model/order/OrderLine';
import { OrderStatus } from '../../../domain/model/order/OrderStatus';

interface OrderRecord {
  PK: string;
  SK: string;
  GSI1PK: string;
  orderId: string;
  customerId: string;
  status: string;
  lines: Array<{
    productId: string;
    quantity: number;
    unitPrice: number;
  }>;
  createdAt: string;
}

export class OrderMapper {
  static toDomain(record: OrderRecord): Order {
    const id = OrderId.from(record.orderId);
    const lines = record.lines.map(line =>
      OrderLine.reconstitute(line.productId, line.quantity, line.unitPrice)
    );
    const status = OrderStatus[record.status as keyof typeof OrderStatus];

    return Order.reconstitute(id, lines, status);
  }

  static toPersistence(order: Order): OrderRecord {
    return {
      PK: `ORDER#${order.id.value}`,
      SK: `ORDER#${order.id.value}`,
      GSI1PK: `CUSTOMER#${order.customerId}`,
      orderId: order.id.value,
      customerId: order.customerId,
      status: order.status,
      lines: order.lines.map(line => ({
        productId: line.productId,
        quantity: line.quantity,
        unitPrice: line.unitPrice.amount,
      })),
      createdAt: new Date().toISOString(),
    };
  }
}
```

### Outbound Adapter: EventBridge Publisher

```typescript
// adapter/outbound/messaging/EventBridgePublisher.ts
import { EventBridgeClient, PutEventsCommand } from '@aws-sdk/client-eventbridge';
import { EventPublisher } from '../../../application/port/outbound/EventPublisher';
import { DomainEvent } from '../../../domain/event/DomainEvent';

export class EventBridgePublisher implements EventPublisher {
  constructor(
    private readonly client: EventBridgeClient,
    private readonly eventBusName: string,
    private readonly source: string
  ) {}

  async publish(event: DomainEvent): Promise<void> {
    await this.publishAll([event]);
  }

  async publishAll(events: DomainEvent[]): Promise<void> {
    if (events.length === 0) return;

    const entries = events.map(event => ({
      EventBusName: this.eventBusName,
      Source: this.source,
      DetailType: event.eventType,
      Detail: JSON.stringify({
        aggregateId: event.aggregateId,
        occurredAt: event.occurredAt.toISOString(),
        ...event,
      }),
    }));

    await this.client.send(new PutEventsCommand({ Entries: entries }));
  }
}
```

---

## Dependency Injection

### Simple Container

```typescript
// config/container.ts
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { EventBridgeClient } from '@aws-sdk/client-eventbridge';
import { DynamoOrderRepository } from '../adapter/outbound/persistence/DynamoOrderRepository';
import { EventBridgePublisher } from '../adapter/outbound/messaging/EventBridgePublisher';
import { PlaceOrderHandler } from '../application/command/PlaceOrderHandler';
import { PlaceOrderUseCase } from '../application/port/inbound/PlaceOrderUseCase';

class Container {
  private instances = new Map<string, any>();

  constructor() {
    this.bootstrap();
  }

  private bootstrap(): void {
    // Infrastructure clients
    const dynamoClient = new DynamoDBClient({});
    const eventBridgeClient = new EventBridgeClient({});

    // Outbound adapters
    const orderRepository = new DynamoOrderRepository(
      dynamoClient,
      process.env.ORDER_TABLE_NAME!
    );

    const eventPublisher = new EventBridgePublisher(
      eventBridgeClient,
      process.env.EVENT_BUS_NAME!,
      'com.example.orders'
    );

    // Use case handlers
    const placeOrderHandler = new PlaceOrderHandler(
      orderRepository,
      eventPublisher
    );

    // Register
    this.instances.set('OrderRepository', orderRepository);
    this.instances.set('EventPublisher', eventPublisher);
    this.instances.set('PlaceOrderUseCase', placeOrderHandler);
  }

  get<T>(key: string): T {
    const instance = this.instances.get(key);
    if (!instance) {
      throw new Error(`No instance registered for key: ${key}`);
    }
    return instance as T;
  }
}

export const container = new Container();
```

### With InversifyJS (More Robust)

```typescript
// config/container.ts
import 'reflect-metadata';
import { Container } from 'inversify';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';

const TYPES = {
  DynamoDBClient: Symbol.for('DynamoDBClient'),
  OrderRepository: Symbol.for('OrderRepository'),
  EventPublisher: Symbol.for('EventPublisher'),
  PlaceOrderUseCase: Symbol.for('PlaceOrderUseCase'),
};

const container = new Container();

// Bind infrastructure
container.bind(TYPES.DynamoDBClient).toConstantValue(new DynamoDBClient({}));

// Bind adapters
container.bind(TYPES.OrderRepository).to(DynamoOrderRepository);
container.bind(TYPES.EventPublisher).to(EventBridgePublisher);

// Bind use cases
container.bind(TYPES.PlaceOrderUseCase).to(PlaceOrderHandler);

export { container, TYPES };
```

---

## Testing Strategies

### Unit Testing Domain Logic

```typescript
// domain/model/order/Order.test.ts
import { Order } from './Order';
import { OrderId } from './OrderId';
import { OrderLine } from './OrderLine';
import { OrderStatus } from './OrderStatus';

describe('Order', () => {
  const createValidOrder = () => {
    const id = OrderId.generate();
    const lines = [
      OrderLine.create('product-1', 2, 10.00),
      OrderLine.create('product-2', 1, 25.00),
    ];
    return Order.create(id, lines);
  };

  describe('create', () => {
    it('creates order with pending status', () => {
      const order = createValidOrder();
      expect(order.status).toBe(OrderStatus.PENDING);
    });

    it('calculates total from lines', () => {
      const order = createValidOrder();
      expect(order.total.amount).toBe(45.00); // 2*10 + 1*25
    });

    it('emits OrderPlaced event', () => {
      const order = createValidOrder();
      const events = order.pullDomainEvents();
      
      expect(events).toHaveLength(1);
      expect(events[0].eventType).toBe('OrderPlaced');
    });

    it('rejects empty order', () => {
      expect(() => Order.create(OrderId.generate(), [])).toThrow();
    });
  });

  describe('cancel', () => {
    it('transitions to cancelled status', () => {
      const order = createValidOrder();
      order.cancel();
      expect(order.status).toBe(OrderStatus.CANCELLED);
    });

    it('rejects cancellation of shipped order', () => {
      const order = Order.reconstitute(
        OrderId.generate(),
        [OrderLine.create('product-1', 1, 10)],
        OrderStatus.SHIPPED
      );
      
      expect(() => order.cancel()).toThrow('Cannot cancel shipped order');
    });
  });
});
```

### Testing Use Cases with In-Memory Adapters

```typescript
// application/command/PlaceOrderHandler.test.ts
import { PlaceOrderHandler } from './PlaceOrderHandler';
import { InMemoryOrderRepository } from '../../../test/adapters/InMemoryOrderRepository';
import { InMemoryEventPublisher } from '../../../test/adapters/InMemoryEventPublisher';
import { PlaceOrderCommand } from './PlaceOrderCommand';

describe('PlaceOrderHandler', () => {
  let handler: PlaceOrderHandler;
  let orderRepository: InMemoryOrderRepository;
  let eventPublisher: InMemoryEventPublisher;

  beforeEach(() => {
    orderRepository = new InMemoryOrderRepository();
    eventPublisher = new InMemoryEventPublisher();
    handler = new PlaceOrderHandler(orderRepository, eventPublisher);
  });

  it('saves order and publishes event', async () => {
    const command: PlaceOrderCommand = {
      customerId: 'customer-123',
      items: [
        { productId: 'product-1', quantity: 2, unitPrice: 10.00 },
      ],
    };

    const orderId = await handler.execute(command);

    // Verify persistence
    const savedOrder = await orderRepository.findById(orderId);
    expect(savedOrder).not.toBeNull();
    expect(savedOrder!.lines).toHaveLength(1);

    // Verify event published
    expect(eventPublisher.publishedEvents).toHaveLength(1);
    expect(eventPublisher.publishedEvents[0].eventType).toBe('OrderPlaced');
  });
});

// test/adapters/InMemoryOrderRepository.ts
import { OrderRepository } from '../../application/port/outbound/OrderRepository';
import { Order } from '../../domain/model/order/Order';
import { OrderId } from '../../domain/model/order/OrderId';

export class InMemoryOrderRepository implements OrderRepository {
  private orders = new Map<string, Order>();

  async findById(id: OrderId): Promise<Order | null> {
    return this.orders.get(id.value) || null;
  }

  async findByCustomerId(customerId: string): Promise<Order[]> {
    return Array.from(this.orders.values())
      .filter(order => order.customerId === customerId);
  }

  async save(order: Order): Promise<void> {
    this.orders.set(order.id.value, order);
  }

  async delete(id: OrderId): Promise<void> {
    this.orders.delete(id.value);
  }

  // Test helper
  clear(): void {
    this.orders.clear();
  }
}
```

### Integration Testing Adapters

```typescript
// adapter/outbound/persistence/DynamoOrderRepository.integration.test.ts
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoOrderRepository } from './DynamoOrderRepository';
import { Order } from '../../../domain/model/order/Order';
import { OrderId } from '../../../domain/model/order/OrderId';
import { OrderLine } from '../../../domain/model/order/OrderLine';

describe('DynamoOrderRepository Integration', () => {
  let repository: DynamoOrderRepository;

  beforeAll(() => {
    const client = new DynamoDBClient({
      endpoint: 'http://localhost:8000', // LocalStack or DynamoDB Local
    });
    repository = new DynamoOrderRepository(client, 'orders-test');
  });

  it('round-trips order through persistence', async () => {
    const order = Order.create(
      OrderId.generate(),
      [OrderLine.create('product-1', 2, 10.00)]
    );

    await repository.save(order);
    const retrieved = await repository.findById(order.id);

    expect(retrieved).not.toBeNull();
    expect(retrieved!.id.value).toBe(order.id.value);
    expect(retrieved!.total.amount).toBe(20.00);
  });
});
```

---

## Common Patterns

### Result Type for Error Handling

```typescript
// domain/shared/Result.ts
export type Result<T, E = Error> =
  | { success: true; value: T }
  | { success: false; error: E };

export const Result = {
  ok: <T>(value: T): Result<T, never> => ({ success: true, value }),
  fail: <E>(error: E): Result<never, E> => ({ success: false, error }),
};

// Usage in use case
async execute(command: PlaceOrderCommand): Promise<Result<OrderId, OrderError>> {
  try {
    // ... create order
    return Result.ok(orderId);
  } catch (error) {
    if (error instanceof InsufficientStockError) {
      return Result.fail(new OrderError('INSUFFICIENT_STOCK', error.message));
    }
    throw error; // Re-throw unexpected errors
  }
}
```

### Specification Pattern

```typescript
// domain/specification/Specification.ts
export interface Specification<T> {
  isSatisfiedBy(candidate: T): boolean;
  and(other: Specification<T>): Specification<T>;
  or(other: Specification<T>): Specification<T>;
  not(): Specification<T>;
}

// domain/specification/OrderSpecifications.ts
export class HighValueOrder implements Specification<Order> {
  constructor(private threshold: Money) {}

  isSatisfiedBy(order: Order): boolean {
    return order.total.amount >= this.threshold.amount;
  }

  and(other: Specification<Order>): Specification<Order> {
    return new AndSpecification(this, other);
  }
  // ... or, not
}

// Usage
const isVIP = new HighValueOrder(Money.of(1000))
  .and(new LoyalCustomer(2)); // 2+ years

const vipOrders = orders.filter(order => isVIP.isSatisfiedBy(order));
```

---

## AWS Serverless Implementation

### Terraform Infrastructure for Hexagonal Architecture

```hcl
# infrastructure/modules/hexagonal-service/variables.tf

variable "service_name" {
  description = "Name of the service/bounded context"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "lambda_source_path" {
  description = "Path to Lambda deployment package"
  type        = string
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
```

```hcl
# infrastructure/modules/hexagonal-service/main.tf

locals {
  prefix = "${var.service_name}-${var.environment}"
  
  common_tags = merge(var.tags, {
    Service     = var.service_name
    Environment = var.environment
    Architecture = "hexagonal"
  })
}

# Outbound Port: Repository (DynamoDB)
resource "aws_dynamodb_table" "aggregate_store" {
  name         = "${local.prefix}-aggregates"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = local.common_tags
}

# Outbound Port: Event Publisher (EventBridge)
resource "aws_cloudwatch_event_bus" "domain_events" {
  name = "${local.prefix}-domain-events"
  tags = local.common_tags
}

# Inbound Adapter: API Gateway
resource "aws_apigatewayv2_api" "main" {
  name          = "${local.prefix}-api"
  protocol_type = "HTTP"
  tags          = local.common_tags
}

resource "aws_apigatewayv2_stage" "main" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "v1"
  auto_deploy = true
}
```

```hcl
# infrastructure/modules/hexagonal-service/lambda.tf

# Lambda per Use Case (Inbound Port implementation)
resource "aws_lambda_function" "place_order" {
  function_name = "${local.prefix}-place-order"
  role          = aws_iam_role.lambda.arn
  handler       = "adapter/inbound/lambda/PlaceOrderLambda.handler"
  runtime       = "nodejs18.x"
  timeout       = 30

  filename         = var.lambda_source_path
  source_code_hash = filebase64sha256(var.lambda_source_path)

  environment {
    variables = {
      TABLE_NAME     = aws_dynamodb_table.aggregate_store.name
      EVENT_BUS_NAME = aws_cloudwatch_event_bus.domain_events.name
    }
  }

  tracing_config {
    mode = "Active"
  }

  tags = local.common_tags
}

resource "aws_lambda_function" "get_order" {
  function_name = "${local.prefix}-get-order"
  role          = aws_iam_role.lambda.arn
  handler       = "adapter/inbound/lambda/GetOrderLambda.handler"
  runtime       = "nodejs18.x"
  timeout       = 10

  filename         = var.lambda_source_path
  source_code_hash = filebase64sha256(var.lambda_source_path)

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.aggregate_store.name
    }
  }

  tags = local.common_tags
}

# IAM Role for Lambda (access to outbound adapters)
resource "aws_iam_role" "lambda" {
  name = "${local.prefix}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy" "lambda" {
  name = "${local.prefix}-lambda-policy"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query"
        ]
        Resource = [
          aws_dynamodb_table.aggregate_store.arn,
          "${aws_dynamodb_table.aggregate_store.arn}/index/*"
        ]
      },
      {
        Effect   = "Allow"
        Action   = ["events:PutEvents"]
        Resource = aws_cloudwatch_event_bus.domain_events.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}
```

```hcl
# infrastructure/modules/hexagonal-service/api_routes.tf

# Route: POST /orders (PlaceOrder use case)
resource "aws_apigatewayv2_route" "place_order" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /orders"
  target    = "integrations/${aws_apigatewayv2_integration.place_order.id}"
}

resource "aws_apigatewayv2_integration" "place_order" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.place_order.invoke_arn
  payload_format_version = "2.0"
}

# Route: GET /orders/{id} (GetOrder use case)
resource "aws_apigatewayv2_route" "get_order" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /orders/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.get_order.id}"
}

resource "aws_apigatewayv2_integration" "get_order" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.get_order.invoke_arn
  payload_format_version = "2.0"
}

# Lambda permissions for API Gateway
resource "aws_lambda_permission" "place_order" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.place_order.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

resource "aws_lambda_permission" "get_order" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_order.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}
```

```hcl
# infrastructure/modules/hexagonal-service/outputs.tf

output "api_endpoint" {
  description = "API Gateway endpoint"
  value       = aws_apigatewayv2_stage.main.invoke_url
}

output "table_name" {
  description = "DynamoDB table for aggregates"
  value       = aws_dynamodb_table.aggregate_store.name
}

output "event_bus_name" {
  description = "EventBridge bus for domain events"
  value       = aws_cloudwatch_event_bus.domain_events.name
}
```

### Deploying the Hexagonal Service

```hcl
# infrastructure/environments/prod/main.tf

module "order_service" {
  source = "../../modules/hexagonal-service"

  service_name       = "orders"
  environment        = "prod"
  lambda_source_path = "${path.module}/../../dist/lambda.zip"

  tags = {
    Team = "order-team"
  }
}

output "order_api_endpoint" {
  value = module.order_service.api_endpoint
}
```

### Complete Lambda Structure

```typescript
// adapter/inbound/lambda/PlaceOrderLambda.ts
import { APIGatewayProxyHandler } from 'aws-lambda';
import middy from '@middy/core';
import jsonBodyParser from '@middy/http-json-body-parser';
import httpErrorHandler from '@middy/http-error-handler';
import { container } from '../../../config/container';
import { PlaceOrderUseCase } from '../../../application/port/inbound/PlaceOrderUseCase';

const placeOrderUseCase = container.get<PlaceOrderUseCase>('PlaceOrderUseCase');

const baseHandler: APIGatewayProxyHandler = async (event) => {
  const body = event.body as any; // Parsed by middy

  const command = {
    customerId: body.customerId,
    items: body.items,
  };

  const orderId = await placeOrderUseCase.execute(command);

  return {
    statusCode: 201,
    body: JSON.stringify({ orderId: orderId.value }),
  };
};

export const handler = middy(baseHandler)
  .use(jsonBodyParser())
  .use(httpErrorHandler());
```

### CDK Infrastructure

```typescript
// cdk/lib/order-service-stack.ts
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda-nodejs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as events from 'aws-cdk-lib/aws-events';

export class OrderServiceStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Domain storage
    const orderTable = new dynamodb.Table(this, 'OrderTable', {
      partitionKey: { name: 'PK', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'SK', type: dynamodb.AttributeType.STRING },
    });

    // Domain events
    const eventBus = new events.EventBus(this, 'OrderEventBus');

    // Place Order use case
    const placeOrderLambda = new lambda.NodejsFunction(this, 'PlaceOrder', {
      entry: 'src/adapter/inbound/lambda/PlaceOrderLambda.ts',
      handler: 'handler',
      environment: {
        ORDER_TABLE_NAME: orderTable.tableName,
        EVENT_BUS_NAME: eventBus.eventBusName,
      },
    });

    orderTable.grantReadWriteData(placeOrderLambda);
    eventBus.grantPutEventsTo(placeOrderLambda);
  }
}
```

---

## Quick Reference: Implementation Checklist

- [ ] Domain layer has zero infrastructure imports
- [ ] Entities created via factory methods with validation
- [ ] Value objects are immutable
- [ ] Domain events recorded in aggregate
- [ ] Inbound ports defined as interfaces (use cases)
- [ ] Outbound ports defined as interfaces (repositories, clients)
- [ ] Adapters implement port interfaces
- [ ] Mappers translate between domain and persistence models
- [ ] DI container wires adapters to ports
- [ ] Unit tests use in-memory adapters
- [ ] Integration tests verify real adapters
- [ ] Lambda handlers are thin (delegate to use cases)

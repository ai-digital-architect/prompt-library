### Component Architecture
- Follow atomic design principles (atoms, molecules, organisms, templates, pages)
- Implement container/presentational pattern where appropriate
- Keep components small and focused on a single responsibility
- Use React.memo for performance optimization of pure components
- Implement proper prop drilling alternatives (Context, Composition)
- Leverage component composition over inheritance
- Implement error boundaries for fault isolation

### TypeScript Implementation
- Define proper interfaces and types for all components and functions
- Use discriminated unions for complex state management
- Leverage generic types for reusable components
- Implement proper type guards and type narrowing
- Use utility types (Partial, Omit, Pick, etc.) appropriately
- Avoid `any` type unless absolutely necessary
- Define proper return types for all functions
- Use type inference where appropriate

### React Hooks Usage
- Follow hooks rules (only call at top level, only call from React functions)
- Implement custom hooks for reusable logic
- Use useCallback for memoizing functions passed to child components
- Use useMemo for expensive calculations
- Implement useEffect with proper dependency arrays
- Use useRef for accessing DOM elements and storing mutable values
- Implement custom hooks for common patterns (useLocalStorage, useMediaQuery, etc.)

### State Management
- Keep component state as local as possible
- Use appropriate state management based on complexity and scope
- Implement proper state normalization for complex data
- Use selectors for derived state
- Implement optimistic updates for better UX
- Use state machines for complex UI states
- Implement proper error and loading states

### Performance Optimization
- Implement code splitting with React.lazy and Suspense
- Use windowing/virtualization for large lists (react-window, react-virtualized)
- Implement proper React.memo usage with custom equality functions
- Avoid unnecessary re-renders with useMemo and useCallback
- Use Web Workers for CPU-intensive tasks
- Implement proper key prop usage in lists
- Use performance profiling with React DevTools
- Optimize images and assets loading
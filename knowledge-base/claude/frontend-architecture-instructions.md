---
title: "Frontend Architecture Instructions"
description: "Guidelines for structuring the React TypeScript application with Vite and Shadcn UI"
applicableGlobs: ["frontend/**/*", "*.tsx", "*.ts", "vite.config.ts"]
version: "1.0.0"
lastUpdated: "2025-05-17"
---

# Frontend Architecture Instructions

## Project Structure

```
frontend/
├── public/                  # Static assets
├── src/
│   ├── assets/              # Processed assets (images, fonts, etc.)
│   ├── components/
│   │   ├── common/          # Reusable components across the app
│   │   ├── layout/          # Layout components (Header, Footer, etc.)
│   │   └── [feature]/       # Feature-specific components
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utility functions and libraries
│   │   └── utils.ts         # Common utility functions
│   ├── services/            # API service integrations
│   ├── contexts/            # React context definitions
│   ├── pages/               # Page components
│   ├── types/               # TypeScript type definitions
│   ├── styles/              # Global styles and theme configurations
│   ├── constants/           # Application constants
│   ├── config/              # Configuration files
│   ├── App.tsx              # Main App component
│   ├── main.tsx             # Application entry point
│   └── routes.tsx           # Route definitions
├── .env                     # Environment variables
├── .env.development         # Development environment variables
├── .env.production          # Production environment variables
├── tsconfig.json            # TypeScript configuration
├── vite.config.ts           # Vite configuration
└── package.json             # Package dependencies
```

## Architecture Patterns

### Component Architecture

1. **Atomic Design Methodology**
   - Atoms: Basic building blocks (buttons, inputs, etc.)
   - Molecules: Simple component groups (form fields with labels, etc.)
   - Organisms: Complex UI sections (forms, data tables, etc.)
   - Templates: Page layouts
   - Pages: Specific implementations of templates

2. **Component Structure**
   ```tsx
   // ComponentName.tsx
   import { useState, useEffect } from 'react';
   import styles from './ComponentName.module.css'; // If using CSS modules
   
   interface ComponentNameProps {
     // Props definition
   }
   
   export const ComponentName = ({ prop1, prop2 }: ComponentNameProps) => {
     // Component logic

     return (
       // JSX
     );
   };
   ```

3. **Index Pattern for Component Exports**
   ```tsx
   // components/common/index.ts
   export * from './Button';
   export * from './Input';
   // etc.
   ```

### State Management

1. **For Simple State**: React hooks (useState, useReducer)
2. **For Shared State**: React Context API with useContext
3. **For Complex State**: Consider Redux Toolkit for larger applications
4. **State Organization**: Group by feature/domain

### API Integration Pattern

1. **Service Layer**
   ```tsx
   // services/apiService.ts
   import axios from 'axios';
   
   const API_URL = import.meta.env.VITE_API_URL;
   
   const apiClient = axios.create({
     baseURL: API_URL,
     headers: {
       'Content-type': 'application/json',
     },
   });
   
   // Add interceptors for auth tokens, error handling, etc.
   apiClient.interceptors.request.use(/* ... */);
   apiClient.interceptors.response.use(/* ... */);
   
   export default apiClient;
   ```

2. **Feature-Specific Services**
   ```tsx
   // services/userService.ts
   import apiClient from './apiService';
   import { User } from '../types';
   
   export const UserService = {
     getCurrentUser: async (): Promise<User> => {
       const response = await apiClient.get('/users/current');
       return response.data;
     },
     // Other user-related API calls
   };
   ```

3. **Custom Hooks for API Calls**
   ```tsx
   // hooks/useApi.ts
   import { useState, useEffect } from 'react';
   
   export function useApi<T>(apiCall: () => Promise<T>) {
     const [data, setData] = useState<T | null>(null);
     const [loading, setLoading] = useState(true);
     const [error, setError] = useState<Error | null>(null);
     
     useEffect(() => {
       const fetchData = async () => {
         try {
           setLoading(true);
           const result = await apiCall();
           setData(result);
         } catch (err) {
           setError(err as Error);
         } finally {
           setLoading(false);
         }
       };
       
       fetchData();
     }, [apiCall]);
     
     return { data, loading, error };
   }
   ```

### Routing Pattern

```tsx
// routes.tsx
import { createBrowserRouter } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import NotFound from './pages/NotFound';
import ProtectedRoute from './components/common/ProtectedRoute';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: 'profile',
        element: (
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        ),
      },
      {
        path: '*',
        element: <NotFound />,
      },
    ],
  },
]);
```

## Shadcn UI Integration

1. **Component Installation**
   - Use the Shadcn CLI to add components: `npx shadcn-ui@latest add [component-name]`
   - Keep components in `src/components/ui/` directory
   - Customize the theme in `src/styles/globals.css`

2. **Tailwind Configuration**
   ```js
   // tailwind.config.js
   const { fontFamily } = require("tailwindcss/defaultTheme")
   
   /** @type {import('tailwindcss').Config} */
   module.exports = {
     darkMode: ["class"],
     content: ["./src/**/*.{ts,tsx}"],
     theme: {
       extend: {
         colors: {
           // Custom color palette
           primary: {
             DEFAULT: "hsl(var(--primary))",
             foreground: "hsl(var(--primary-foreground))",
           },
           // Additional custom colors
         },
         fontFamily: {
           sans: ["var(--font-sans)", ...fontFamily.sans],
         },
         // Additional custom theme extensions
       },
     },
     plugins: [require("tailwindcss-animate")],
   }
   ```

3. **Theme Configuration**
   ```css
   /* src/styles/globals.css */
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   
   @layer base {
     :root {
       --background: 0 0% 100%;
       --foreground: 222.2 84% 4.9%;
       --primary: 221.2 83.2% 53.3%;
       --primary-foreground: 210 40% 98%;
       /* Additional color variables */
     }
     
     .dark {
       --background: 222.2 84% 4.9%;
       --foreground: 210 40% 98%;
       /* Dark theme color variables */
     }
   }
   ```

## Performance Considerations

1. **Code Splitting**: Utilize dynamic imports with React.lazy and Suspense
   ```tsx
   const LazyComponent = React.lazy(() => import('./LazyComponent'));
   
   function MyComponent() {
     return (
       <Suspense fallback={<div>Loading...</div>}>
         <LazyComponent />
       </Suspense>
     );
   }
   ```

2. **Memoization**: Use React.memo, useMemo, and useCallback appropriately
   ```tsx
   const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);
   const memoizedCallback = useCallback(() => { doSomething(a, b); }, [a, b]);
   ```

3. **Virtual Lists**: For long lists, use virtualization libraries
   ```tsx
   import { useVirtualizer } from '@tanstack/react-virtual';
   
   function VirtualList({ items }) {
     const rowVirtualizer = useVirtualizer({
       count: items.length,
       getScrollElement: () => parentRef.current,
       estimateSize: () => 35,
     });
     
     // Implementation details
   }
   ```

4. **Lazy Loading Images**: Use modern image loading strategies
   ```tsx
   import { useState, useEffect } from 'react';
   
   function LazyImage({ src, alt }) {
     const [imageSrc, setImageSrc] = useState('placeholder.jpg');
     
     useEffect(() => {
       const img = new Image();
       img.src = src;
       img.onload = () => {
         setImageSrc(src);
       };
     }, [src]);
     
     return <img src={imageSrc} alt={alt} loading="lazy" />;
   }
   ```

## Vite Configuration

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          // Additional chunk definitions
        },
      },
    },
  },
});
```

## Accessibility Guidelines

1. **Ensure all components are accessible**:
   - Use proper ARIA attributes
   - Maintain proper contrast ratios
   - Support keyboard navigation
   - Design focus states for interactive elements

2. **Utilize Shadcn UI's built-in accessibility features**

3. **Implement focus management for modals and dialogs**

## Error Handling Strategy

1. **Global Error Boundary**
   ```tsx
   // components/common/ErrorBoundary.tsx
   import React, { Component, ErrorInfo, ReactNode } from 'react';
   
   interface Props {
     children: ReactNode;
     fallback?: ReactNode;
   }
   
   interface State {
     hasError: boolean;
     error?: Error;
   }
   
   class ErrorBoundary extends Component<Props, State> {
     public state: State = {
       hasError: false,
     };
   
     public static getDerivedStateFromError(error: Error): State {
       return { hasError: true, error };
     }
   
     public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
       console.error("Uncaught error:", error, errorInfo);
       // Log to error tracking service
     }
   
     public render() {
       if (this.state.hasError) {
         return this.props.fallback || (
           <div>
             <h2>Something went wrong.</h2>
             <button onClick={() => this.setState({ hasError: false })}>
               Try again
             </button>
           </div>
         );
       }
   
       return this.props.children;
     }
   }
   
   export default ErrorBoundary;
   ```

2. **API Error Handling**
   ```tsx
   // services/errorHandler.ts
   export class ApiError extends Error {
     status: number;
     
     constructor(message: string, status: number) {
       super(message);
       this.status = status;
       this.name = 'ApiError';
     }
   }
   
   export const handleApiError = (error: unknown) => {
     if (axios.isAxiosError(error)) {
       const status = error.response?.status || 500;
       const message = error.response?.data?.message || error.message;
       
       // Handle specific error codes
       switch (status) {
         case 401:
           // Handle unauthorized
           break;
         case 403:
           // Handle forbidden
           break;
         // Other cases
       }
       
       throw new ApiError(message, status);
     }
     
     throw error;
   };
   ```
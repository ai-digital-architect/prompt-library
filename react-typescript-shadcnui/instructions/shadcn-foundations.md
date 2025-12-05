---
description: "Prompts for scaffolding application layouts with Tailwind/shadcn"
globs: 
  - "src/App.tsx"
  - "src/layouts/**/*"
keywords: ["scaffold", "layout", "shell", "sidebar"]
---

# Shadcn Foundation Prompts

## Prompt: App Scaffolding
"Scaffold a root layout for a React application.
1. Create a `RootLayout` component that acts as the shell.
2. Use a **Sidebar Layout**:
   - Fixed Sidebar on the left (w-64, hidden on mobile).
   - Top Header (h-16, sticky).
   - Main Content Area (scrollable).
3. Use Tailwind classes like `flex`, `h-screen`, `sticky`, `border-r`, `border-b`.
4. Use `bg-background` and `text-foreground` to ensure dark mode compatibility.
5. In the Sidebar, create a navigation list using `Button` components with `variant='ghost'` and `justify-start`."

## Prompt: Dashboard Grid
"Create a Dashboard View using Tailwind Grid.
- Container: `grid gap-4 md:grid-cols-2 lg:grid-cols-4`.
- **Stats Cards**: Create 4 cards at the top. Use the `<Card>` component. Inside, use `<CardHeader>` for the title (text-sm, text-muted-foreground) and `<CardContent>` for the bold value (text-2xl).
- **Main Chart**: A large card spanning 2 columns and 2 rows (`col-span-2 row-span-2`) .
- **Recent Sales**: A list card spanning 1 column."
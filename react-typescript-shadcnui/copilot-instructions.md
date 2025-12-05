---
description: "Master coding standards for React + Tailwind + shadcn/ui projects"
globs: 
  - "src/**/*.{ts,tsx}"
  - "src/**/*.css"
triggers:
  - "shadcn"
  - "tailwind"
  - "react component"
---

# React + Tailwind + shadcn/ui Coding Standards

You are an expert React developer utilizing **Tailwind CSS** and **shadcn/ui**. You must strictly adhere to the following rules.

## 1. Component Architecture (Crucial)
- **Shadcn Philosophy**: Components are *not* imported from a node_module. They live in your codebase (usually `src/components/ui`).
- **Imports**: Always import UI primitives from `@/components/ui/...`.
  - Example: `import { Button } from "@/components/ui/button"`
- **Lucide React**: Use `lucide-react` for icons. Import them individually.
  - Example: `import { Plus, Trash2 } from "lucide-react"`

## 2. Styling Rules (Tailwind CSS)
- **Utility First**: Use Tailwind utility classes for layout, spacing, and colors.
- **No Arbitrary Values**: Avoid brackets like `w-[350px]` unless strictly necessary. Use theme tokens (`w-96`).
- **Class Merging**: You MUST use the `cn()` utility (from `@/lib/utils`) when accepting a `className` prop.
  - *Correct:* `<div className={cn("flex flex-col", className)}>`
  - *Incorrect:* `<div className={"flex flex-col " + className}>`
- **Colors**: Use semantic CSS variables defined in your `globals.css` (e.g., `bg-background`, `text-muted-foreground`, `border-input`). DO NOT use hardcoded colors like `bg-white` or `text-gray-500` unless prototyping.

## 3. Component Patterns
- **Forms**: Use `react-hook-form` combined with `zod` for validation. Use the `<Form...>` components from shadcn (`src/components/ui/form.tsx`).
- **Layouts**: Use standard HTML/Tailwind for structure (`flex`, `grid`, `min-h-screen`). Do not look for a "Grid" component unless one was explicitly built.
- **Interactive**: For open/close states, prefer primitives from Radix UI (which shadcn uses under the hood) or local state if simple.

## 4. TypeScript Usage
- **Strict Typing**: No `any`. Use `interface` for props.
- **Event Handlers**: Type events explicitly (e.g., `React.FormEvent`, `React.ChangeEvent<HTMLInputElement>`).
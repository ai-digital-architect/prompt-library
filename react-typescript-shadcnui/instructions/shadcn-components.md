---
description: "Recipes for complex shadcn components (Forms, Tables)"
globs: 
  - "src/features/**/*"
keywords: ["form", "zod", "table", "tanstack"]
---

# Shadcn Component Recipes

## Prompt: Zod Form
"Create a 'Profile Settings' form using `react-hook-form`, `zod`, and shadcn Form components.
1. **Schema**: Define a zod schema with `username` (min 2 chars) and `email` (valid email).
2. **Components**: Use `<Form>`, `<FormField>`, `<FormItem>`, `<FormLabel>`, `<FormControl>`, `<FormDescription>`, and `<FormMessage>`.
3. **Layout**: Stack the fields vertically with `space-y-6`.
4. **Submit**: A generic submit handler that logs data to console.
5. Ensure the Input components are imported from `@/components/ui/input`."

## Prompt: Data Table (TanStack)
"Build a 'Users Table' using the shadcn Data Table pattern (TanStack Table).
1. **Columns Definition**: Create a `columns.tsx` file. Define columns for `id`, `name`, `email`, and `status`.
2. **Actions**: Add a 'Row Actions' cell using a `<DropdownMenu>` with options 'Edit' and 'Delete'.
3. **DataTable Component**: Create a reusable `DataTable` component that accepts `columns` and `data`.
4. **Styling**: Ensure the table uses the `<Table>` components (`TableHeader`, `TableRow`, `TableHead`, `TableBody`, `TableCell`) from `@/components/ui/table`."

## Prompt: Dialog Pattern
"Create a 'Delete Confirmation' modal.
- Use `<Dialog>` components: `DialogTrigger`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogDescription`, `DialogFooter`.
- **Trigger**: A button with `variant='destructive'`.
- **Footer**: A 'Cancel' button (variant='outline') and a 'Confirm' button (variant='destructive').
- Ensure proper accessibility descriptions are included."
---
description: "Prompts for Unit and Integration testing"
globs: 
  - "src/**/*.test.tsx"
keywords: ["vitest", "testing-library", "unit test"]
---

# React Testing Prompts

## Prompt: Component Test
"Write a unit test for `[Component Name]`.
1. Use `render` from `@testing-library/react`.
2. Test the 'Happy Path': User enters data, clicks submit, success message appears.
3. Test 'Error States': Invalid input triggers validation text.
4. Mock any network requests using `MSW` (Mock Service Worker) or simple function spies if it's a pure UI test.
5. Do NOT test internal state directly; test what the user sees."

## Prompt: Hook Test
"Write a test for the custom hook `use[HookName]`.
1. Use `renderHook` from `@testing-library/react`.
2. Assert initial return values.
3. Use `act()` if the hook performs state updates.
4. Verify the final state after the action."
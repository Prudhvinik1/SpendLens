# CLAUDE.md - AI Assistant Guidelines for SpendLens

> This file provides context and guidelines for AI assistants (like Claude) working on the SpendLens codebase.

## Project Overview

**SpendLens** is a financial management and expense tracking application. The project is currently in its initial setup phase.

**Repository**: Prudhvinik1/SpendLens
**Status**: New project - under initial development

---

## Codebase Structure

> *This section should be updated as the project structure evolves.*

```
SpendLens/
├── CLAUDE.md              # AI assistant guidelines (this file)
├── README.md              # Project documentation (to be added)
├── package.json           # Dependencies and scripts (to be added)
└── ...                    # Source code (to be added)
```

### Planned Architecture

When implementing features, consider organizing the codebase with these common patterns:

- **`/src`** - Main source code
- **`/src/components`** - Reusable UI components
- **`/src/pages` or `/src/views`** - Page-level components
- **`/src/services` or `/src/api`** - API calls and external service integrations
- **`/src/utils` or `/src/lib`** - Utility functions and helpers
- **`/src/hooks`** - Custom React hooks (if using React)
- **`/src/store` or `/src/state`** - State management
- **`/src/types`** - TypeScript type definitions
- **`/tests` or `/__tests__`** - Test files
- **`/public`** - Static assets

---

## Technology Stack

> *Update this section once the technology choices are finalized.*

Potential technologies to consider for a financial tracking app:

- **Frontend**: React, Vue, or Next.js
- **Backend**: Node.js/Express, Python/FastAPI, or serverless functions
- **Database**: PostgreSQL, MongoDB, or SQLite
- **Authentication**: Auth0, Firebase Auth, or custom JWT
- **Styling**: Tailwind CSS, styled-components, or CSS Modules
- **Testing**: Jest, Vitest, Playwright, or Cypress

---

## Development Workflow

### Getting Started

```bash
# Clone the repository
git clone <repository-url>
cd SpendLens

# Install dependencies (once package.json is set up)
npm install  # or yarn install / pnpm install

# Start development server
npm run dev  # or equivalent command
```

### Common Commands

> *Update these once scripts are defined in package.json*

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run test` | Run test suite |
| `npm run lint` | Run linter |
| `npm run format` | Format code |

### Git Workflow

1. **Branch Naming**: Use descriptive branch names
   - `feature/` - New features (e.g., `feature/expense-categories`)
   - `fix/` - Bug fixes (e.g., `fix/login-redirect`)
   - `refactor/` - Code refactoring
   - `docs/` - Documentation updates
   - `claude/` - AI-assisted development branches

2. **Commit Messages**: Write clear, descriptive commit messages
   - Use present tense ("Add feature" not "Added feature")
   - Keep the first line under 72 characters
   - Reference issue numbers when applicable

3. **Pull Requests**: Include a clear description of changes and testing done

---

## Code Conventions

### General Guidelines

- **Keep it simple**: Avoid over-engineering; implement only what's needed
- **DRY (Don't Repeat Yourself)**: Extract repeated code into reusable functions
- **Single Responsibility**: Each function/component should do one thing well
- **Meaningful Names**: Use descriptive names for variables, functions, and files
- **Comments**: Write comments for complex logic, not obvious code

### File Naming

- **Components**: PascalCase (e.g., `ExpenseCard.tsx`, `Dashboard.vue`)
- **Utilities/Helpers**: camelCase (e.g., `formatCurrency.ts`, `dateUtils.ts`)
- **Constants**: SCREAMING_SNAKE_CASE for values, camelCase for files
- **Test Files**: `*.test.ts`, `*.spec.ts`, or in `__tests__/` directory

### TypeScript Conventions (if using TypeScript)

- Prefer explicit types over `any`
- Use interfaces for object shapes, types for unions/intersections
- Export types alongside their implementations
- Use strict mode in tsconfig.json

### Code Style

- Use consistent formatting (Prettier recommended)
- Use ESLint for code quality
- Prefer `const` over `let`, avoid `var`
- Use async/await over raw Promises
- Handle errors gracefully with try/catch

---

## Domain-Specific Knowledge

### Financial/Expense Tracking Concepts

When working on SpendLens, be aware of these domain concepts:

- **Transactions**: Individual income or expense records
- **Categories**: Classification of expenses (food, transport, utilities, etc.)
- **Budgets**: Planned spending limits by category or time period
- **Accounts**: Bank accounts, credit cards, cash, etc.
- **Recurring Transactions**: Regular expenses (subscriptions, bills)
- **Reports**: Aggregated views of financial data over time

### Data Sensitivity

- **Never log sensitive financial data** (account numbers, full amounts in debug logs)
- **Validate all user inputs** especially monetary values
- **Use proper decimal handling** for currency (avoid floating-point errors)
- **Implement proper authentication** before accessing user financial data

---

## Testing Guidelines

### Test Types

1. **Unit Tests**: Test individual functions and components in isolation
2. **Integration Tests**: Test component interactions and API integrations
3. **E2E Tests**: Test complete user flows

### Testing Best Practices

- Write tests for critical business logic (especially calculations)
- Mock external services and APIs
- Test edge cases (zero amounts, negative values, currency formatting)
- Maintain test coverage for financial calculations

---

## AI Assistant Guidelines

### When Working on This Codebase

1. **Read before writing**: Always read existing code before making changes
2. **Stay focused**: Only make changes that are directly requested
3. **Preserve style**: Match existing code patterns and formatting
4. **Don't over-engineer**: Keep solutions simple and maintainable
5. **Security first**: Be especially careful with financial data handling

### Things to Avoid

- Adding features not explicitly requested
- Creating unnecessary abstractions or utilities
- Adding excessive error handling for impossible cases
- Modifying unrelated code while fixing bugs
- Creating documentation files unless requested

### Code Review Checklist

Before completing a task, verify:

- [ ] Code compiles/builds without errors
- [ ] Tests pass (if tests exist)
- [ ] No security vulnerabilities introduced
- [ ] Changes are focused on the requested task
- [ ] Code follows existing patterns and conventions

---

## Environment Variables

> *Update this section when environment variables are defined*

Expected environment variables (create a `.env.local` file):

```env
# Database
DATABASE_URL=

# Authentication
AUTH_SECRET=

# API Keys
API_KEY=

# Environment
NODE_ENV=development
```

**Never commit `.env` files or secrets to the repository.**

---

## Troubleshooting

### Common Issues

> *This section will be populated as common issues are discovered*

1. **Issue**: [Description]
   - **Solution**: [Steps to resolve]

---

## Resources

- [Project Repository](https://github.com/Prudhvinik1/SpendLens)
- [Issue Tracker](https://github.com/Prudhvinik1/SpendLens/issues)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-25 | Initial CLAUDE.md created | AI Assistant |

---

*This document should be updated as the project evolves. When adding new patterns, conventions, or important context, please update the relevant sections.*

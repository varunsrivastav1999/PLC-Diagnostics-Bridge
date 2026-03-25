# Contributing to PLC Diagnostics Bridge

Thank you for your interest in contributing to PLC Diagnostics Bridge! We welcome contributions from the community.

## Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## How to Contribute

### Reporting Bugs

- Use the [GitHub Issues](https://github.com/yourusername/plc-diagnostics-bridge/issues) to report bugs
- Include detailed steps to reproduce the issue
- Include your environment details (OS, Python version, etc.)

### Suggesting Features

- Open a [GitHub Discussion](https://github.com/yourusername/plc-diagnostics-bridge/discussions) for feature requests
- Describe the feature and its use case
- Consider if the feature fits the project's scope

### Contributing Code

1. **Fork the repository** and create your branch from `main`
2. **Set up development environment**:
   ```bash
   # Clone your fork
   git clone https://github.com/yourusername/plc-diagnostics-bridge.git
   cd plc-diagnostics-bridge

   # Install dependencies
   pip install -r backend/requirements.txt
   cd frontend && npm install && cd ..
   ```
3. **Make your changes** following our coding standards
4. **Test your changes**:
   ```bash
   # Backend tests
   cd backend
   python -m pytest

   # Frontend tests (if any)
   cd frontend
   npm run test
   ```
5. **Commit your changes** with clear commit messages
6. **Push to your fork** and submit a Pull Request

## Development Guidelines

### Python Backend
- Follow PEP 8 style guidelines
- Use type hints
- Write docstrings for functions and classes
- Add tests for new functionality

### Vue.js Frontend
- Follow Vue.js style guide
- Use TypeScript for new components
- Maintain consistent component structure

### Docker
- Keep images minimal and secure
- Use multi-stage builds where possible
- Test builds on multiple architectures

## Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

## Testing

- Write unit tests for new features
- Test PLC connections in isolated environments
- Ensure Docker builds work correctly

## Documentation

- Update README.md for significant changes
- Add docstrings to new functions
- Update API documentation

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

## Questions?

Feel free to open a [Discussion](https://github.com/yourusername/plc-diagnostics-bridge/discussions) or contact the maintainers.
# FLEXT LDIF - Enterprise LDIF Processing Library

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Type Checked](https://img.shields.io/badge/typed-mypy-blue.svg)](https://mypy.readthedocs.io/)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-black.svg)](https://github.com/astral-sh/ruff)

**FLEXT LDIF** is a modern, enterprise-grade LDIF (LDAP Data Interchange Format) processing library built with **Clean Architecture** and **Domain-Driven Design** principles using the **flext-core** foundation.

## Quick Start

### Installation

```bash
pip install flext-ldif
```

### Simple Usage

```python
from flext_ldif import parse_ldif, write_ldif, validate_ldif

# Parse LDIF content
ldif_content = """
dn: cn=John Doe,ou=people,dc=example,dc=com
cn: John Doe
objectClass: person
objectClass: inetOrgPerson
mail: john.doe@example.com
"""

# Parse entries
entries = parse_ldif(ldif_content)
print(f"Parsed {len(entries)} entries")

# Validate LDIF
is_valid = validate_ldif(ldif_content)
print(f"LDIF is valid: {is_valid}")

# Write back to LDIF format
output = write_ldif(entries)
print(output)
```

### Advanced Usage

```python
from flext_ldif import (
    FlextLdifEntry,
    FlextLdifParser,
    FlextLdifValidator,
    FlextLdifDistinguishedName,
    FlextLdifAttributes
)

# Create entry programmatically
dn = FlextLdifDistinguishedName.model_validate({
    "value": "cn=Jane Smith,ou=users,dc=company,dc=com"
})

attributes = FlextLdifAttributes.model_validate({
    "attributes": {
        "cn": ["Jane Smith"],
        "objectClass": ["person", "organizationalPerson"],
        "mail": ["jane.smith@company.com"],
        "sn": ["Smith"],
        "givenName": ["Jane"]
    }
})

entry = FlextLdifEntry.model_validate({
    "dn": dn,
    "attributes": attributes
})

# Validate entry
entry.validate_domain_rules()

# Check object classes
if entry.has_object_class("person"):
    print("Entry is a person")

# Get attribute values
mail_addresses = entry.get_attribute_values("mail")
print(f"Email addresses: {mail_addresses}")

# Convert to LDIF format
ldif_output = entry.to_ldif()
print(ldif_output)
```

## <� Architecture

FLEXT LDIF follows **Clean Architecture** principles with clear separation of concerns:

```
flext_ldif/
   domain/           # <� Core business logic
      entities.py   # Business entities with identity
      values.py     # Immutable value objects
      aggregates.py # Aggregate roots
      events.py     # Domain events
      specifications.py # Business rules
   infrastructure/   # =' External concerns
      di_container.py # Dependency injection
   models.py         # =� Data models
   parser.py         # =� LDIF parsing
   processor.py      # � Processing logic
   validator.py      #  Validation
   writer.py         # =� LDIF writing
   utils.py          # =� Utilities
```

### Core Principles

- **<� FlextLdif Prefixing**: All public classes use `FlextLdif` prefix for clarity
- **<� flext-core Foundation**: Built on flext-core patterns (FlextEntity, FlextValueObject, FlextResult)
- **= Type Safety**: Full mypy strict type checking
- **=� Code Quality**: Lint-free, PEP compliant code
- **>� Test Coverage**: Comprehensive test suite
- **=� Simple Imports**: All functionality available at root level

## <� Key Features

### =' Simple API

- **Root-level imports**: `from flext_ldif import parse_ldif, FlextLdifEntry`
- **Intuitive functions**: `parse_ldif()`, `write_ldif()`, `validate_ldif()`
- **Backward compatibility**: Legacy aliases still work

### <� Enterprise Architecture

- **Domain-Driven Design**: Clear business logic separation
- **Clean Architecture**: Dependency inversion, testable code
- **SOLID Principles**: Maintainable, extensible design
- **Event-Driven**: Domain events for integration

### = Type Safety & Quality

- **Python 3.13+**: Modern Python features
- **MyPy Strict**: Full static type checking
- **Ruff Linting**: Fast, comprehensive code analysis
- **PEP Compliant**: Follows Python standards

### � Performance

- **Efficient Parsing**: Optimized LDIF processing
- **Memory Conscious**: Lazy loading where appropriate
- **Hierarchical Sorting**: DN-based ordering
- **Batch Operations**: Process multiple entries efficiently

## =� API Reference

### Core Classes

#### FlextLdifEntry

```python
# Create entry
entry = FlextLdifEntry.model_validate({
    "dn": "cn=user,dc=example,dc=com",
    "attributes": {
        "cn": ["user"],
        "objectClass": ["person"]
    }
})

# Methods
entry.get_object_classes() -> list[str]
entry.has_object_class(object_class: str) -> bool
entry.get_attribute_values(name: str) -> list[str]
entry.has_attribute(name: str) -> bool
entry.to_ldif() -> str
entry.validate_domain_rules() -> None
```

#### FlextLdifDistinguishedName

```python
dn = FlextLdifDistinguishedName.model_validate({
    "value": "cn=user,ou=people,dc=example,dc=com"
})

# Methods
dn.get_rdn() -> str
dn.get_parent_dn() -> FlextLdifDistinguishedName | None
dn.is_child_of(other: FlextLdifDistinguishedName) -> bool
dn.get_depth() -> int
```

#### FlextLdifAttributes

```python
attrs = FlextLdifAttributes.model_validate({
    "attributes": {"cn": ["user"], "mail": ["user@example.com"]}
})

# Methods
attrs.get_values(name: str) -> list[str]
attrs.get_single_value(name: str) -> str | None
attrs.has_attribute(name: str) -> bool
attrs.add_value(name: str, value: str) -> FlextLdifAttributes
attrs.remove_value(name: str, value: str) -> FlextLdifAttributes
```

### Processing Classes

#### FlextLdifParser

```python
parser = FlextLdifParser()
result = parser.parse_ldif_content(ldif_content)
result = parser.parse_ldif_file(file_path)
```

#### FlextLdifValidator

```python
validator = FlextLdifValidator()
result = validator.validate_entry(entry)
result = validator.validate_entries(entries)
```

#### FlextLdifWriter

```python
writer = FlextLdifWriter()
result = writer.write_entries_to_file(file_path, entries)
result = writer.write_flext_entries_to_file(file_path, flext_entries)
```

#### FlextLdifProcessor

```python
processor = FlextLdifProcessor()
result = processor.parse_ldif_content(content)
result = processor.validate_entries(entries)
result = processor.filter_entries(entries, specification)
```

## >� Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=flext_ldif

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

## =' Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/flext-sh/flext-ldif.git
cd flext-ldif

# Install dependencies
poetry install

# Run quality checks
make check

# Run tests
make test

# Build package
make build
```

### Code Quality

```bash
# Lint code
ruff check .

# Format code
ruff format .

# Type checking
mypy .

# Run all checks
make lint
```

## = Migration Guide

### From Legacy LDIF Libraries

```python
# Before (legacy)
import ldif
from ldif import LDIFParser

# After (FLEXT LDIF)
from flext_ldif import FlextLdifParser, parse_ldif

# Simple parsing
entries = parse_ldif(ldif_content)

# Advanced parsing
parser = FlextLdifParser()
result = parser.parse_ldif_content(ldif_content)
```

### From Complex Imports

```python
# L Old complex imports (deprecated)
from flext_ldif.domain.entities import FlextLdifEntry
from flext_ldif.infrastructure.parsers import LDIFParser

#  New simple imports
from flext_ldif import FlextLdifEntry, FlextLdifParser
```

## > Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Guidelines

1. **Follow flext-core patterns**
2. **Maintain type safety** (mypy strict)
3. **Write comprehensive tests**
4. **Keep code lint-free** (ruff)
5. **Document public APIs**
6. **Respect existing architecture**

## =� License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## = Related Projects

- **[flext-core](https://github.com/flext-sh/flext-core)** - Foundation library
- **[flext-cli](https://github.com/flext-sh/flext-cli)** - Command-line tools
- **[flext-web](https://github.com/flext-sh/flext-web)** - Web framework integration

## <� Support

- **Documentation**: [GitHub README](https://github.com/flext-sh/flext-ldif)
- **Issues**: [GitHub Issues](https://github.com/flext-sh/flext-ldif/issues)
- **Discussions**: [GitHub Discussions](https://github.com/flext-sh/flext-ldif/discussions)

---

**Built with d by the FLEXT Team**

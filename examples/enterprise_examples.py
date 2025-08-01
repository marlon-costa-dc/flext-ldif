"""Enterprise examples demonstrating all flext-ldif functionality.

This module provides comprehensive examples showing how to use flext-ldif
in enterprise scenarios with real-world LDIF processing tasks.
"""

from __future__ import annotations

import tempfile
import time
from pathlib import Path

from flext_ldif import (
    FlextLdifAPI,
    FlextLdifConfig,
    TLdif,
    flext_ldif_get_api,
    flext_ldif_parse,
    flext_ldif_validate,
    flext_ldif_write,
)


def example_basic_ldif_processing() -> None:
    """Example: Basic LDIF parsing, validation, and writing."""
    # Sample LDIF content
    ldif_content = """dn: cn=John Doe,ou=people,dc=example,dc=com
objectClass: person
objectClass: inetOrgPerson
cn: John Doe
sn: Doe
givenName: John
mail: john.doe@example.com
uid: johndoe

dn: cn=Jane Smith,ou=people,dc=example,dc=com
objectClass: person
objectClass: organizationalPerson
cn: Jane Smith
sn: Smith
givenName: Jane
mail: jane.smith@example.com
uid: janesmith

"""

    # Using TLdif core functionality
    parse_result = TLdif.parse(ldif_content)

    if parse_result.is_success:
        entries = parse_result.data

        # Validate entries
        validate_result = TLdif.validate_entries(entries)
        if validate_result.is_success:
            pass

        # Write back to LDIF
        write_result = TLdif.write(entries)
        if write_result.is_success:
            pass


def example_api_usage() -> None:
    """Example: Using FlextLdifAPI for advanced processing."""
    ldif_content = """dn: ou=people,dc=company,dc=com
objectClass: organizationalUnit
ou: people
description: People container

dn: cn=Alice Johnson,ou=people,dc=company,dc=com
objectClass: person
objectClass: inetOrgPerson
cn: Alice Johnson
sn: Johnson
givenName: Alice
mail: alice.johnson@company.com
uid: ajohnson
title: Software Engineer

dn: cn=Bob Wilson,ou=people,dc=company,dc=com
objectClass: person
objectClass: organizationalPerson
cn: Bob Wilson
sn: Wilson
givenName: Bob
mail: bob.wilson@company.com
uid: bwilson
title: Manager

dn: cn=developers,ou=groups,dc=company,dc=com
objectClass: groupOfNames
cn: developers
member: cn=Alice Johnson,ou=people,dc=company,dc=com

"""

    # Initialize API with configuration
    config = FlextLdifConfig.model_validate(
        {
            "strict_validation": True,
            "max_entries": 100,
        },
    )
    api = FlextLdifAPI(config)

    parse_result = api.parse(ldif_content)

    if parse_result.is_success:
        entries = parse_result.data

        # Filter person entries
        person_result = api.filter_persons(entries)
        if person_result.is_success:
            person_entries = person_result.data
            for entry in person_entries:
                pass

        # Filter by objectClass
        api.filter_by_objectclass(entries, "inetOrgPerson")

        # Find specific entry by DN
        target_dn = "cn=Alice Johnson,ou=people,dc=company,dc=com"
        found_entry = api.find_entry_by_dn(entries, target_dn)
        if found_entry:
            pass

        # Sort hierarchically
        sort_result = api.sort_hierarchically(entries)
        if sort_result.is_success:
            sorted_entries = sort_result.data
            for entry in sorted_entries:
                str(entry.dn).count(",")


def example_file_operations() -> None:
    """Example: File-based LDIF operations."""
    ldif_content = """dn: dc=filetest,dc=com
objectClass: top
objectClass: domain
dc: filetest

dn: ou=users,dc=filetest,dc=com
objectClass: top
objectClass: organizationalUnit
ou: users

dn: cn=Test User,ou=users,dc=filetest,dc=com
objectClass: top
objectClass: person
cn: Test User
sn: User
mail: test.user@filetest.com

"""

    # Create temporary files
    with tempfile.NamedTemporaryFile(
        encoding="utf-8",
        mode="w",
        delete=False,
        suffix=".ldif",
    ) as input_file:
        input_file.write(ldif_content)
        input_path = Path(input_file.name)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ldif") as output_file:
        output_path = Path(output_file.name)

    try:
        # Using TLdif for file operations
        read_result = TLdif.read_file(input_path)
        if read_result.is_success:
            entries = read_result.data

            # Process entries
            api = FlextLdifAPI()
            person_result = api.filter_persons(entries)
            if person_result.is_success:
                person_entries = person_result.data

                # Write to output file
                write_result = TLdif.write_file(person_entries, output_path)
                if write_result.is_success:
                    # Verify output
                    if output_path.exists():
                        output_path.read_text(encoding="utf-8")

        # Using API for file operations
        api = FlextLdifAPI()
        file_parse_result = api.parse_file(input_path)
        if file_parse_result.is_success:
            pass

    finally:
        # Cleanup
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)


def example_convenience_functions() -> None:
    """Example: Using convenience functions for simple tasks."""
    ldif_content = """dn: cn=convenience,dc=example,dc=com
objectClass: person
cn: convenience
sn: example
mail: convenience@example.com

"""

    # Parse using convenience function
    entries = flext_ldif_parse(ldif_content)

    # Validate using convenience function
    flext_ldif_validate(ldif_content)

    # Write using convenience function
    flext_ldif_write(entries)

    # Global API instance
    api = flext_ldif_get_api()
    result = api.parse(ldif_content)
    if result.is_success:
        pass


def example_configuration_scenarios() -> None:
    """Example: Different configuration scenarios."""
    # Test content with multiple entries
    large_ldif = ""
    for i in range(15):
        large_ldif += f"""dn: cn=user{i:02d},ou=people,dc=config,dc=com
objectClass: person
cn: user{i:02d}
sn: user{i:02d}

"""

    strict_config = FlextLdifConfig.model_validate(
        {
            "strict_validation": True,
            "max_entries": 10,
            "max_entry_size": 1024,
        },
    )

    strict_api = FlextLdifAPI(strict_config)
    strict_result = strict_api.parse(large_ldif)
    if strict_result.is_success:
        pass

    permissive_config = FlextLdifConfig.model_validate(
        {
            "strict_validation": False,
            "max_entries": 100,
            "max_entry_size": 10240,
        },
    )

    permissive_api = FlextLdifAPI(permissive_config)
    permissive_result = permissive_api.parse(large_ldif)
    if permissive_result.is_success:
        pass


def example_error_handling() -> None:
    """Example: Proper error handling patterns."""
    # Invalid LDIF content
    invalid_ldif = """This is not LDIF content
It has no proper structure
And should fail parsing"""

    parse_result = TLdif.parse(invalid_ldif)
    if not parse_result.is_success:
        pass

    # File not found error
    nonexistent_file = Path("/nonexistent/path/file.ldif")
    file_result = TLdif.read_file(nonexistent_file)
    if not file_result.is_success:
        pass

    # Validation errors
    incomplete_ldif = """dn: cn=incomplete,dc=example,dc=com
cn: incomplete
# Missing objectClass"""

    api = FlextLdifAPI()
    incomplete_result = api.parse(incomplete_ldif)
    if incomplete_result.is_success:
        # Parse might succeed, but validation should catch issues
        entries = incomplete_result.data
        validate_result = api.validate(entries)
        if not validate_result.is_success:
            pass


def example_advanced_filtering() -> None:
    """Example: Advanced filtering and processing."""
    complex_ldif = """dn: dc=advanced,dc=com
objectClass: top
objectClass: domain
dc: advanced

dn: ou=people,dc=advanced,dc=com
objectClass: top
objectClass: organizationalUnit
ou: people

dn: ou=groups,dc=advanced,dc=com
objectClass: top
objectClass: organizationalUnit
ou: groups

dn: cn=John Engineer,ou=people,dc=advanced,dc=com
objectClass: top
objectClass: person
objectClass: inetOrgPerson
cn: John Engineer
sn: Engineer
title: Software Engineer
departmentNumber: IT

dn: cn=Mary Manager,ou=people,dc=advanced,dc=com
objectClass: top
objectClass: person
objectClass: organizationalPerson
cn: Mary Manager
sn: Manager
title: Engineering Manager
departmentNumber: IT

dn: cn=Bob Admin,ou=people,dc=advanced,dc=com
objectClass: top
objectClass: person
cn: Bob Admin
sn: Admin
title: System Administrator
departmentNumber: IT

dn: cn=engineers,ou=groups,dc=advanced,dc=com
objectClass: top
objectClass: groupOfNames
cn: engineers
member: cn=John Engineer,ou=people,dc=advanced,dc=com

dn: cn=managers,ou=groups,dc=advanced,dc=com
objectClass: top
objectClass: groupOfNames
cn: managers
member: cn=Mary Manager,ou=people,dc=advanced,dc=com

"""

    api = FlextLdifAPI()
    parse_result = api.parse(complex_ldif)

    if parse_result.is_success:
        entries = parse_result.data

        # Filter different types

        # Person entries
        person_entries = api.filter_persons(entries).data

        # inetOrgPerson entries (more specific)
        api.filter_by_objectclass(entries, "inetOrgPerson")

        # Group entries
        api.filter_by_objectclass(entries, "groupOfNames")

        # Organizational units
        api.filter_by_objectclass(entries, "organizationalUnit")

        # Custom filtering example
        def filter_by_title_containing(entries: list, keyword: str) -> list:
            """Custom filter for entries with title containing keyword."""
            result = []
            for entry in entries:
                title_attr = entry.get_attribute("title")
                if title_attr and any(
                    keyword.lower() in title.lower() for title in title_attr
                ):
                    result.append(entry)
            return result

        filter_by_title_containing(person_entries, "engineer")

        filter_by_title_containing(person_entries, "manager")

        # Hierarchical analysis
        sort_result = api.sort_hierarchically(entries)
        if sort_result.is_success:
            sorted_entries = sort_result.data
            for entry in sorted_entries:
                depth = str(entry.dn).count(",")
                "   " + "  " * depth
                "domain" if entry.has_object_class(
                    "domain",
                ) else "OU" if entry.has_object_class(
                    "organizationalUnit",
                ) else "person" if entry.has_object_class(
                    "person",
                ) else "group" if entry.has_object_class("groupOfNames") else "other"


def example_performance_monitoring() -> None:
    """Example: Performance monitoring and optimization."""
    # Generate larger dataset
    large_ldif = (
        "dn: dc=perf,dc=com\nobjectClass: top\nobjectClass: domain\ndc: perf\n\n"
    )

    for i in range(100):
        large_ldif += f"""dn: cn=user{i:03d},dc=perf,dc=com
objectClass: top
objectClass: person
objectClass: inetOrgPerson
cn: user{i:03d}
sn: User{i:03d}
givenName: Test{i:03d}
mail: user{i:03d}@perf.com
uid: user{i:03d}
employeeNumber: EMP{i:03d}
description: Test user {i:03d} for performance monitoring

"""

    # Measure parsing performance
    start_time = time.time()
    parse_result = TLdif.parse(large_ldif)
    parse_time = time.time() - start_time

    if parse_result.is_success:
        entries = parse_result.data

        # Measure filtering performance
        api = FlextLdifAPI()

        start_time = time.time()
        person_result = api.filter_persons(entries)
        filter_time = time.time() - start_time

        if person_result.is_success:
            # Measure writing performance
            start_time = time.time()
            write_result = TLdif.write(person_result.data)
            write_time = time.time() - start_time

            if write_result.is_success:
                # Total performance
                parse_time + filter_time + write_time


def main() -> None:
    """Run all enterprise examples."""
    # Run all examples
    example_basic_ldif_processing()
    example_api_usage()
    example_file_operations()
    example_convenience_functions()
    example_configuration_scenarios()
    example_error_handling()
    example_advanced_filtering()
    example_performance_monitoring()


if __name__ == "__main__":
    main()

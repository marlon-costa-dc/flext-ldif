#!/usr/bin/env python3
"""Example of running FLEXT-LDIF examples with Docker OpenLDAP container.

This script automatically starts an OpenLDAP container, populates it with test data,
exports LDIF, and demonstrates FLEXT-LDIF processing capabilities.
Perfect for testing and demonstration without needing a manual LDAP setup.
"""

from __future__ import annotations

import asyncio
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from flext_ldif import (
    FlextLdifProcessor,
    FlextLdifValidator,
    parse_ldif,
)
from flext_ldif.domain.specifications import (
    FlextLdifPersonSpecification,
)

# Add src to path for local testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def start_openldap_container() -> bool:
    """Start OpenLDAP container for LDIF testing."""
    try:
        # Stop any existing container
        subprocess.run(
            ["docker", "stop", "flext-ldif-demo", "2>/dev/null"],
            check=False,
            shell=True,
        )
        subprocess.run(
            ["docker", "rm", "flext-ldif-demo", "2>/dev/null"],
            check=False,
            shell=True,
        )

        # Start new container
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                "flext-ldif-demo",
                "-p",
                "3391:389",
                "-e",
                "LDAP_ORGANISATION=FLEXT LDIF Demo Org",
                "-e",
                "LDAP_DOMAIN=flext-ldif.demo",
                "-e",
                "LDAP_ADMIN_PASSWORD=admin123",
                "-e",
                "LDAP_CONFIG_PASSWORD=config123",
                "-e",
                "LDAP_READONLY_USER=false",
                "-e",
                "LDAP_RFC2307BIS_SCHEMA=true",
                "-e",
                "LDAP_BACKEND=mdb",
                "-e",
                "LDAP_TLS=false",
                "-e",
                "LDAP_REMOVE_CONFIG_AFTER_SETUP=true",
                "osixia/openldap:1.5.0",
            ],
            check=True,
        )

        # Wait for container to be ready
        for _attempt in range(30):
            try:
                result = subprocess.run(
                    [
                        "docker",
                        "exec",
                        "flext-ldif-demo",
                        "ldapsearch",
                        "-x",
                        "-H",
                        "ldap://localhost:389",
                        "-D",
                        "cn=admin,dc=flext-ldif,dc=demo",
                        "-w",
                        "admin123",
                        "-b",
                        "dc=flext-ldif,dc=demo",
                        "-s",
                        "base",
                        "(objectClass=*)",
                    ],
                    capture_output=True,
                    check=True,
                )

                if result.returncode == 0:
                    return True

            except subprocess.CalledProcessError:
                time.sleep(1)

        return False

    except (RuntimeError, ValueError, TypeError):
        return False


def populate_test_data() -> bool:
    """Populate OpenLDAP container with comprehensive test data."""
    try:
        test_ldif = """
# Base organization
dn: dc=flext-ldif,dc=demo
objectClass: dcObject
objectClass: organization
dc: flext-ldif
o: FLEXT LDIF Demo Organization

# Organizational units
dn: ou=people,dc=flext-ldif,dc=demo
objectClass: organizationalUnit
ou: people
description: People in the organization

dn: ou=groups,dc=flext-ldif,dc=demo
objectClass: organizationalUnit
ou: groups
description: Groups in the organization

dn: ou=departments,dc=flext-ldif,dc=demo
objectClass: organizationalUnit
ou: departments
description: Company departments

# Departments
dn: ou=Engineering,ou=departments,dc=flext-ldif,dc=demo
objectClass: organizationalUnit
ou: Engineering
description: Software Engineering Department

dn: ou=Marketing,ou=departments,dc=flext-ldif,dc=demo
objectClass: organizationalUnit
ou: Marketing
description: Marketing Department

dn: ou=Sales,ou=departments,dc=flext-ldif,dc=demo
objectClass: organizationalUnit
ou: Sales
description: Sales Department

# Engineering team members
dn: uid=alice.johnson,ou=people,dc=flext-ldif,dc=demo
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
uid: alice.johnson
cn: Alice Johnson
sn: Johnson
givenName: Alice
displayName: Alice Johnson
mail: alice.johnson@flext-ldif.demo
telephoneNumber: +1 555 100 1001
employeeNumber: 10001
departmentNumber: Engineering
title: Senior Software Engineer
description: Full-stack developer specializing in Python and React

dn: uid=bob.smith,ou=people,dc=flext-ldif,dc=demo
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
uid: bob.smith
cn: Bob Smith
sn: Smith
givenName: Bob
displayName: Bob Smith
mail: bob.smith@flext-ldif.demo
telephoneNumber: +1 555 100 1002
employeeNumber: 10002
departmentNumber: Engineering
title: DevOps Engineer
description: Infrastructure and deployment automation specialist

dn: uid=carol.davis,ou=people,dc=flext-ldif,dc=demo
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
uid: carol.davis
cn: Carol Davis
sn: Davis
givenName: Carol
displayName: Carol Davis
mail: carol.davis@flext-ldif.demo
telephoneNumber: +1 555 100 1003
employeeNumber: 10003
departmentNumber: Engineering
title: Engineering Manager
description: Engineering team lead with 10+ years experience

# Marketing team members
dn: uid=david.wilson,ou=people,dc=flext-ldif,dc=demo
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
uid: david.wilson
cn: David Wilson
sn: Wilson
givenName: David
displayName: David Wilson
mail: david.wilson@flext-ldif.demo
telephoneNumber: +1 555 200 2001
employeeNumber: 20001
departmentNumber: Marketing
title: Marketing Manager
description: Digital marketing and brand strategy specialist

dn: uid=eva.brown,ou=people,dc=flext-ldif,dc=demo
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
uid: eva.brown
cn: Eva Brown
sn: Brown
givenName: Eva
displayName: Eva Brown
mail: eva.brown@flext-ldif.demo
telephoneNumber: +1 555 200 2002
employeeNumber: 20002
departmentNumber: Marketing
title: Content Creator
description: Social media and content marketing specialist

# Sales team members
dn: uid=frank.miller,ou=people,dc=flext-ldif,dc=demo
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
uid: frank.miller
cn: Frank Miller
sn: Miller
givenName: Frank
displayName: Frank Miller
mail: frank.miller@flext-ldif.demo
telephoneNumber: +1 555 300 3001
employeeNumber: 30001
departmentNumber: Sales
title: Sales Representative
description: Enterprise sales specialist

dn: uid=grace.taylor,ou=people,dc=flext-ldif,dc=demo
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
uid: grace.taylor
cn: Grace Taylor
sn: Taylor
givenName: Grace
displayName: Grace Taylor
mail: grace.taylor@flext-ldif.demo
telephoneNumber: +1 555 300 3002
employeeNumber: 30002
departmentNumber: Sales
title: Sales Manager
description: Regional sales manager with proven track record

# Groups
dn: cn=Engineering Team,ou=groups,dc=flext-ldif,dc=demo
objectClass: groupOfNames
objectClass: top
cn: Engineering Team
description: All engineering department members
member: uid=alice.johnson,ou=people,dc=flext-ldif,dc=demo
member: uid=bob.smith,ou=people,dc=flext-ldif,dc=demo
member: uid=carol.davis,ou=people,dc=flext-ldif,dc=demo

dn: cn=Marketing Team,ou=groups,dc=flext-ldif,dc=demo
objectClass: groupOfNames
objectClass: top
cn: Marketing Team
description: All marketing department members
member: uid=david.wilson,ou=people,dc=flext-ldif,dc=demo
member: uid=eva.brown,ou=people,dc=flext-ldif,dc=demo

dn: cn=Sales Team,ou=groups,dc=flext-ldif,dc=demo
objectClass: groupOfNames
objectClass: top
cn: Sales Team
description: All sales department members
member: uid=frank.miller,ou=people,dc=flext-ldif,dc=demo
member: uid=grace.taylor,ou=people,dc=flext-ldif,dc=demo

dn: cn=Managers,ou=groups,dc=flext-ldif,dc=demo
objectClass: groupOfNames
objectClass: top
cn: Managers
description: All department managers
member: uid=carol.davis,ou=people,dc=flext-ldif,dc=demo
member: uid=david.wilson,ou=people,dc=flext-ldif,dc=demo
member: uid=grace.taylor,ou=people,dc=flext-ldif,dc=demo

dn: cn=All Employees,ou=groups,dc=flext-ldif,dc=demo
objectClass: groupOfNames
objectClass: top
cn: All Employees
description: All company employees
member: uid=alice.johnson,ou=people,dc=flext-ldif,dc=demo
member: uid=bob.smith,ou=people,dc=flext-ldif,dc=demo
member: uid=carol.davis,ou=people,dc=flext-ldif,dc=demo
member: uid=david.wilson,ou=people,dc=flext-ldif,dc=demo
member: uid=eva.brown,ou=people,dc=flext-ldif,dc=demo
member: uid=frank.miller,ou=people,dc=flext-ldif,dc=demo
member: uid=grace.taylor,ou=people,dc=flext-ldif,dc=demo
"""

        # Write LDIF to temporary file
        with tempfile.NamedTemporaryFile(
            encoding="utf-8",
            mode="w",
            suffix=".ldif",
            delete=False,
        ) as f:
            f.write(test_ldif)
            temp_file = f.name

        # Copy LDIF to container
        subprocess.run(
            [
                "docker",
                "cp",
                temp_file,
                "flext-ldif-demo:/tmp/test_data.ldif",
            ],
            check=True,
        )

        # Import LDIF data
        result = subprocess.run(
            [
                "docker",
                "exec",
                "flext-ldif-demo",
                "ldapadd",
                "-x",
                "-H",
                "ldap://localhost:389",
                "-D",
                "cn=admin,dc=flext-ldif,dc=demo",
                "-w",
                "admin123",
                "-f",
                "/tmp/test_data.ldif",
            ],
            check=False,
            capture_output=True,
        )

        # Clean up temp file
        Path(temp_file).unlink()

        return result.returncode == 0

    except (RuntimeError, ValueError, TypeError):
        return False


def export_ldif_from_container() -> str:
    """Export LDIF data from the container."""
    try:
        result = subprocess.run(
            [
                "docker",
                "exec",
                "flext-ldif-demo",
                "ldapsearch",
                "-x",
                "-H",
                "ldap://localhost:389",
                "-D",
                "cn=admin,dc=flext-ldif,dc=demo",
                "-w",
                "admin123",
                "-b",
                "dc=flext-ldif,dc=demo",
                "-s",
                "sub",
                "(objectClass=*)",
                "-LLL",  # LDIF format without comments
            ],
            capture_output=True,
            check=True,
        )

        return result.stdout.decode()

    except (RuntimeError, ValueError, TypeError):
        return ""


def stop_openldap_container() -> None:
    """Stop and remove OpenLDAP container."""
    try:
        subprocess.run(["docker", "stop", "flext-ldif-demo"], check=False)
        subprocess.run(["docker", "rm", "flext-ldif-demo"], check=False)
    except (RuntimeError, ValueError, TypeError):
        pass


async def run_flext_ldif_examples(ldif_data: str) -> None:
    """Run FLEXT-LDIF examples against real OpenLDAP data."""
    from flext_ldif import (
        modernized_ldif_parse,
        modernized_ldif_write,
    )

    # Example 1: Simple parsing

    entries = parse_ldif(ldif_data)

    # Show some entry details
    for _i, entry in enumerate(entries[:3]):
        if entry.has_attribute("cn"):
            pass
        if entry.has_attribute("objectClass"):
            pass

    if len(entries) > 3:
        pass

    # Example 2: Advanced processing

    processor = FlextLdifProcessor()
    result = processor.parse_ldif_content(ldif_data)

    if result.is_success:
        # Filter person entries
        person_result = processor.filter_person_entries(result.data)
        if person_result.is_success:
            # Show person details
            for person in person_result.data[:3]:
                if person.has_attribute("cn"):
                    person.get_single_attribute("cn")
                    person.get_single_attribute("title") or "N/A"
                    person.get_single_attribute("departmentNumber") or "N/A"

        # Filter valid entries
        valid_result = processor.filter_valid_entries(result.data)
        if valid_result.is_success:
            pass

    # Example 3: Domain specifications

    person_spec = FlextLdifPersonSpecification()

    sum(1 for entry in entries if person_spec.is_satisfied_by(entry))

    # Example 4: Validation

    modernized_ldif_parse(ldif_data)

    validator = FlextLdifValidator()
    validation_result = validator.validate_entries(entries)
    if validation_result.is_success:
        pass

    # Example 5: Write LDIF

    # Filter person entries for writing
    person_entries = [entry for entry in entries if person_spec.is_satisfied_by(entry)]

    if person_entries:
        output_ldif = modernized_ldif_write(person_entries)

        # Save to file
        output_file = Path("flext_ldif_demo_output.ldif")
        output_file.write_text(output_ldif, encoding="utf-8")

        # Show a sample of the output
        for line in output_ldif.split("\n")[:5]:
            if line.strip():
                pass

    # Example 6: Performance measurement

    # Measure parsing performance
    start_time = time.time()
    for _ in range(10):
        parse_ldif(ldif_data)
    parse_time = (time.time() - start_time) / 10

    # Measure validation performance
    start_time = time.time()
    for _ in range(10):
        modernized_ldif_parse(ldif_data)
    (time.time() - start_time) / 10

    len(entries) / max(parse_time, 0.001)


async def main() -> None:
    """Main execution function."""
    # Start container
    if not start_openldap_container():
        return

    # Populate with test data
    if not populate_test_data():
        pass

    try:
        # Export LDIF data
        ldif_data = export_ldif_from_container()
        if not ldif_data:
            return

        # Run examples
        await run_flext_ldif_examples(ldif_data)

    finally:
        # Always cleanup
        stop_openldap_container()


if __name__ == "__main__":
    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        sys.exit(1)

    asyncio.run(main())

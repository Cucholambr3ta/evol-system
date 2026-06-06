# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously.

**Please do NOT report security issues via public GitHub issues.**

To report a security issue:

1. **Email**: Send details to the maintainers via the repository's security
   contact or directly.
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Affected components and versions
3. **Timeline**:
   - Acknowledgment within 48 hours
   - Initial assessment within 1 week
   - Fix and disclosure within 30 days for critical issues

## Scope

Security issues in the following are in scope:
- HMAC gate signing and verification
- Credential storage and permissions (`.evol/.gate-key` at `0600`)
- Supply chain skill installation
- Memoria Persistente safe indexing configuration
- Secret detection and exposure
- Hook blocking of dangerous commands

## Out of Scope

- Social engineering
- Physical security
- Denial of service on external infrastructure

## Security Design

- Gate keys are project-local, never shared
- Runtime state (`.evol/`) is never versioned
- Memoria Persistente index paths are allowlisted, never broad `.` scans
- Hooks block dangerous commands by default
- Strict local network bindings for MCP servers

## PGP/GPG

For sensitive communications, use the repository's security contact.
# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported            |
|---------|----------------------|
| 1.0.x   | ✅ Currently Supported |
| < 1.0   | ❌ End of Life         |

## Reporting a Vulnerability

**Please do NOT create public issues for security vulnerabilities.** Instead, please report security vulnerabilities privately to the maintainers.

### How to Report

1. **Email**: Send a detailed report to [repository owner] if an email is available
2. **GitHub Security Advisory**: Use GitHub's "Report a vulnerability" feature in the Security tab

Please include:

- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact and severity assessment
- Suggested fix (if you have one)

### What to Expect

1. **Acknowledgment**: We'll acknowledge receipt within 48 hours
2. **Assessment**: We'll assess the vulnerability and its impact
3. **Fix**: We'll work on a fix and release a security patch as soon as possible
4. **Disclosure**: We'll coordinate with you on public disclosure timing

## Security Considerations

### XML Processing

This project processes XML files from potentially untrusted sources. Security measures include:

- **XXE Prevention**: All XML parsing is configured to prevent XML External Entity (XXE) attacks
- **Entity Expansion Protection**: Protections against billion laughs / billion giggles attacks
- **DTD Restrictions**: External DTDs are not loaded
- **Schema Validation**: XSD validation is available to verify XML structure

### Best Practices When Using xmlcompare

When using xmlcompare in production:

1. **Validate sources**: Validate XML sources before comparing
2. **Limit file size**: Consider file size limits for very large XML files
3. **Use schema validation**: Enable XSD schema validation when possible
4. **Monitor performance**: Monitor execution time and resource usage for untrusted input
5. **Keep updated**: Always use the latest version which includes security fixes

### Dependencies

We actively monitor our dependencies for security vulnerabilities:

- **Python**: pyyaml, pytest, ruff, lxml
- **Java**: Jackson, Picocli, JUnit

Security updates are released promptly when vulnerabilities are discovered in dependencies.

## Security Best Practices

### For Contributors

- Keep your local repository and tools updated
- Use strong security practices in contributed code
- Don't commit credentials or sensitive data
- Report security issues privately, don't disclose publicly

### For Users

- Keep xmlcompare updated to the latest version
- Keep your Python/Java installation updated
- Validate XML input from untrusted sources
- Use schema validation when possible
- Monitor resource usage when processing untrusted XML

## Vulnerability Reporting

If you discover a security vulnerability in xmlcompare, thank you for reporting it responsibly!

Please note:

- Official security advisories are published only after a fix is available or a reasonable time has passed
- We appreciate responsible disclosure and will credit reporters (unless they wish to remain anonymous)
- Security vulnerabilities reported after a fix is public may not receive a CVE or advisory

## Security Changelog

Please see [CHANGELOG.md](CHANGELOG.md) for security-related updates and fixes.

## Third-Party Security Tools

We welcome security audits and vulnerability reports from automated tools and services:

- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)
- [Snyk](https://snyk.io/)
- [GitHub Advanced Security](https://github.com/features/security)
- Other reputable security scanning tools

## Questions?

If you have security-related questions (not vulnerability reports), please:

1. Check this document and our README
2. Open a public issue if it's not security-sensitive
3. Contact the maintainers privately if needed

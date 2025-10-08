# Versioning Guide

## 🎯 Semantic Versioning Policy

Chimera follows [Semantic Versioning 2.0.0](https://semver.org/) for predictable, meaningful version numbers.

```
MAJOR.MINOR.PATCH[-PRERELEASE]
```

### Version Components

- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features (backward compatible additions)
- **PATCH**: Bug fixes (backward compatible bug fixes)
- **PRERELEASE**: Alpha/beta/rc labels (-alpha, -beta, -rc.1, etc.)

### Version Examples

- `1.0.0`: First stable release
- `1.1.0`: New features added
- `1.1.1`: Bug fixes
- `2.0.0`: Breaking changes
- `1.2.0-alpha.1`: First alpha of new version

## 📋 Current Version

```
0.1.0 - Early MVP Release
Features: Multi-provider AI, persona system, demo mode
Status: Pre-production, breaking changes likely
```

## 🏷️ Git Tags and Releases

### Creating Releases

```bash
# Tag a new release
git tag -a v1.0.0 -m "Release v1.0.0: Production ready"

# Push tags
git push origin --tags

# Create GitHub release from tag
```

### Version File

The VERSION file contains current version and notable changes:

```bash
cat VERSION
0.1.0
Pre-Release: Early MVP with AI conversations
Features: Multi-provider AI, persona system, demo mode
```

## 🔄 Update Process

### For Patch Releases (Bug Fixes)
1. Fix bugs
2. Update tests
3. Commit changes
4. Update VERSION file
5. `git tag -a v0.1.1 -m "v0.1.1: Bug fixes"`
6. Push

### For Minor Releases (New Features)
1. Implement features
2. Update documentation
3. Update tests
4. Update VERSION file
5. `git tag -a v0.2.0 -m "v0.2.0: New features"`
6. Push

### For Major Releases (Breaking Changes)
1. Audit breaking changes
2. Update migration guides
3. Update API documentation
4. Update VERSION file
5. `git tag -a v1.0.0 -m "v1.0.0: Production ready"`
6. Push

## 📊 Version History

### v0.1.0 (Current)
- 🎭 Multi-AI conversation orchestration
- 🤖 32 AI personas with custom provider/model assignment
- ⚙️ Connection manager GUI for API keys
- 🎪 Demo mode for personal installations
- 🖥️ Real-time WebSocket chat interface
- 🏗️ FastAPI + React architecture

## 🔮 Future Milestones

### v0.2.0 (Planned)
- 🔄 Persona learning from conversations
- 📊 Advanced conversation analytics
- 🔐 Premium user features
- 📱 Mobile responsive improvements

### v1.0.0 (Production Ready)
- 🏢 Multi-user enterprise features
- 🔒 Production security hardening
- 📈 Performance optimizations
- 🧪 Comprehensive test coverage
- 📚 Complete API documentation

## 🐛 Stability Expectations

| Version Range | Stability | Support |
|---------------|-----------|---------|
| 0.x.x | Unstable, breaking changes likely | Best effort |
| 1.x.x | Stable API, backwards compatible | Active |
| 1.x.x with -alpha/beta | Experimental features | Limited |

## 🤝 Contributing

When submitting pull requests:
- Include version impact assessment
- Update VERSION file if appropriate
- Follow semantic versioning for all changes

## 📝 Release Notes

See CHANGELOG.md for detailed release notes (coming soon).

---

This versioning policy ensures predictable releases and helps users understand what to expect when upgrading.</content>
</xai:function_call committed to overwriting the file. The creation overwrites the old file.
# SHAM.CASH

Native Android WebView application for https://sham.cash

## Build

### GitHub Actions (recommended)

Push to `main` or open a Pull Request. The APK is built automatically
and uploaded as a workflow artifact.

### Local build

Requirements:
- JDK 17
- Android SDK Platform 35
- Gradle 8.9

```bash
gradle assembleDebug

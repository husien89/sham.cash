# sham.cash

Native Android WebView application.

## Build

GitHub Actions builds the APK automatically. The APK is available from the workflow artifacts.

For a local build:

```bash
gradle wrapper --gradle-version 8.9
./gradlew assembleDebug

# webview-apk

Generates Android APKs that wrap a URL in a WebView.

## Project Structure

- `src/webview_apk.py` - CLI entry point; reads YAML config, renders Jinja2 templates, generates icons, runs Gradle build
- `app/src/main/kotlin/app/webviewapk/MainActivity.kt` - The Android activity (not templated, shared by all builds)
- `templates/` - Jinja2 templates for `build.gradle.kts`, `settings.gradle.kts`, `strings.xml`, `themes.xml`
- `examples/` - Example YAML configs

## How It Works

1. User provides a YAML config with app name, URL, icon, etc.
2. `webview_apk.py` renders templates with the config values, generates mipmap icons, then runs `gradlew assembleDebug`
3. `BuildConfig` fields (APP_URL, APP_HOST, REFRESH_TIMEOUT_MS) are injected via the Gradle template and read at runtime in `MainActivity.kt`

## Smart Refresh

`MainActivity` tracks `lastPauseTime` in `onPause()`. On `onResume()`, if the elapsed time exceeds `BuildConfig.REFRESH_TIMEOUT_MS`, it calls `window.__webviewRefresh()` via `evaluateJavascript()`. The web page opts in by defining this function. Default timeout is 5 minutes (300000ms).

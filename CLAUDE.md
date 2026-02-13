# webview-apk

Generates a lightweight Android APK that wraps a URL in a WebView.

## Usage

```
webview-apk build <config.yaml>
```

The built APK is written to `app/build/outputs/apk/debug/app-debug.apk`.

## Config

See `examples/gitmob.yaml` for a full example.

| Field | Required | Default | Description |
|---|---|---|---|
| `name` | yes | | App name shown in the launcher |
| `id` | yes | | Android application ID (e.g. `com.example.app`) |
| `url` | yes | | URL to load in the WebView |
| `host` | yes | | Hostname used to keep navigation in-app; external links open in the browser |
| `icon` | yes | | Path to a PNG icon (resized to all mipmap densities) |
| `theme_color` | no | `#0a0a0a` | Status bar / theme color |
| `refresh_timeout_sec` | no | `10` | Seconds the app must be backgrounded before triggering a smart refresh on resume (see below) |

## Project Structure

- `src/webview_apk.py` - CLI entry point; reads YAML config, renders Jinja2 templates, generates icons, runs Gradle build
- `app/src/main/kotlin/app/webviewapk/MainActivity.kt` - The Android activity (not templated, shared by all builds)
- `templates/` - Jinja2 templates for `build.gradle.kts`, `settings.gradle.kts`, `strings.xml`, `themes.xml`
- `examples/` - Example YAML configs

## How It Works

1. User provides a YAML config with app name, URL, icon, etc.
2. `webview_apk.py` renders templates with the config values, generates mipmap icons, then runs `gradlew assembleDebug`
3. `BuildConfig` fields (APP_URL, APP_HOST, REFRESH_TIMEOUT_SEC) are injected via the Gradle template and read at runtime in `MainActivity.kt`

## Smart Refresh

`MainActivity` tracks `lastPauseTime` in `onPause()`. On `onResume()`, if the elapsed time exceeds `BuildConfig.REFRESH_TIMEOUT_SEC`, it calls `window.__webviewRefresh()` via `evaluateJavascript()`. The web page opts in by defining this function. Default timeout is 10 seconds.

To opt in, define the function in your web app:

```javascript
window.__webviewRefresh = () => {
  // Re-fetch data, update DOM, etc.
};
```

If the function is not defined, nothing happens.

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
| `refresh_timeout_ms` | no | `300000` | Milliseconds the app must be backgrounded before triggering a smart refresh on resume (see below) |

## Smart Refresh

When the user returns to the app after it has been in the background longer than `refresh_timeout_ms`, the WebView calls:

```javascript
if (typeof window.__webviewRefresh === 'function') window.__webviewRefresh()
```

This lets the web page re-fetch data and update the UI without a full page reload. To opt in, define the function in your web app:

```javascript
window.__webviewRefresh = () => {
  // Re-fetch data, update DOM, etc.
};
```

If the function is not defined, nothing happens.

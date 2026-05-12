# RustDesk 局域网定制化修改提示词

将此提示词提供给大模型(如 Claude、DeepSeek、GPT-4 等)，配合 RustDesk v1.4.x 源码仓库，可复现全部定制化修改。

---

## 背景

我需要将 RustDesk 改造为仅限局域网使用的屏幕保护/远程控制工具。需要完成以下四项工作:

1. **禁用全部外网访问**: 禁用自动更新、将所有外网 URL 的 host 替换为 127.0.0.1、默认配置中继服务器指向 127.0.0.1
2. **Floating Toolbar 默认隐藏**: 远程连接时的浮动工具栏默认隐藏，按 Ctrl+Alt+O 切换显示
3. **默认设置修改**: 允许 IP 直接访问、开启 UDP 打洞、监听端口 22228、仅密码访问、禁用摄像头；同时将命名从 RustDesk 改为 RustWallpaper 以隐藏远程桌面特征
4. **Connection Manager 窗口默认隐藏**: 被控端被连接时弹出窗口默认隐藏为托盘图标，按 Ctrl+Alt+P 切换显示

---

## 详细修改清单

### 一、命名改换：RustDesk → RustWallpaper (隐藏远程桌面特征)

目的是将"RustDesk Remote Desktop"这些明显是远程桌面的字样统一改成 RustWallpaper Screen Saver。

#### 1.1 Rust 源码层

**`Cargo.toml`** (根目录):
```diff
-description = "RustDesk Remote Desktop"
-default-run = "rustdesk"
+description = "RustWallpaper Screen Saver"
+default-run = "RustWallpaper"

+[[bin]]
+name = "RustWallpaper"
+path = "src/main.rs"

-[package.metadata.winres]
-ProductName = "RustDesk"
-FileDescription = "RustDesk Remote Desktop"
-OriginalFilename = "rustdesk.exe"
+[package.metadata.winres]
+ProductName = "RustWallpaper"
+FileDescription = "RustWallpaper Screen Saver"
+OriginalFilename = "RustWallpaper.exe"
```

**`src/main.rs`**:
```diff
-App::new("rustdesk")
-.about("RustDesk command line tool")
+App::new("RustWallpaper")
+.about("RustWallpaper command line tool")
```

**`src/auth_2fa.rs`**:
```diff
-const ISSUER: &str = "RustDesk";
+const ISSUER: &str = "RustWallpaper";
```

**`src/common.rs`**:
```diff
-// is_rustdesk() 返回 hbb_common::config::APP_NAME.read().unwrap().eq("RustDesk")
+// is_rustdesk() 返回 hbb_common::config::APP_NAME.read().unwrap().eq("RustWallpaper")

-// is_custom_client() 返回 get_app_name() != "RustDesk"
+// is_custom_client() 返回 get_app_name() != "RustWallpaper"
```

**`src/flutter_ffi.rs`** (Update download filenames):
```diff
-format!("rustdesk-{version}-x86_64.msi")
-format!("rustdesk-{version}-x86_64.exe")
-format!("rustdesk-{version}-x86_64.dmg")
-format!("rustdesk-{version}-aarch64.dmg")
+format!("RustWallpaper-{version}-x86_64.msi")
+format!("RustWallpaper-{version}-x86_64.exe")
+format!("RustWallpaper-{version}-x86_64.dmg")
+format!("RustWallpaper-{version}-aarch64.dmg")
```

**`libs/hbb_common/src/config.rs`**:
```diff
-pub static ref APP_NAME: RwLock<String> = RwLock::new("RustDesk".to_owned());
+pub static ref APP_NAME: RwLock<String> = RwLock::new("RustWallpaper".to_owned());
```

#### 1.2 Flutter Windows 构建层

**`flutter/windows/CMakeLists.txt`**:
```diff
-set(BINARY_NAME "rustdesk")
+set(BINARY_NAME "RustWallpaper")
```

**`flutter/windows/runner/Runner.rc`**: 修改 Version Info 区块中的 FileDescription、InternalName、OriginalFilename、ProductName，全部把 RustDesk 改为 RustWallpaper，FileDescription 改为 "RustWallpaper Screen Saver"。

**`flutter/linux/CMakeLists.txt`**:
```diff
-set(BINARY_NAME "rustdesk")
+set(BINARY_NAME "RustWallpaper")
```

#### 1.3 打包/安装脚本

**`libs/portable/Cargo.toml`**: description、ProductName、OriginalFilename、FileDescription 全部改为 RustWallpaper。

**`libs/portable/generate.py`**: 将默认 executable 和注释中的 `rustdesk.exe` 改为 `RustWallpaper.exe`。

**`build.py`**: 将所有二进制名引用 (`rustdesk.exe`, `rustdesk`, `RustWallpaper.exe` 等) 统一为 `RustWallpaper.exe`。需要 grep 处理以下路径位置:
- `rm tmpdeb/usr/bin/rustdesk` → `rm tmpdeb/usr/bin/RustWallpaper`
- `-e ../../{path}/RustWallpaper.exe`
- Sciter DEB 构建路径下的 strip/mv 命令

**`.github/workflows/flutter-build.yml`**: CI 中便携打包器的 exe 引用改为 `RustWallpaper.exe`。

**`res/rustdesk.desktop`**:
```diff
-Name=RustDesk
-GenericName=Remote Desktop
-Comment=Remote Desktop
-Exec=rustdesk %u
+Name=RustWallpaper
+GenericName=Screen Saver
+Comment=Screen Saver
+Exec=RustWallpaper %u
```

**`res/rustdesk-link.desktop`**: Name、MimeType handler、TryExec、Exec 全部改。

**`res/rustdesk.service`**: Description、ExecStart、ExecStop 全部改。

**`res/DEBIAN/postinst`**: 软链接路径 `rustdesk` → `RustWallpaper`。

**`res/PKGBUILD`**: 软链接路径 `rustdesk` → `RustWallpaper`。

**`res/rpm.spec`** 和 **`res/rpm-suse.spec`**: install 路径和 %files 列表中的二进制名全部改。

#### 1.4 语言文件 (仅中文)

**`src/lang/cn.rs`**: 
- "控制远程桌面" → "控制屏幕保护"
- "远程桌面" → "屏幕保护"
- 其他明显提及远程桌面的中文描述更换为屏幕保护相关

**`src/lang.rs`**: 翻译替换逻辑增加条件 `crate::get_app_name() != "RustDesk"`，确保即使 is_rustdesk() 改了也能正确替换文本中的 RustDesk 为 RustWallpaper。

---

### 二、禁用外网访问

#### 2.1 禁用自动更新

**`src/rendezvous_mediator.rs`**: 注释掉自动更新启动:
```diff
-        #[cfg(target_os = "windows")]
-        if crate::platform::is_installed() && crate::is_server() {
-            crate::updater::start_auto_update();
-        }
+        // Auto-update disabled for LAN-only build
```

**`src/updater.rs`**: 禁用更新检查线程:
```diff
 fn start_auto_update_check() -> Sender<UpdateMsg> {
-    let (tx, rx) = channel();
-    std::thread::spawn(move || start_auto_update_check_(rx));
+    let (tx, rx) = channel::<UpdateMsg>();
+    // Auto-update is disabled in LAN-only build
+    drop(rx);
     return tx;
 }
```

#### 2.2 替换所有外网 URL host 为 127.0.0.1

所有资源文件中的 `rustdesk.com`、`api.rustdesk.com`、`admin.rustdesk.com`、`github.com/rustdesk` 等 host 全部替换为 `127.0.0.1`:

- **`src/client.rs`**: `SCRAP_X11_REF_URL`、`LOGIN_MSG_...link` 中的 URL
- **`src/common.rs`**: `get_api_server_()` 回退默认值
- **`src/lang/en.rs`**: 帮助文档链接 (`doc_mac_permission`, `doc_fix_wayland`)
- **`libs/hbb_common/src/config.rs`**: `LINK_DOCS_HOME`, `LINK_DOCS_X11_REQUIRED`, `LINK_HEADLESS_LINUX_SUPPORT`
- **`libs/hbb_common/src/lib.rs`**: `version_check_request()` 中的 `URL`
- **Flutter 所有页面**: `connection_page.dart`, `desktop_home_page.dart`, `desktop_setting_page.dart`, `install_page.dart`, `settings_page.dart` 等中的链接

注意：路径保留原样，只改 host 部分。例如:
- `https://rustdesk.com/download` → `https://127.0.0.1/download`
- `https://rustdesk.com/privacy.html` → `https://127.0.0.1/privacy.html`
- `https://api.rustdesk.com/version/latest` → `https://127.0.0.1/version/latest`
- `https://admin.rustdesk.com` → `https://127.0.0.1`

#### 2.3 默认配置中继服务器指向本地

**`src/common.rs`** 新增 `set_lan_defaults()` 函数并在 `global_init()` 中调用:

```rust
fn set_lan_defaults() {
    use hbb_common::config::{self, keys};
    let mut defaults = config::DEFAULT_SETTINGS.write().unwrap();
    if defaults.is_empty() {
        defaults.insert(keys::OPTION_CUSTOM_RENDEZVOUS_SERVER.to_string(), "127.0.0.1".to_string());
        defaults.insert(keys::OPTION_RELAY_SERVER.to_string(), "127.0.0.1".to_string());
        defaults.insert(keys::OPTION_API_SERVER.to_string(), "https://127.0.0.1".to_string());
        defaults.insert(keys::OPTION_DIRECT_SERVER.to_string(), "Y".to_string());
        defaults.insert(keys::OPTION_DIRECT_ACCESS_PORT.to_string(), "22228".to_string());
        defaults.insert(keys::OPTION_VERIFICATION_METHOD.to_string(), "use-permanent-password".to_string());
        defaults.insert(keys::OPTION_ENABLE_CAMERA.to_string(), "N".to_string());
        defaults.insert(keys::OPTION_APPROVE_MODE.to_string(), "password".to_string());
        defaults.insert(keys::OPTION_ALLOW_AUTO_UPDATE.to_string(), "N".to_string());
        defaults.insert("allow-hide-cm".to_string(), "Y".to_string());
    }
    let mut local_defaults = config::DEFAULT_LOCAL_SETTINGS.write().unwrap();
    if local_defaults.is_empty() {
        local_defaults.insert(keys::OPTION_ENABLE_CHECK_UPDATE.to_string(), "N".to_string());
        local_defaults.insert(keys::OPTION_ENABLE_UDP_PUNCH.to_string(), "Y".to_string());
    }
}
```

---

### 三、Floating Toolbar 默认隐藏 (Ctrl+Alt+O)

**`flutter/lib/desktop/widgets/remote_toolbar.dart`**:

1. `ToolbarState` 类中 `hide` 初始化改为 `true`:
```diff
-  RxBool hide = false.obs;
+  RxBool hide = true.obs;
```

2. 初始化加载时默认值也是 `true`:
```diff
-      hide.value = results[1] ?? false;
+      hide.value = results[1] ?? true;
```

3. 添加键盘事件处理——在 `_RemoteToolbarState.initState()` 中注册、`dispose()` 中移除:
```dart
initState() {
    super.initState();
+    HardwareKeyboard.instance.addHandler(_handleKeyEvent);
    ...
}

+bool _handleKeyEvent(KeyEvent event) {
+    if (event is KeyDownEvent &&
+        HardwareKeyboard.instance.isControlPressed &&
+        HardwareKeyboard.instance.isAltPressed &&
+        event.logicalKey == LogicalKeyboardKey.keyO) {
+      widget.state.switchHide(widget.ffi.sessionId);
+      return true;
+    }
+    return false;
+}

dispose() {
+    HardwareKeyboard.instance.removeHandler(_handleKeyEvent);
    super.dispose();
    ...
}
```

4. `_debouncerHideProc` 函数的位置保持不变（移到 dispose 之后即可），确保括号层级正确。

---

### 四、Connection Manager 窗口默认隐藏 (Ctrl+Alt+P)

#### 4.1 默认隐藏

**`flutter/lib/models/server_model.dart`**:
```diff
-  bool hideCm = false;
+  bool hideCm = true;
```

#### 4.2 无客户端时的关闭逻辑修正

`server_model.dart` 中 `_clients.isEmpty` 和 `_clients.isNotEmpty` 时正确处理 `hideCm`:

```dart
if (_clients.isEmpty) {
-    hideCmWindow();
+    if (!hideCm) {
+      hideCm = true;
+      hideCmWindow();
+    }
} else {
    if (!hideCm) showCmWindow();
}
```

#### 4.3 Ctrl+Alt+P 切换显示

**`flutter/lib/desktop/pages/desktop_home_page.dart`**: 添加键盘事件处理

```dart
initState() {
    super.initState();
+    HardwareKeyboard.instance.addHandler(_handleCmKeyEvent);
    ...
}

+bool _handleCmKeyEvent(KeyEvent event) {
+    if (event is KeyDownEvent &&
+        HardwareKeyboard.instance.isControlPressed &&
+        HardwareKeyboard.instance.isAltPressed &&
+        event.logicalKey == LogicalKeyboardKey.keyP) {
+      bind.cmSetConfig(name: "show-cm", value: "1");
+      return true;
+    }
+    return false;
+}

dispose() {
+    HardwareKeyboard.instance.removeHandler(_handleCmKeyEvent);
    ...
}
```

#### 4.4 服务端模型中的 toggle 逻辑

**`flutter/lib/models/server_model.dart`** 的轮询循环中添加:

```dart
final showCmFlag = await bind.cmGetConfig(name: "show-cm");
if (showCmFlag == "1") {
    bind.cmSetConfig(name: "show-cm", value: "0");
    hideCm = !hideCm;
    if (hideCm) {
        hideCmWindow();
    } else {
        showCmWindow();
    }
}
```

#### 4.5 聊天框不自动弹出

**`flutter/lib/models/chat_model.dart`**:
```diff
-    if (desktopType == DesktopType.cm) {
+    if (desktopType == DesktopType.cm && !gFFI.serverModel.hideCm) {
```

#### 4.6 启动时的窗口配置 (解决任务栏图标残留)

**`flutter/lib/main.dart`**: 核心改动——必须在 `_runApp()` 之前检查 `hide_cm` 配置并使用 `skipTaskbar: true`，否则 Windows 会在窗口创建时注册任务栏图标，后续再怎么隐藏都无法移除该图标。

1. `getHiddenTitleBarWindowOptions()` 新增 `skipTaskbar` 参数:
```diff
 WindowOptions getHiddenTitleBarWindowOptions(
     {bool isMainWindow = false,
     Size? size,
     bool center = false,
-    bool? alwaysOnTop}) {
+    bool? alwaysOnTop,
+    bool skipTaskbar = false}) {
   ...
   return WindowOptions(
     ...
-    skipTaskbar: false,
+    skipTaskbar: skipTaskbar,
     ...
   );
```

2. `runConnectionManagerScreen()` 重构——先读配置，再用 `waitUntilReadyToShow` 设置 `skipTaskbar: true`，最后才 `_runApp()`:
```dart
void runConnectionManagerScreen() async {
  await initEnv(kAppTypeConnectionManager);
  // 必须在 _runApp() 之前检查并配置窗口
  final hideVal = await bind.cmGetConfig(name: "hide_cm");
  final hide = hideVal.isEmpty ? gFFI.serverModel.hideCm : hideVal == 'true';
  gFFI.serverModel.hideCm = hide;
  if (hide) {
    WindowOptions windowOptions = getHiddenTitleBarWindowOptions(
        size: kConnectionManagerWindowSizeClosedChat, skipTaskbar: true);
    windowManager.setOpacity(0);
    await windowManager.waitUntilReadyToShow(windowOptions, null);
  }
  _runApp('', const DesktopServerPage(), MyTheme.currentThemeMode());
  if (hide) {
    bind.mainHideDock();
    await windowManager.minimize();
    await windowManager.hide();
    _isCmReadyToShow = true;
  } else {
    await showCmWindow(isStartup: true);
  }
  ...
}
```

3. `showCmWindow()` 和 `hideCmWindow()` 的 `isStartup` 分支也要传 `skipTaskbar: true`:
```diff
 showCmWindow({bool isStartup = false}) async {
   if (isStartup) {
     WindowOptions windowOptions = getHiddenTitleBarWindowOptions(
-        size: kConnectionManagerWindowSizeClosedChat, alwaysOnTop: true);
+        size: kConnectionManagerWindowSizeClosedChat,
+        alwaysOnTop: true,
+        skipTaskbar: true);
     ...

 hideCmWindow({bool isStartup = false}) async {
   if (isStartup) {
     WindowOptions windowOptions = getHiddenTitleBarWindowOptions(
-        size: kConnectionManagerWindowSizeClosedChat);
+        size: kConnectionManagerWindowSizeClosedChat, skipTaskbar: true);
     ...
```

**原理解释**: 在 Windows 上，`skipTaskbar` 对应 `WS_EX_TOOLWINDOW` 扩展窗口样式。此样式必须在窗口创建时设置（`waitUntilReadyToShow` 会将其传递给原生窗口）。如果先 `runApp()` 创建窗口默认出现在任务栏，再设置 `skipTaskbar: true` 已经来不及了，缩略图/图标会残留在任务栏。

#### 4.7 添加 cm_set_config FFI 接口

**`src/flutter_ffi.rs`** 新增:
```rust
pub fn cm_set_config(name: String, value: String) {
    #[cfg(not(target_os = "ios"))]
    {
        let _ = crate::ipc::set_config(&name, value);
    }
    #[cfg(target_os = "ios")]
    {
        let _ = name;
        let _ = value;
    }
}
```

---

### 五、关于 RS_PUB_KEY 公钥的说明

`libs/hbb_common/src/config.rs` 中的 `RS_PUB_KEY` 用于客户端与中继服务器之间的 NaCl 加密握手。如果修改了此公钥，又需要连接自建 relay 服务器，需在连接时使用 `id@server?key=服务器公钥` 格式，或在设置面板手动填写服务器的 key。仅纯 IP 直连则不受影响。

---

### 六、已知编译错误与修复 (Common Pitfalls)

以下是在实际修改过程中遇到的编译错误，后续修改时务必注意避免：

#### 6.1 Rust `#[cfg]` 块语法错误

**`src/flutter_ffi.rs`** 中 `cm_set_config` 函数，`#[cfg(target_os = "ios")]` 块必须用 `{}` 包裹:

❌ **错误写法:**
```rust
pub fn cm_set_config(name: String, value: String) {
    #[cfg(not(target_os = "ios"))]
    {
        let _ = crate::ipc::set_config(&name, value);
    }
    #[cfg(target_os = "ios")]
    let _ = name;      // 裸 let 语句在 cfg 属性后缺少块，编译失败！
    let _ = value;
}
```

✅ **正确写法:**
```rust
pub fn cm_set_config(name: String, value: String) {
    #[cfg(not(target_os = "ios"))]
    {
        let _ = crate::ipc::set_config(&name, value);
    }
    #[cfg(target_os = "ios")]
    {
        let _ = name;
        let _ = value;
    }
}
```

#### 6.2 DEFAULT_SETTINGS 与 DEFAULT_LOCAL_SETTINGS 分离

`set_lan_defaults()` 中必须区分两类配置。有些选项属于本地配置(`DEFAULT_LOCAL_SETTINGS`)，有些属于全局配置(`DEFAULT_SETTINGS`)。如果全部塞进一个 Map，某些选项不会生效:

- **`DEFAULT_SETTINGS`** (全局，写入 `Config`): 中继服务器、API 服务器、直连开关、端口、验证方式、摄像头、批准模式、自动更新允许
- **`DEFAULT_LOCAL_SETTINGS`** (本地，写入 `LocalConfig`): 检查更新开关、UDP 打洞开关

✅ **正确写法:**
```rust
fn set_lan_defaults() {
    use hbb_common::config::{self, keys};
    let mut defaults = config::DEFAULT_SETTINGS.write().unwrap();
    if defaults.is_empty() {
        defaults.insert(keys::OPTION_CUSTOM_RENDEZVOUS_SERVER.to_string(), "127.0.0.1".to_string());
        defaults.insert(keys::OPTION_RELAY_SERVER.to_string(), "127.0.0.1".to_string());
        defaults.insert(keys::OPTION_API_SERVER.to_string(), "https://127.0.0.1".to_string());
        defaults.insert(keys::OPTION_DIRECT_SERVER.to_string(), "Y".to_string());
        defaults.insert(keys::OPTION_DIRECT_ACCESS_PORT.to_string(), "22228".to_string());
        defaults.insert(keys::OPTION_VERIFICATION_METHOD.to_string(), "use-permanent-password".to_string());
        defaults.insert(keys::OPTION_ENABLE_CAMERA.to_string(), "N".to_string());
        defaults.insert(keys::OPTION_APPROVE_MODE.to_string(), "password".to_string());
        defaults.insert(keys::OPTION_ALLOW_AUTO_UPDATE.to_string(), "N".to_string());
        defaults.insert("allow-hide-cm".to_string(), "Y".to_string());
    }
    let mut local_defaults = config::DEFAULT_LOCAL_SETTINGS.write().unwrap();
    if local_defaults.is_empty() {
        local_defaults.insert(keys::OPTION_ENABLE_CHECK_UPDATE.to_string(), "N".to_string());
        local_defaults.insert(keys::OPTION_ENABLE_UDP_PUNCH.to_string(), "Y".to_string());
    }
}
```

❌ **错误写法:** 全部塞进 `DEFAULT_SETTINGS`（然后第一行 `if !defaults.is_empty() { return; }`），导致 `OPTION_ENABLE_CHECK_UPDATE` 和 `OPTION_ENABLE_UDP_PUNCH` 不生效。

#### 6.3 remote_toolbar.dart 重复 dispose 和孤儿括号

在 `remote_toolbar.dart` 中添加键盘事件处理器后，如果不同时清理原有的旧代码结构，会产生:
- **重复的 `dispose()` 方法** → Dart 编译错误
- **孤儿闭合括号** (`    });` `  }`) → Freezed 代码生成失败

修改 `remote_toolbar.dart` 时需要确保:
1. 只有一个 `dispose()` 方法（合并两个的功能）
2. `_debouncerHideProc` 函数移到 `dispose()` 之后、`build()` 之前
3. 删除所有多余的闭合括号

#### 6.4 CM 窗口 show-cm 检查必须放在客户端数量检查之后

`server_model.dart` 中 Ctrl+Alt+P 的 `show-cm` 配置检查（IPC 读取）**必须放在 `cmCheckClientsLength` 检查之后**，否则在高速轮询场景下会与客户端状态更新产生竞态，导致 CM 窗口隐藏/显示逻辑错乱。

#### 6.5 命名统一性的陷阱

改名时要确保**所有文件**的一致性:
- Rust source (`main.rs`, `common.rs`, `auth_2fa.rs`, `flutter_ffi.rs`)
- Flutter build (`windows/CMakeLists.txt`, `linux/CMakeLists.txt`, `windows/runner/Runner.rc`)
- 打包脚本 (`build.py`, `libs/portable/Cargo.toml`, `libs/portable/generate.py`)
- Linux 系统文件 (`res/rustdesk.desktop`, `res/rustdesk-link.desktop`, `res/rustdesk.service`)
- 包管理文件 (`res/DEBIAN/postinst`, `res/PKGBUILD`, `res/rpm.spec`, `res/rpm-suse.spec`)
- CI/CD (`.github/workflows/flutter-build.yml`)
- `libs/hbb_common` 子模块 (`src/config.rs`, `src/lib.rs`)

如果漏改任一文件，会导致:
- 安装器创建的快捷方式指向不存在的 exe
- `dpkg -i` 安装后软链接断裂
- systemd 服务启动失败

#### 6.6 `set_lan_defaults()` 只执行一次

由于 `DEFAULT_SETTINGS` / `DEFAULT_LOCAL_SETTINGS` 是进程内全局静态 Map，`set_lan_defaults()` 中 `if defaults.is_empty()` 的检查确保只在首次调用时写入默认值。后续调用（如 `global_init()` 被多次调用时）不会重复写入，避免覆盖用户后续自己的设置。

如果改成 `if !defaults.is_empty() { return; }` 在开头直接 return，然后后续无条件 insert，会导致:
- 每次调用都重复写入默认值
- 用户手动修改的设置可能在下一次 `global_init()` 时被覆盖

#### 6.7 Windows 任务栏幽灵图标 (skipTaskbar 设置时机)

**现象**: CM 窗口虽然被 `hideCmWindow()` 隐藏（opacity=0 + minimize + hide），但 Windows 任务栏仍然残留一个图标，鼠标悬停可看到窗口缩略图，点击无反应。

**根因**: `runConnectionManagerScreen()` 先执行 `_runApp()` 创建窗口（默认 `skipTaskbar: false`），再执行 `hideCmWindow()` 去隐藏窗口。但在 Windows 上，窗口创建的瞬间就注册了任务栏图标，后续 `hide()` 无法移除。

**修复**: 必须在 `_runApp()` 之前，通过 `windowManager.waitUntilReadyToShow()` 配置 `skipTaskbar: true`。该属性对应 Windows 的 `WS_EX_TOOLWINDOW` 扩展样式，必须在窗口创建时设置。

详见第四章 4.6 节的完整代码。

---

## 使用方式

将此文件内容粘贴给大模型，说:
```
请按照这个文档中的所有修改，对当前的 RustDesk 源码进行修改。
```

注意：本提示词基于 RustDesk v1.4.6 版本编写，如果基于更新的版本，部分代码行号和上下文可能有所变化，届时需要大模型自行适配。

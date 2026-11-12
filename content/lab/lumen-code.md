+++

title = "Lumen Code"
date = 2026-11-12

+++

简单描述一下这个项目

**不联网，也能传文件。** 两台设备之间没有共同的网络、也插不了 USB 时，靠一块屏幕和一个摄像头把文件传过去：一台设备在屏幕上播放，另一台用摄像头接收。

官网：https://lumencode.link/

## 能做什么

- 传文档、照片、配置文件等，也可以直接发一段文字。
- iPhone、Android 和电脑之间都能互传。
- 用你手头已有的两台设备就能试。

## 怎么用

- **网页版**：任何带摄像头的浏览器都能用，发送打开 [lumencode.link/send](https://lumencode.link/send)，接收打开 [lumencode.link/recv](https://lumencode.link/recv)。
- **桌面版**（v1.0.1）：macOS 12+、Windows 10/11、Linux（x86_64 / ARM64），从 GitHub Releases 下载。
- **手机 App**：iPhone（iOS 17+）和 Android（Android 10+）即将上架。接收速度比网页版快，安装后可以完全离线使用。

## 速度

实测（设备和拍摄条件不同，结果会有差异）：

| 方向 | 速度 |
|---|---|
| 电脑 → iPhone App | 约 0.5 MB/s |
| Android App → iPhone App | 约 100 KB/s |

性能好的设备可以调高播放帧率来提速。

## 价格与开源

- 网页版、桌面版免费；自己用 Android Studio 或 Xcode 编译手机 App 永久免费，和商店里的是同一个应用。
- Google Play / App Store 版本一次买断 US$2.99（即将上架，以商店页面为准），无订阅，两个平台分开购买，收入用于持续维护。
- 源码 MIT 协议开源：[github.com/mondaylabsltd/lumen-code](https://github.com/mondaylabsltd/lumen-code)。

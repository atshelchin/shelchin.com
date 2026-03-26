+++
title="一个 JS 老兵的多语言生存指南"
date="2026-03-26"
+++



写了十年 JavaScript。jQuery、React、Node.js、Bun 都用过，前端后端都写过，觉得 JS 够用了。

直到需求开始逼你了：要做个桌面应用，Electron 太重；想写 Solana 合约，JS 不行；要出 iOS 和 Android 版本；后端的交易机器人要跑一万个策略实例，Bun 撑不住。

一下子要同时面对 Go、Rust、Swift、Kotlin 四门语言。

好在现在有 AI 写代码。我不需要四门语言都精通，我需要的是读得懂、能判断 AI 写的东西对不对、出了问题知道往哪里查。这篇文章就是干这个的。

## 它们各自干什么

先搞清楚每门语言在我的场景里负责什么，别混了：

**Go** — 交易机器人后端。一万个策略跑在一个进程里，goroutine 天然适合。

**Rust** — 两个场景。Tauri 做跨平台桌面应用（替代 Electron，打包只有几 MB）。Solana 合约开发（链上程序必须用 Rust）。

**Swift** — iOS 应用。SwiftUI 写界面。

**Kotlin** — Android 应用。Jetpack Compose 写界面。

场景不同，互不干扰。

## 先全部跑起来

学一门新语言，第一件事是把 hello world 跑通。不是为了学语法，是为了确认环境没问题。

### Go

```bash
mkdir my-go && cd my-go
go mod init my-go
```

```go
// main.go
package main
import "fmt"
func main() {
    fmt.Println("hello from go")
}
```

```bash
go run main.go
```

### Rust

```bash
cargo new my-rust
cd my-rust
```

```rust
// src/main.rs（cargo 自动生成好了）
fn main() {
    println!("hello from rust");
}
```

```bash
cargo run
```

### Swift

```bash
mkdir my-swift && cd my-swift
```

```swift
// main.swift
print("hello from swift")
```

```bash
swift main.swift
```

### Kotlin

```bash
# 装好 Kotlin 编译器后
mkdir my-kotlin && cd my-kotlin
```

```kotlin
// Main.kt
fun main() {
    println("hello from kotlin")
}
```

```bash
kotlinc Main.kt -include-runtime -d app.jar && java -jar app.jar
```

Kotlin 那个命令最长。实际开发中你不会手动编译，Android Studio 或 Gradle 会管这些。

四个环境跑通了，后面的事情交给 AI 之前，先确认这一步没问题。

## 变量

JS 里 `let` 和 `const` 搞定一切。其他语言也差不多，只是关键字不一样：

```
JS:      let x = 1      const x = 1
Go:      x := 1         const x = 1（只能编译期常量）
Rust:    let mut x = 1   let x = 1（默认不可变）
Swift:   var x = 1       let x = 1
Kotlin:  var x = 1       val x = 1
```

注意 Rust 的变量默认不可变。`let x = 1` 之后写 `x = 2` 会编译报错，必须 `let mut x = 1`。这个和其他所有语言都反过来。

Go 和 Rust 的 `const` 只能是编译期就确定的值，`const t = time.Now()` 会报错。Rust 的 `let` 虽然不可变但是运行时赋值，和 Go 的 `const` 不是一回事。Swift 的 `let` 和 Kotlin 的 `val` 没有编译期限制。

四门语言都有类型推导，大部分情况不用手动写类型。

给 AI 的提示词可以加一句："变量默认用不可变，只在需要修改的时候用 mut/var"。Rust 和 Swift 社区都推荐这个风格。

## null 的问题

JS 里有 `null` 和 `undefined`，经常半夜被 `Cannot read property of undefined` 叫醒。四门语言各有各的解法：

**Go** 没管这个问题。Go 里 null 叫 `nil`，指针和 interface 都可能是 nil，用之前你自己判断。

**Rust** 最严格——没有 null 这个概念。要表达"有或没有"，用 `Option<T>`：

```rust
let name: Option<String> = Some("shelchin".to_string());
let empty: Option<String> = None;

// 必须显式处理两种情况
match name {
    Some(n) => println!("{}", n),
    None => println!("no name"),
}
```

编译器逼你处理 `None` 的情况，不处理不让过。

**Swift** 用 `Optional`，语法比 Rust 甜一些：

```swift
var name: String? = "shelchin"  // ? 表示可以是 nil
print(name?.count ?? 0)         // 如果 nil 就用默认值
```

**Kotlin** 和 Swift 很像：

```kotlin
var name: String? = "shelchin"
println(name?.length ?: 0)
```

Swift 和 Kotlin 几乎一样的语法，都用 `?` 和 `?:`。记住一个就记住两个了。

AI 写 Swift 和 Kotlin 的时候经常乱用 `!`（强制解包），看到 `!` 就要警觉——如果值是 nil，程序会崩。

## 错误处理

JS 的 try/catch 是运行时的事情，忘了 catch 程序就崩了。四门语言的处理方式差别很大。

**Go**——错误是返回值，没有异常：

```go
resp, err := http.Get(url)
if err != nil {
    return err
}
defer resp.Body.Close()
```

**Rust**——错误也是返回值，但编译器管着你：

```rust
let resp = reqwest::get(url).await?;  // ? 自动传播错误
```

`?` 是 Rust 的语法糖。如果出错，函数直接返回这个错误。不用写 `if err != nil`，但函数签名必须声明返回 `Result<T, E>`。

**Swift**——有 try/catch，但必须标记哪些函数会抛错：

```swift
do {
    let data = try fetchData(url)
} catch {
    print(error)
}
```

函数要用 `throws` 标记，调用时要写 `try`，编译器会检查你有没有处理。比 JS 的 try/catch 严格。

**Kotlin**——和 JS 一样 try/catch，但协程里用 `runCatching`：

```kotlin
val result = runCatching { fetchData(url) }
result.onSuccess { data -> println(data) }
result.onFailure { e -> println(e) }
```

Go 和 Rust 不用异常，错误是普通的返回值。Swift 和 Kotlin 有异常但比 JS 严格。

让 AI 写 Go 的时候盯着 `if err != nil`，写 Rust 的时候盯着 `?` 和 `unwrap()`。`unwrap()` 遇到错误会直接 panic，在 Solana 合约里这个会导致交易失败，要用 `?` 替代。

## 面向对象

JS 有 class。Go 和 Rust 没有 class，Swift 和 Kotlin 有但风格不同。

**Go**——struct + 方法，没有继承：

```go
type User struct {
    Name string
    Age  int
}

func (u *User) IsAdult() bool {
    return u.Age >= 18
}
```

**Rust**——struct + impl，没有继承：

```rust
struct User {
    name: String,
    age: u32,
}

impl User {
    fn is_adult(&self) -> bool {
        self.age >= 18
    }
}
```

**Swift**——有 class 但更推荐 struct：

```swift
struct User {
    let name: String
    let age: Int

    func isAdult() -> Bool {
        return age >= 18
    }
}
```

**Kotlin**——有 class，和 JS/TypeScript 最像：

```kotlin
data class User(val name: String, val age: Int) {
    fun isAdult(): Boolean = age >= 18
}
```

Kotlin 的 `data class` 自动生成 equals、hashCode、toString、copy，相当于 TypeScript 里你手动写的那堆样板代码。

四门语言的接口/协议/trait：

```
Go:      interface（隐式实现，不用写 implements）
Rust:    trait（显式 impl Trait for Struct）
Swift:   protocol（和 Rust 的 trait 很像）
Kotlin:  interface（和 TypeScript 几乎一样）
```

让 AI 写代码时可以说："优先用组合而不是继承"。Go 和 Rust 根本没有继承，Swift 和 Kotlin 虽然有但社区也不推荐用。

## 并发

JS 是单线程 + 事件循环。四门语言各有各的并发模型。

**Go** 用 goroutine，用 `go` 关键字启动，语法最简单：

```go
go func() {
    // 并发执行
}()
```

goroutine 初始栈只有 2KB，一万个才 20MB，而且自动利用所有 CPU 核。

**Rust** 用 `tokio`（第三方库，但几乎是标准）：

```rust
tokio::spawn(async {
    // 并发执行
});
```

写法和 JS 的 async/await 很像，但 Rust 的 async 有生命周期和 Send/Sync 约束，AI 经常在这里编译不过。提示词里加一句"用 `tokio::spawn` 的时候确保闭包里的变量都是 `Send + 'static`"能减少一些麻烦。

**Swift** 有原生 async/await，写法和 JS 很像：

```swift
Task {
    let data = await fetchData()
}
```

**Kotlin** 的协程：

```kotlin
launch {
    val data = fetchData()  // 挂起函数，自动 await
}
```

Kotlin 的协程写起来和同步代码一样，不需要写 `await`。挂起函数（`suspend fun`）在调用的时候自动挂起，这个是 Kotlin 独有的设计。

Swift 和 Kotlin 的 async/await 和 JS 很像，几乎不用适应。Go 的 goroutine + channel 是另一套思路。Rust 的 async 语法像 JS，但底下的规则多得多。

## 内存管理

这块差别最大。

**Go 和 Kotlin**——有垃圾回收（GC），和 JS 一样不用管。

**Swift**——ARC（自动引用计数）。每个对象有一个计数器，有人引用就 +1，没人引用就释放。大部分时候不用管，但两个对象互相引用会内存泄漏。Swift 用 `weak` 打破循环引用：

```swift
class Parent {
    var child: Child?
}

class Child {
    weak var parent: Parent?  // weak 不增加引用计数
}
```

AI 写 Swift 的时候看看闭包里有没有 `[weak self]`。如果闭包捕获了 self 又被 self 持有，没有 weak 就会泄漏。

**Rust**——没有 GC，没有引用计数（默认）。靠所有权系统管内存。这是 Rust 最难的部分，也是绕不过去的。

```rust
let s1 = String::from("hello");
let s2 = s1;     // s1 的所有权移动到了 s2
// println!("{}", s1);  // 编译错误！s1 已经失效了
```

一个值在同一时间只能有一个"主人"（owner）。赋值给别人，自己就不能用了。这叫移动语义。

想共享数据，用引用（借用）：

```rust
let s1 = String::from("hello");
let s2 = &s1;    // 借用，s1 还能用
println!("{} {}", s1, s2);  // OK
```

但可变引用同一时间只能有一个：

```rust
let mut s = String::from("hello");
let r1 = &mut s;
// let r2 = &mut s;  // 编译错误！已经有一个可变引用了
```

这些规则在编译期就检查完了。运行时不需要 GC，性能接近 C。代价是编译器会拒绝很多在其他语言里合法的写法，你需要和它"谈判"。

写 Solana 合约的时候会碰到大量的 `&`、`&mut`、`.clone()`、`lifetime`。让 AI 写 Rust 的提示词里加一句："避免不必要的 clone，用引用传递"。AI 偶尔会到处 `.clone()` 来绕过编译器，能编译但浪费性能。

如果你只学一个 Rust 概念，就学所有权。其他都能边写边查，这个不理解的话 AI 写的代码你看不懂。

## 日常会碰到的

这几个操作每天都在写，放在一起看。

**集合操作**。JS 的 map/filter 在 Rust、Swift、Kotlin 里都有，语法也像。Go 没有，就是 for 循环。

```kotlin
// Kotlin，和 JS 最像。it 是单参数 lambda 的默认名
val result = items.filter { it > 0 }.map { it * 2 }
```

```swift
// Swift 用 $0
let result = items.filter { $0 > 0 }.map { $0 * 2 }
```

```go
// Go 就是 for 循环，接受它
var result []int
for _, x := range items {
    if x > 0 {
        result = append(result, x*2)
    }
}
```

**JSON**。四门语言的套路一样：定义 struct/class，加个注解，反序列化。以 Go 和 Rust 为例：

```go
// Go — 用 tag 标注字段名
type Price struct {
    Symbol string  `json:"symbol"`
    Value  float64 `json:"value"`
}
var p Price
if err := json.Unmarshal([]byte(text), &p); err != nil {
    log.Fatal(err)
}
```

```rust
// Rust — 用 serde，几乎所有项目都用
#[derive(Deserialize)]
struct Price { symbol: String, value: f64 }
let p: Price = serde_json::from_str(text)?;
```

Swift 用 `Codable`，Kotlin 用 `@Serializable`，写法大同小异。让 AI 生成这些 struct 就行，它很擅长这个。

**编译**。Go 和 Rust 产出单二进制，丢到服务器直接跑。Swift 走 Xcode，Kotlin 走 Gradle。

```
Go:     CGO_ENABLED=0 go build -o app     →  5-10MB
Rust:   cargo build --release              →  3-8MB
Swift:  Xcode 打包
Kotlin: ./gradlew assembleRelease
```

## 和 AI 协作

通用的提示词："写完加测试"、"错误要处理不要忽略"、"优先用标准库"。

各语言有各的注意事项，提示词和 review 要点放在一起：

**Go**。提示词："不要用 panic 做错误处理"、"goroutine 里加 defer recover"、"context 要传递"。review 的时候看 `if err != nil` 有没有漏，nil map 有没有 make，大小写对不对。

**Rust**。提示词："不要用 unwrap()，用 ?"、"避免不必要的 clone"、"Solana 程序用 anchor 框架"。review 的时候看有没有到处 `.clone()` 绕编译器，所有权和借用对不对，合约里有没有权限检查。

**Swift**。提示词："闭包捕获 self 要用 [weak self]"、"优先 struct 不用 class"、"用 SwiftUI"。review 看有没有强制解包 `!`，Optional 有没有处理。

**Kotlin**。提示词："用 data class"、"用协程不要用线程"、"用 Jetpack Compose"。review 看有没有 `!!`，协程 scope 对不对（别用 GlobalScope）。

这些不用背。AI 写完代码对着看一遍，查几次就记住了。

## 最后

十年前学 JS 的时候，每一行都是自己写的。现在四门语言同时上，每一行都是 AI 写的，我做的事情是看它写的对不对。

有人说程序员变成质检员了。我觉得不是降级。查语法、翻文档这些活交出去了，剩下的是架构、性能、并发这些判断。这些 AI 做不了，做了你也不敢信。

不用都记住。遇到的时候翻一下，看几遍就熟了。

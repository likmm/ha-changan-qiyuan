# 长安启源 Home Assistant 集成

非官方只读集成，v0.1.0，目标车型 A05（2023）。基于用户已验证接口开发；本项目尚未经过真实车辆与 HA OS 安装验收，不宣称已完成实车测试。不支持远程控制、手机号登录或自动刷新 Token。

## 安装

需要 Home Assistant 2025.1 或以上版本。HACS → 右上角菜单 → 自定义存储库 → 输入 https://github.com/likmm/ha-changan-qiyuan → 类型选择 Integration → 添加 → 搜索 Changan Qiyuan → 下载 → 重启 HA。

手动安装：复制 `custom_components/changan_qiyuan` 到 HA 的 `/config/custom_components/changan_qiyuan`，重启。

设置 → 设备与服务 → 添加集成 → 搜索「长安启源」→ 输入 carId、Access Token。默认关闭 GPS。无需修改 YAML。

## 配置及数据

默认每 10 分钟刷新，选项中可设置 5–1440 分钟。每次最多各请求一次车况和定位；GPS 关闭时完全不请求定位。启用 GPS 后重载并创建城市、地址、定位时间与地图实体；关闭后相关旧实体不可用，可在实体管理中删除。

电量、两类续航、总里程、四轮胎压、车外温度默认启用。胎压默认无单位、保留原值。请与官方 App 对照后设置单位及比例，例如确认原值 214 对应 2.14 bar 后才设置 bar 和 0.01。本项目不预先假定单位。

行驶状态始终保守显示「未知」，属性保留原始状态码、速度及车辆时间；未验证 2 的含义，速度为零不能证明驻车。地图仅接受 validGps=true 且定位时间在 30 分钟内的数据，允许最多 5 分钟时钟偏差。GCJ-02 转换为 WGS84；中国边界外原样返回。中国本地无时区时间按 Asia/Shanghai 解析。车辆更新时间来自接口，不使用请求时间替代。

Token 通过 HA 配置存储持久化（不额外加密，保护 HA 备份与 .storage）。HTTP 401/403 或明确 Token/登录错误触发重新认证并阻止同一客户端继续请求。未知业务错误码按接口错误处理，待有脱敏证据后扩展映射。可通过重新认证页面或选项更新 Token，保留车辆配置及实体 ID。

不记录接口响应、地址、坐标或认证 URL，不提供位置诊断导出。启用位置实体后 HA 自身的历史记录与备份可能保存位置，请按需配置 recorder 和访问权限。

## 开发验证

Python 3.13：`pip install -e ".[test]"`，然后 `ruff check .`、`pytest -q`、`python -m compileall -q custom_components`。测试只使用虚构凭据与合成坐标。CI 运行同样检查。尚需在真实 HA 中验收配置、重认证、GPS 开关及 HACS 下载。

## 发布与更新

将项目推送到公开仓库 ha-changan-qiyuan，创建 v0.1.0 标签和 GitHub Release；后续递增 manifest 版本并发布对应标签，HACS 可检查更新。不要提交任何真实凭据或车辆数据。

MIT 许可证。与长安汽车无官方关联。接口兼容性、Token 生命周期和车辆数据实时性均由上游决定。

# 验证记录

`python -m unittest discover -s tests -v`

```text
test_invalid_data (test_prototype.PrototypeTests.test_invalid_data) ... ok
test_reference_recovery (test_prototype.PrototypeTests.test_reference_recovery) ... ok
test_reject_invalid_process_input (test_prototype.PrototypeTests.test_reject_invalid_process_input) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.016s

OK
```

`python src/prototype.py --output artifacts` 生成实际结果图及 metrics.json。指标来自固定种子合成样例，不代表真实场景精度。

## 公开真实图像验证（2026-11-02）

运行 `python scripts/validate_public_data.py`（需要 curl 和网络；已有下载会复用）。
数据为 [Middlebury 2003](https://vision.middlebury.edu/stereo/data/scenes2003/) 的 Cones、Teddy，im2/im6，共4张450×375图像。作者允许使用与发表图像，要求引用：D. Scharstein and R. Szeliski, *High-accuracy stereo depth maps using structured light*, CVPR 2003, pp.195–202。许可说明：https://vision.middlebury.edu/stereo/data/ 。下载链接和 SHA256 见 `artifacts/public-data/report.json`。

测试分开报告：

- 受控裁切：从4张真实图各裁出40、80、120像素重叠的水平窗口，共12例，全部恢复正确重叠，重建RMSE小于1e-12。这验证真实纹理下的纯平移基线，不是独立相机多视角精度。
- 原始双视角压力测试：搜索350—449像素重叠，Cones选择404，重叠区灰度RMSE为0.14979；Teddy选择419，RMSE为0.10793（灰度范围0—1）。这些误差是对齐后输入间差异，不是全景真值误差；没有声称通过立体匹配基准。
- 两组双视角均被当前算法接受，但深度不同导致视差不同，单一全局平移不足以对齐；当前相关性阈值不是可靠的几何质量保证。结果图保留用于检查错位与融合重影。

实际货架采集、透视/旋转、重复商品纹理与曝光变化仍未覆盖。下一步应加入特征与几何模型、对齐残差及可靠拒绝条件，再建立多视角基准。

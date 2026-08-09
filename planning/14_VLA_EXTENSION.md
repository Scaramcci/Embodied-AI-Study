# VLA Extension

VLA 是后期语言条件策略扩展，不是项目贡献本身。进入条件是：ACT 真机 baseline、长时序 Planner/Verifier/Recovery、数据与评估协议均稳定；有具体语言泛化问题无法由结构化 Planner 充分回答。

## 最小路线

1. 给现有 episode 加入一致、可审计的 task instruction 与改写，不改变 action contract。
2. 先让 ACT 接受结构化 task token，建立廉价语言条件对照。
3. 使用 SmolVLA 或当时官方维护的小型模型做离线 preprocessing/checkpoint smoke test。
4. 采用参数高效微调或官方推荐路径；先单子目标，再多子目标。
5. 离线回放检查动作范围/语言对应；本地测 memory、latency、chunk age。
6. 经过 safety gate 进行低速真机 rollout，与 ACT 使用相同 trial manifest。

## Action 与部署约束

模型输出必须适配版本化 action representation：joint order、绝对/增量形式、单位、频率、chunk horizon 和 normalization。动作经过独立安全 gate；推理超时/陈旧 observation/invalid chunk 自动停止。真机实时控制不依赖公网服务器；云端只做训练、批量离线推理和评估。

## GPU 判断

显存取决于具体 checkpoint、量化/精度、视觉分辨率、序列长度、batch、optimizer 和是否全参训练，不能仅凭模型名称承诺。

- 16GB：可能足够小型 VLA 的量化/低精度 inference、batch=1 和部分参数高效微调；必须用目标版本实测峰值显存与延迟。
- 24GB：更适合正式参数高效训练、更高分辨率/较长序列和较宽松 inference。
- 40GB：更大模型、较大 batch 或全参/长序列实验。
- 80GB：只有明确的大模型训练/长上下文/大 batch 需要；不是默认选择。

AutoDL 4090/A100 可训练；未来 M16 16GB 的价值是本地较大模型实时 inference 与交互调试。旧 GTX1650 只做接口 smoke/非 VLA 控制，不建议承担正式 VLA。

## 评估与 Gate

比较语言顺序、同义改写、未见对象属性组合、视觉 OOD、成功率、延迟、饱和/安全停止及 failure distribution。Entry：G7 通过且 VLA 假设写入 DECISIONS。Exit：相对结构化 Planner/ACT 有量化增益或明确负结果；资源/延迟可部署；不改变主 A/B/C 数据实验结论。π0/OpenVLA/GR00T 等更大模型须另过 Optional Extension Gate。


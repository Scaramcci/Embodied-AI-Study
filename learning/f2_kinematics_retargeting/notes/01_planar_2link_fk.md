第 1 课：从机器人语言到 2-link FK
=======================

本课唯一目标
------

给定平面二连杆的长度 `l1, l2` 和关节配置 `q = [theta1, theta2]`，计算肩、肘、
腕在基座坐标系中的位置。

1\. 先把几个词分开
-----------

*   **link**：刚性的“骨段”。本例有上臂 link 和前臂 link。
*   **joint**：连接 link、允许相对运动的机构。本例两个 joint 都是 revolute joint。
*   **DoF**：描述配置所需的独立变量数。本例需要 `theta1, theta2`，所以是 2 DoF。
*   **configuration `q`**：某一时刻所有关节变量按约定顺序组成的向量。
*   **end effector**：我们关心的末端。本例把腕点当作末端。
*   **joint order**：数组中关节的固定顺序。本例永远是 `[shoulder, elbow]`。

注意：`q` 是角度组成的数组；肩、肘、腕是点的位置。两者的单位、shape 和物理
含义不同，不能直接互换。

2\. 本例约定
--------

*   二维平面为基座 frame；原点在肩部；`+x` 向右，`+y` 向上；
*   使用列向量思维；角度逆时针为正；
*   输入角度单位是 radian；长度单位保持一致，本课用 metre；
*   `theta1` 是上臂相对 `+x` 的角度；
*   `theta2` 是前臂相对上臂的角度，不是前臂相对 `+x` 的绝对角度。

因此，前臂相对基座 `+x` 的绝对角度为 `theta1 + theta2`。

3\. Forward Kinematics
----------------------

FK 的方向是：

```
joint configuration q  ----FK---->  link / end-effector positions

```

肩点：

```
p0 = [, ]

```

肘点：

```
p1 = [l1 cos(theta1),
      l1 sin(theta1)]

```

腕点：

```
p2 = [l1 cos(theta1) + l2 cos(theta1 + theta2),
      l1 sin(theta1) + l2 sin(theta1 + theta2)]

```

这就是本课的完整数学模型。FK 没有“猜”关节角，也没有优化；给定 `q` 后结果是
确定的。

4\. 一个用于建立直觉的例子
---------------

令：

```
l1 =  m
l2 =  m
theta1 =  degrees
theta2 = - degrees

```

这个例子由测试自动验证。学习重点不是手算数值，而是知道：若错误地把 `theta2`
当成前臂的绝对角，程序仍可能正常运行，却会得到错误的机器人姿态。这属于
**convention bug**，通常不会以异常的形式暴露。

5\. 阅读代码时只看三件事
--------------

打开 `src/f2_kinematics/planar_arm.py`，确认：

1.  输入 `q` 的 shape 是否被检查；
2.  第二段是否使用 `theta1 + theta2`；
3.  输出为什么是 `(3, 2)`：三个位点，每个位点两个坐标。

然后运行测试：

```
conda run -n Robot python -m pytest \
  learning/f2_kinematics_retargeting/tests/test_planar_arm.py -v

```

6\. 本课检查题
---------

请先用自己的话回答，不追求术语漂亮：

1.  FK 的输入和输出分别是什么？
2.  为什么人体腕点 `[x, y, z]` 不能直接当作机器人关节角数组 `q`？
3.  本例的 `theta2` 是相对角还是绝对角？这会怎样影响公式？
4.  为什么 FK 单元测试通过，仍不能证明轨迹能在真实机器人上安全执行？

能独立回答概念题，并能指出代码接口中的约定，才完成 F2.1 的第一半。
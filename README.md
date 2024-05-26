1. 不需要带界面（dearpygui不用了）
2. 不需要pytorch
3. 走通逐物体迭代优化流程
2. 减面逻辑用pymeshlab
3. 渲染逻辑用mitsuba
5. 日记记录
6. 工具文件记录
7. 目前不可避免的存在 pymeshlab的cpu侧存储的顶点数据，需要每次都传递到gpu做render
同时，也用不到迭代优化的逻辑了

### 可微分渲染
- [x] mitsuba3

### 并行计算
- [x] pyopencl

### 渲染任务
- [x] pyrender
- [x] moderngl 
- [x] open3d
  - [x] 离屏默认支持，和headless不是一个东西
  - [x] 源码编译支持离屏渲染
  - [x] 编译能过，自己编译的也能装到pip库中，但是run不起来
- [x] pyrender:
  - [x] 确认如何修改背景颜色&模型材质；
  - [x] 确认多线程不可以

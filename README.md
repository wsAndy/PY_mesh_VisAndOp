1. 不需要带界面（dearpygui不用了）
2. 不需要pytorch
3. 走通逐物体迭代优化流程
2. 减面逻辑用pymeshlab
3. 渲染逻辑用mitsuba
5. 日记记录
6. 工具文件记录

7. 目前不可避免的存在 pymeshlab的cpu侧存储的顶点数据，需要每次都传递到gpu做render
同时，也用不到迭代优化的逻辑了

mitsuba做differentiable rendering合适，但是我只要渲染就行，杀鸡用牛刀了
可以选择pyrender，自带离屏渲染，用了pyopengl

open3d
- [x] 源码编译支持离屏渲染
- [ ] 编译能过，自己编译的也能装到pip库中，但是run不起来

pyrender:
- [x] 确认如何修改背景颜色&模型材质；
- [ ] 确认多线程

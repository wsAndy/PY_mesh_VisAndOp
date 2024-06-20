resourcemanager: 统一管理所有资产（模型、贴图、材质、shader）
scenenmanager：主入口，包含主循环
material: 材质
ui：imgui


渲染流程：
1. 初始化，上下文、资产
2. 根据所有待渲染的资产，根据材质，分配不同pass
3. 渲染每一个pass
4. 渲染UI层
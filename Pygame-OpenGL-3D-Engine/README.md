UE和OpenGL的相机以及物体坐标系变换: https://excalidraw.com/#room=1511ce163ddf6a87ada3,T-2xC9orJ874jA6H6G_lUQ

engine: 资源管理、renderer管理

renderer：保存当前任务所有pass、待处理model、渲染setting、Draw函数

renderpass：定义具体的渲染过程，初始化了rt、需要访问renderer
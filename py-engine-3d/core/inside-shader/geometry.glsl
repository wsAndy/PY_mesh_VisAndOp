#version 330

#if defined VERTEX_SHADER

uniform mat4 projection_matrix;
uniform mat4 model_matrix;
uniform mat4 view_matrix;

in vec3 in_position;
in vec3 in_normal;

out vec3 pos;
out vec3 normal;
out mat4 v_matrix;

void main() {
    gl_Position = projection_matrix * view_matrix * model_matrix * vec4(in_position, 1.0);;
    pos = in_position;
    normal = in_normal;
    v_matrix = view_matrix;
}

#elif defined FRAGMENT_SHADER

in vec3 pos;
in vec3 normal;
in mat4 v_matrix;

layout(location=0) out float g_view_z;
layout(location=1) out vec3 g_normal;

void main() {
    // Rotate into view space, and record the z component.
    g_view_z = -(v_matrix * vec4(pos, 1.0)).z;
    g_normal = normalize(normal);
}

#endif

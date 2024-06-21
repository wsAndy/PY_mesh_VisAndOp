#version 330

#if defined VERTEX_SHADER

in vec3 in_position;
// in vec3 base_color;

uniform vec3 base_color;
uniform mat4 projection_matrix;
uniform mat4 model_matrix;
uniform mat4 view_matrix;

out vec3 color;

void main() {
    gl_Position = projection_matrix * view_matrix * model_matrix * vec4(in_position, 1.0);
    color = base_color;
}

#elif defined FRAGMENT_SHADER

out vec4 fragColor;
in vec3 color;

void main()
{
    fragColor = vec4(color, 1.0);
}

#endif

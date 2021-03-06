fragment_triangle = ("""
#version 120

uniform sampler2D u_sky_texture;
uniform sampler2D u_bed_texture;
uniform sampler2D u_bed_depth_texture;
uniform vec3 u_sun_direction;
uniform vec3 u_sun_diffused_color;
uniform vec3 u_sun_reflected_color;
uniform float u_reflected_mult;
uniform float u_diffused_mult;
uniform float u_bed_mult;
uniform float u_depth_mult;
uniform float u_sky_mult;

varying vec3 v_normal;
varying vec3 v_position;
varying vec3 v_reflected;
varying vec2 v_sky_texcoord;
varying vec2 v_bed_texcoord;
varying float v_reflectance;
varying vec3 v_mask;
varying float bed_upper_water;

void main (void) {

    vec3 sky_color = texture2D(u_sky_texture, v_sky_texcoord).rgb;
    vec3 bed_color = texture2D(u_bed_texture, v_bed_texcoord).rgb;
    vec3 depth_color = texture2D(u_bed_depth_texture, v_bed_texcoord).rgb;

    vec3 normal = normalize(v_normal);
    float diffused_intensity = u_diffused_mult * max(0, -dot(normal, u_sun_direction));
    float cosphi = max(0, dot(u_sun_direction, normalize(v_reflected)));
    float reflected_intensity = u_reflected_mult * pow(cosphi, 20);

    vec3 ambient_water = vec3(0, 0.3, 0.5);
    vec3 image_color = u_bed_mult * bed_color * v_mask + u_depth_mult * ambient_water * (1 - v_mask) * (depth_color.r / 255.0);
    vec3 rgb = u_sky_mult * sky_color * v_reflectance
        + image_color * (1 - v_reflectance)
        + diffused_intensity * u_sun_diffused_color
        + reflected_intensity * u_sun_reflected_color;

    gl_FragColor = vec4(rgb, 1.0);
}
""")
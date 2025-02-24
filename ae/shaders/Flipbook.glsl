// https://github.com/UnityCommunity/UnityLibrary/blob/master/Assets/Shaders/2D/Sprites/FlipBook.shader
vec2 flipbook(vec2 innUv, vec2 foo, float progress){
	// get single sprite size
	vec2 size = vec2(1.0f / foo.x, 1.0f / foo.y);
	uint totalFrames = uint(foo.x * foo.y);

	// use timer to increment index
	int index = int(progress);

	// wrap x and y indexes
	uint indexX = uint(index) % uint(foo.x);
	uint indexY = uint((uint(index) % totalFrames) / uint(foo.x));

	// get offsets to our sprite index
	vec2 offset = vec2(size.x*indexX,-size.y*indexY);

	// get single sprite UV
	vec2 newUV = innUv*size;

	// flip Y (to start 0 from top)
	newUV.y = newUV.y + size.y*(foo.y - 1);

	return vec2(newUV + offset);
}

void main() {
	outColor = texture(inLayer, flipbook(uv, vec2(int(slider[0]), int(slider[1])), int(slider[2])));
}

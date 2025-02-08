void main(
  //vec4 v0 : SV_POSITION0,
  //vec2 v1 : TEXCOORD0,
  //vec2 w1 : TEXCOORD2,
  //vec2 v2 : TEXCOORD3,
  //vec2 w2 : TEXCOORD4
  )
{
  vec4 r0,r1,r2,r3,r4,r5,r6,r7,r8,r9,r10;

  vec4 o0;
  vec2 w1 = uv.xy;
  vec2 v1 = w1;

  r0.xyz = vec3(lessThan(vec3(0.5,0.5,0.5), vec3(0.0, 0.0, 0.0))); // cb0[30].yxz
  r0.w = 1 + -v1.y;
  r1.y = bool(r0.x) ? r0.w : v1.y;
  r1.x = v1.x;
  r2.xyzw = texture(inLayer, r1.xy).xyzw;
  r1.xzw = vec3(1,1,1) + vec3(0.0, 0.0, 0.0); // cb0[28].zyx
  if (bool(r0.y != 0)) {
    r3.xyz = vec3(1.0, 1.0, 1.0) * r2.xyz; // cb0[22].xyz
    r3.xyz = clamp(r3.xyz * r1.xxx, vec3(0.0, 0.0, 0.0), vec3(1.0, 1.0, 1.0));
  } else {
    r4.xyzw = texture(layer[0], w1.xy, 7).xyzw;
    r0.y = dot(r2.xyz, vec3(0.298999995,0.587000012,0.114));
    r5.xyz = r2.xyz + -r0.yyy;
    r5.xyz = slider[1] * r5.xyz + r0.yyy; // cb0[26].www
    r6.xyz = vec3(12.9200001,12.9200001,12.9200001) * r2.xyz;
    r7.xyz = log2(abs(r2.xyz));
    r7.xyz = vec3(0.416666657,0.416666657,0.416666657) * r7.xyz;
    r7.xyz = exp2(r7.xyz);
    r7.xyz = r7.xyz * vec3(1.05499995,1.05499995,1.05499995) + vec3(-0.0549999997,-0.0549999997,-0.0549999997);
    r8.xyz = vec3(greaterThanEqual(vec3(0.00313080009,0.00313080009,0.00313080009), r2.xyz));
    r6.x = bool(r8.x) ? r6.x : r7.x;
	r6.x = bool(r8.y) ? r6.y : r7.y;
	r6.x = bool(r8.z) ? r6.z : r7.z;
    r0.y = 30 * 0.100000001 + 10; // cb0[29].y = 30
    r6.xyz = vec3(-0.5,-0.5,-0.5) + r6.xyz;
    r6.xyz = r6.xyz * -r0.yyy;
    r6.xyz = vec3(1.44269502,1.44269502,1.44269502) * r6.xyz;
    r6.xyz = exp2(r6.xyz);
    r6.xyz = vec3(1,1,1) + r6.xyz;
    r6.xyz = vec3(1,1,1) / r6.xyz;
    r0.y = dot(r6.xyz, vec3(0.298999995,0.587000012,0.114));
    r0.y = clamp(1.5 * r0.y, 0.0, 1.0); // cb0[29].x = 1.5
    r4.xyz = vec3(-1,-1,-1) + r4.xyz;
    r4.xyz = vec3(0.3, 0.3, 0.3) * r4.xyz + vec3(1,1,1); // cb0[29].www = 0.3
    r6.xyz = clamp(r4.xyz * color[1].xyz + r0.yyy, vec3(0.0, 0.0, 0.0), vec3(1.0, 1.0, 1.0)); // cb0[27].xyz
    r5.xyz = r5.xyz + -r2.xyz;
    r2.xyz = slider[0] * r5.xyz + r2.xyz; // cb0[29].zzz
    r5.xyz = r2.xyz * r6.xyz;
    r4.xyz = r5.xyz * r4.xyz + -r2.xyz;
    r2.xyz = slider[0] * r4.xyz + r2.xyz; // cb0[29].zzz
    r4.xyz = r2.xyz * color[0].xyz + -r2.xyz; // cb0[26].xyz
    r2.xyz = slider[0] * r4.xyz + r2.xyz; // cb0[29].zzz
    r2.xyz = vec3(1.0, 1.0, 1.0) * r2.xyz; // cb0[22].xyz
    r4.xyz = vec3(lessThan(r2.xyz, vec3(0.5,0.5,0.5)));
    r5.xyz = r2.xyz * r1.xxx;
    r6.xyz = -r2.xyz * vec3(2,2,2) + vec3(1,1,1);
    r6.xyz = r6.xyz * r5.xyz;
    r7.xyz = -r2.xyz * r1.xxx + vec3(1,1,1);
    r6.xyz = -r6.xyz * r7.xyz + r5.xyz;
    r7.xyz = vec3(lessThan(r5.xyz, vec3(0.25,0.25,0.25)));
    r8.xyz = r2.xyz * vec3(2,2,2) + vec3(-1,-1,-1);
    r9.xyz = r8.xyz * r5.xyz;
    r10.xyz = r5.xyz * vec3(16,16,16) + vec3(-12,-12,-12);
    r10.xyz = r10.xyz * r5.xyz + vec3(3,3,3);
    r9.xyz = r9.xyz * r10.xyz + r5.xyz;
    r10.xyz = sqrt(r5.xyz);
    r2.xyz = -r2.xyz * r1.xxx + r10.xyz;
    r2.xyz = r8.xyz * r2.xyz + r5.xyz;
    r2.x = bool(r7.x) ? r9.x : r2.x;
	r2.y = bool(r7.y) ? r9.y : r2.y;
	r2.z = bool(r7.z) ? r9.z : r2.z;
	//r2.xyz = r7.xyz ? r9.xyz : r2.xyz;
    //r2.xyz = r4.xyz ? r6.xyz : r2.xyz;
	r2.x = bool(r4.x) ? r6.x : r2.x;
	r2.y = bool(r4.y) ? r6.y : r2.y;
	r2.z = bool(r4.z) ? r6.z : r2.z;
    r5.xyz = clamp(r5.xyz, vec3(0.0, 0.0, 0.0), vec3(1.0, 1.0, 1.0));
    r1.x = clamp(r1.x, 0.0, 1.0);
    r4.xyz = r5.xyz + -r2.xyz;
    r3.xyz = r1.xxx * r4.xyz + r2.xyz;
  }
  r2.xyz = vec3(greaterThanEqual(vec3(0.5,0.5,0.5), r3.xyz));
  r4.xyz = r3.xyz * r3.xyz;
  r4.xyz = r4.xyz + r4.xyz;
  r5.xyz = vec3(1,1,1) + -r3.xyz;
  r5.xyz = r5.xyz * r5.xyz;
  r5.xyz = -r5.xyz * vec3(2,2,2) + vec3(1,1,1);
  //r2.xyz = r2.xyz ? r4.xyz : r5.xyz;
  r2.x = bool(r2.x) ? r4.x : r5.x;
  r2.y = bool(r2.y) ? r4.y : r5.y;
  r2.z = bool(r2.z) ? r4.z : r5.z;
  r4.xyz = vec3(0.333333343,0.333333343,0.333333343) * r3.xyz;
  r4.xyz = vec3(0.0, 0.0, 0.0) * r4.xyz + r2.xyz; // cb0[28].yyy
  r4.xyz = r4.xyz + -r3.xyz;
  r3.xyz = vec3(0.0, 0.0, 0.0) * r4.xyz + r3.xyz; // cb0[28].yyy
  r2.xyz = vec3(-0.5,-0.5,-0.5) + r2.xyz;
  r2.xyz = clamp(r2.xyz * r1.zzz + vec3(0.5,0.5,0.5), vec3(0.0, 0.0, 0.0), vec3(1.0, 1.0, 1.0));
  r4.xyz = vec3(0.5,0.5,0.5) * r3.xyz;
  r4.xyz = r2.xyz * r2.xyz + r4.xyz;
  r2.xyz = r2.xyz * vec3(0.5,0.5,0.5) + -r4.xyz;
  r2.xyz = r1.zzz * r2.xyz + r4.xyz;
  r1.z = clamp(r1.z, 0.0, 1.0);
  r3.xyz = r3.xyz + -r2.xyz;
  r2.xyz = r1.zzz * r3.xyz + r2.xyz;
  r0.y = dot(r2.xyz, vec3(0.298999995,0.587000012,0.114));
  r2.xyz = r2.xyz + -r0.yyy;
  r1.xzw = r1.www * r2.xyz + r0.yyy;
  r0.y = float(v1.x >= 0.0); // cb0[3].x
  r2.xyz = vec3(1,1,1) + -vec3(0.0, 0.0, 0.0); // cb0[3].ywz
  r0.w = float(r2.x >= v1.x);
  //r0.yw = r0.yw ? vec2(1,1) : 0;
  r0.y = bool(r0.y) ? float(1) : float(0);
  r0.w = bool(r0.w) ? float(1) : float(0);
  r0.y = r0.y * r0.w;
  r3.xy = vec2(greaterThanEqual(r1.yy, vec2(0.0, 0.0))); //cb0[3].zw
  //r3.xy = r3.xy ? vec2(1,1) : 0;
  r3.x = bool(r3.x) ? float(1) : float(0);
  r3.y = bool(r3.y) ? float(1) : float(0);
  r0.yw = r3.xy * r0.yy;
  r2.xy = vec2(greaterThanEqual(r2.yz, r1.yy));
  //r2.xy = r2.xy ? vec2(1,1) : 0;
  r2.x = bool(r2.x) ? float(1) : float(0);
  r2.y = bool(r2.y) ? float(1) : float(0);
  r0.yw = r2.xy * r0.yw;
  r0.x = bool(r0.x) ? r0.y : r0.w;
  r0.x = r2.w * r0.x;
  if (bool(r0.z != 0)) {
    o0.xyz = vec3(1.0, 1.0, 1.0) * r1.xzw; // cb0[28].www
    o0.w = 1.0 * r0.x; // cb0[28].w
    //return;
  } else {
    o0.w = 1.0 * r0.x; // cb0[28].w
    o0.xyz = r1.xzw;
    //return;
  }
  outColor = o0;
  return;
}

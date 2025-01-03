// https://creativecow.net/forums/thread/create-a-bounding-box-based-on-an-alpha/

// posterizeTime(0); // uncomment for still images
includeEffects = false;
l=thisComp.layer("transparent PNG");
w=l.source.width;
h=l.source.height;
threshold = 0;
width_bits = Math.ceil(Math.log(w)/Math.log(2));
height_bits = Math.ceil(Math.log(h)/Math.log(2));
left = 0; right = 0;
for (b=width_bits-1; b>=0; b--) {
    slice_width = 2**b;
    if (l.sampleImage([left + slice_width/2, h/2], [slice_width/2, h/2],includeEffects)[3]<=threshold) {
        left+=slice_width;
    }
    if (l.sampleImage([w - (right + slice_width/2), h/2], [slice_width/2, h/2],includeEffects)[3]<=threshold) {
        right+=slice_width;
    }
}
right= w-right;
top = 0; bottom = 0;
for (b=height_bits-1; b>=0; b--) {
    slice_height = 2**b;
    if (l.sampleImage([w/2, top + slice_height/2], [w/2, slice_height/2],includeEffects)[3]<=threshold) {
        top+=slice_height;
    }
    if (l.sampleImage([w/2, h - (bottom + slice_height/2)], [w/2, slice_height/2],includeEffects)[3]<=threshold) {
        bottom+=slice_height;
    }
}
bottom = h-bottom;
[right-left, bottom-top];
// fromComp([(right+left)/2, (bottom+top)/2]);

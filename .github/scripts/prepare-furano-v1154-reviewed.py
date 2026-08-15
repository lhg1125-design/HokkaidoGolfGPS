from pathlib import Path

p=Path('.github/scripts/generate-furano-king123-v1152.py')
s=p.read_text()

repls={
    "top=max(150,int(math.ceil(total/50))*50)":"top={1:250,2:250,3:400}[hole]",
    "if total>=200:":"if top>=200:",
    "build(1,4,(274,286,298));build(2,3,(142,154,166));build(3,4,(355,367,379))":"build(1,4,(393,412,430));build(2,3,(142,154,166));build(3,4,(355,367,379))",
}
for old,new in repls.items():
    if old in s:
        s=s.replace(old,new,1)
    elif new not in s:
        raise SystemExit(f'V1.15.4 reviewed generator anchor missing: {old}')

# Official Prince images are high-resolution page canvases. After removing only
# edge-connected neutral page pixels, crop the now-transparent exterior before
# aspect-fit. This changes no course pixel/shape; it prevents the full page
# canvas from shrinking a tall hole into a tiny strip.
old="    return Image.fromarray(np.dstack([a,alpha]),'RGBA')"
new="    out=Image.fromarray(np.dstack([a,alpha]),'RGBA')\n    bbox=out.getbbox()\n    return out.crop(bbox) if bbox else out"
if old in s:
    s=s.replace(old,new,1)
elif "return out.crop(bbox) if bbox else out" not in s:
    raise SystemExit('V1.15.4 alpha-tight crop anchor missing')

p.write_text(s)
print('V1.15.4 REVIEWED GENERATOR: H1=393/412/430, ruler tops=250/250/400, alpha-tight official H2/H3')

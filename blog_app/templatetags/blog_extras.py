import re
from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

register = template.Library()


def parse_kv_attrs(attr_str):
    """Extract key-value pairs (src, caption) AND boolean flags (relative, checked)."""
    attrs = {}
    if not attr_str:
        return attrs
        
    # Match key="value", key='value', or standalone key flags
    token_pattern = r'(\w+)=(?:"([^"]*)"|\'([^\']*)\')|(\w+)'
    
    for match in re.finditer(token_pattern, attr_str):
        key = match.group(1) or match.group(4)
        key = key.lower()
        
        if match.group(4):
            # Standalone boolean flag (e.g. 'relative')
            attrs[key] = True
        else:
            # Key-value pair
            attrs[key] = match.group(2) if match.group(2) is not None else match.group(3)
            
    return attrs


# --- Component Handlers ---

def handle_carousel(attrs):
    """Handler for <carousel> or [carousel] component."""
    src_raw = attrs.get('src', '')
    images = [url.strip() for url in src_raw.split(',') if url.strip()]
    
    if not images:
        return ""
        
    return render_to_string('blog_app/components/carousel.html', {
        'images': images,
        'caption': attrs.get('caption', attrs.get('alt', '')),
        'is_relative': attrs.get('relative', False) is True,
    })


def handle_image(attrs):
    """Handler for single <image> or [image] component."""
    src = attrs.get('src', '').strip()
    if not src:
        return ""
        
    return render_to_string('blog_app/components/image.html', {
        'src': src,
        'alt': attrs.get('alt', attrs.get('caption', 'Blog Image')),
        'caption': attrs.get('caption', ''),
        'is_relative': attrs.get('relative', False) is True,
    })


# --- Component Registry ---
COMPONENTS = {
    'carousel': handle_carousel,
    'image': handle_image,
}

COMPONENT_PATTERN = re.compile(
    r'(?:<(?P<tag_html>\w+)\s+(?P<attrs_html>[^>]+)>\s*</\1>|\[(?P<tag_sc>\w+)\s+(?P<attrs_sc>[^\]]+)\])',
    re.IGNORECASE
)


@register.filter(name='parse_components')
def parse_components(content):
    if not content:
        return ""

    def replace_component(match):
        tag_name = (match.group('tag_html') or match.group('tag_sc') or '').lower()
        
        if tag_name not in COMPONENTS:
            return match.group(0)

        attr_string = match.group('attrs_html') or match.group('attrs_sc') or ""
        attrs = parse_kv_attrs(attr_string)
        
        handler = COMPONENTS[tag_name]
        return handler(attrs)

    parsed_content = COMPONENT_PATTERN.sub(replace_component, content)
    return mark_safe(parsed_content)

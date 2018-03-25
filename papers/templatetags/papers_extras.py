from django import template
register = template.Library()


# 注册成为模板过滤器
@register.filter(name='split_underline')
def split_underline(value):
    return value.split('_') if value is not None else ['...', ]

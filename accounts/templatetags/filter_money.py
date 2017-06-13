from django import template
register = template.Library()
def fenToyuan(value):
    return value/100

register.filter('fenToyuan',fenToyuan)
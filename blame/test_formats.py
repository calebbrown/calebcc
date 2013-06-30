from .formats import get_formatter

def test_text_format():
    fmt = get_formatter('text')
    assert fmt('<i>this</i> is a\ntest') == '<i>this</i> is a<br />\ntest'

def test_html_format():
    fmt = get_formatter('html')
    html = '<i>this</i> is a\ntest'
    assert fmt(html) == html

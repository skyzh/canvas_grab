from dataclasses import dataclass
from html import escape


@dataclass
class SnapshotLink:
    name: str
    url: str = ''
    module_name: str = ''

    def content(self):
        return f'''<html>
<head>
    <title>{escape(self.name)}</title>
    <meta http-equiv="refresh" content="0; URL={self.url}" />
</head>
<body>
    <p>Redirecting you to <a href="{self.url}">{escape(self.module_name)} - {escape(self.name)}</a></p>
</body>
</html>'''

from dataclasses import dataclass
from html import escape


@dataclass
class SnapshotLink:
    """A snapshot of link, which only includes metadata.
    """
    name: str
    url: str = ''
    module_name: str = ''

    def content(self):
        """Generate HTML content of the link

        Returns:
            str: HTML content string
        """
        return f'''<html>
<head>
    <title>{escape(self.name)}</title>
    <meta charset="UTF-8" />
    <meta http-equiv="refresh" content="0; URL={self.url}" />
</head>
<body>
    <p>Redirecting you to <a href="{self.url}">{escape(self.module_name)} - {escape(self.name)}</a></p>
</body>
</html>'''

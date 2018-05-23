import os
import uuid
from flask import Flask, request, url_for
from elifecrossref import generate
from elifecrossref.conf import raw_config, parse_raw_config
app = Flask(__name__)
UPLOAD_DIR = 'uploads'

def crossref_convert(file_path):
    if not file_path:
        return None
    config_section = 'elife'
    try:
        articles = generate.build_articles_for_crossref([file_path])
    except:
        # parsing failed somehow
        return None
    crossref_config = None
    #if config_section:
    #    crossref_config = parse_raw_config(raw_config(config_section))
    crossref_xml_object = generate.build_crossref_xml(articles, crossref_config)
    crossref_xml = crossref_xml_object.output_xml(pretty=True, indent="\t")
    return crossref_xml

def escape_angle_brackets(string):
    if string:
        return string.replace('<', '&lt;').replace('>', '&gt;')
    return string

def upload_form():
    form_content = '<form method="post" enctype="multipart/form-data">'
    form_content += '<input type="file" id="file" name="file">'
    form_content += '<input type="submit" id="submit" value="Submit">'
    form_content += '</form>'
    return form_content

@app.route('/', methods=['GET', 'POST'])
def main():
    # handle the uploaded file
    url_for('static', filename='prism.js')
    url_for('static', filename='prism.css')
    file_path = None
    if request.method == 'POST':
        f = request.files['file']
        file_path = os.path.join(UPLOAD_DIR, 'upload_{file_uuid}.xml'.format(
            file_uuid=uuid.uuid1()))
        f.save(file_path)
    crossref_xml = crossref_convert(file_path)
    crossref_xml_escaped = escape_angle_brackets(crossref_xml)
    header = ('''<html><head>
              <link href="static/prism.css" rel="stylesheet" />
              <script src="static/prism.js"></script>
</head>
<body>
<style type="text/css">
pre.language-markup
{
    white-space: pre-wrap;
    white-space: -moz-pre-wrap;
    white-space: -pre-wrap;
    white-space: -o-pre-wrap;
    word-wrap: break-word;
}
</style>
<h1>Crossref XML generation demo</h1>
<h2>Instructions:</h2>
<ul>
<li>Choose a JATS XML file from your computer and upload to generate a Crossref deposit from it.</li>
<li>The Crossref deposit output will be shown in the browser window.</li>
<li>The deposit <strong>will not</strong> be transmitted to Crossref; this is for demonstration purposes.</li>
</ul>''')
    content = '{form}'.format(form=upload_form())
    if crossref_xml_escaped:
        content += ('<br><pre class="language-markup line-numbers"><code class="language-markup">{crossref_xml}</code></pre>'.format(
            crossref_xml=crossref_xml_escaped))
    footer = '<h2>TODO:</h2>TODO: create a git repo<br>TODO: handle errors<br>TODO: write some tests<br>TODO: How to override the default config)</body></html>'
    return_value =  ('{header}{content}{footer}'.format(
        header=header,
        content=content,
        footer=footer))
    return return_value

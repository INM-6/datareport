# Publications {{ year }}

{% for pub in publications.references %}
## {{pub.title}}

  **Authors:** {{ pub.author | map(attribute='family') | join(", ") }}

  {% if pub.abstract %}
  **Abstract:**
  {{ pub.abstract | wordwrap(70) | indent(width=2) }}
  {% endif %}

  id: {{ "[%s](%s)" | format(pub.id, pub.URL) }} ({{ pub.type }})

{% endfor %}

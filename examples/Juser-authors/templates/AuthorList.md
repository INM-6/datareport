{% for entries in list.values()|groupby("0.registry") %}

# Registry {{entries.grouper}}

  {% for authorgroup in entries.list %}
    {% for author in authorgroup %}
      {% if loop.first %}  * {%else%}    {%endif-%}
      {{ "%-25s" | format(author.family + "," + author.given)}} {{author.id}}
    {% endfor %}
  {% endfor %}
{% endfor %}

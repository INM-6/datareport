
# Telephone List

{% for building in phonelist | groupby("Building") -%}
  ## **{{building.grouper}}**

  {% for person in building.list %}
  * {{ "%-30s"|format(person.Name) }}: {{ "%10s"|format(person.Room)}}: {{ "%15s"|format(person.Phone)}}
  {% endfor %}

{% endfor %}

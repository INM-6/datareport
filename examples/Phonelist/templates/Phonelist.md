
# Telephone List

{% for building in phonelist | groupby("Building") -%}
  ## **{{building.grouper}}**

  Name                           | Room       | Phone
  ------------------------------ | ---------- | ---------------
  {% for person in building.list %}
  {{ "%-30s"|format(person.Name) }} | {{ "%10s"|format(person.Room)}} | {{ "%15s"|format(person.Phone)}}
  {% endfor %}

{% endfor %}

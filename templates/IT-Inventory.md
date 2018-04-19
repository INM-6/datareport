
# IT Inventory

{% for entries in data.serial.items() | groupby("1.type") %}

## Type {{entries.grouper}}

  {{ "%-25s"|format("Serial")}}  {{ "%-10s"| format("Status") }}  {{ "%-30s" | format("Model")}}  References
  -------------------------  ----------  ------------------------------  --------------------
  {% for serial,entry in entries.list %}
  {{ "%-25s"|format(serial)}}  {{ "%-10s"| format(entry.history[-1].values() | list | map(attribute='newstate') | list | last) }}  {{ "%-30s"|format( entry.model | truncate(30, True, '…',0)) }}  {{ "%-20s"| format(entry.history[-1].values() | list | map(attribute='references') | list | last | map('last') | list | map('title') | join(', ') )}}
  {% endfor %}

{% endfor %}

This is the end.

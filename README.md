# Portainer templates aggragator

This repo attempts to aggregate all the popular Portainer custom templates list into a single file.
It is updated daily using GitHub actions.

My own list is in the file [template.json](https://raw.githubusercontent.com/Guekka/portainer_templates_aggregator/main/template.json). The merged one is [merged.json](https://raw.githubusercontent.com/Guekka/portainer_templates_aggregator/main/merged.json)

The current sources are listed in `scripts/configuration.json`. They mostly come from [this list](https://github.com/mycroftwilde/portainer_templates/tree/master/TemplatesList).

Feel free to create a PR in order to add another source.

## What's the catch?

This tool tries to avoid duplicates. However, in case of conflict, the *first* template is chosen. The second or the third might be better, but there is no way to override the default.

A list with duplicates is available as `merged-with-duplicates.json`

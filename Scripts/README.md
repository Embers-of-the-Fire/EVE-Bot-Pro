# Scripts for creating static files

## Requirements

### Skills

Script: `skills.ipynb`

EVE SDE: `sde/fsd/typeDogma.yaml`

Export: `skills.db`(sqlite3) > `skills`(table)

### Skill constant

Script: `skill-constant.ipynb`

EVE SDE: `sde/fsd/typeDogma.yaml`<br />
Hhoboleaks Export: `cloneStates.yaml`

Export: `skills.db`(sqlite3) > `omega`(table)

### Skill recursive

Script: `skill-recursive.ipynb`

EVE SDE: None<br />
DB: `skills.db`

Export: `skills.db`(sqlite3) > `recursive`(table)

### ID-Name mapping

Script: `id-name.ipynb`

EVE SDE: `sde/fsd/typeIDs.yaml`

Export: `id-name.db`(sqlite3) > `typename`(table)

### Blueprints

Script: `blueprints.ipynb`

EVE SDE: `sde/fsd/typeIDs.yaml`, `sde/fsd/blueprints.yaml`

Export: `blueprints.db`(sqlite3)

### Blueprints-Product mapping

Script: `blueprints-name.ipynb`

EVE SDE: None<br />
DB: `blueprints.db`

Export: `blueprints.db`(sqlite3) > `product`(table)

### Blueprints(recursive)

Script: `blueprints-recursive.ipynb`

EVE SDE: None<br />
DB: `blueprints.db`

Export: `blueprints.db`(sqlite3) > `blp_recursive`(table)

### Bueprints(remove)

Script: `blueprints-remove.ipynb`

EVE SDE: None<br />
DB: `blueprints.db`, `id-name.db`

Export: None

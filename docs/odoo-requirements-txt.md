# odoo\_requirements.txt

*odoo_requirements.txt* parsed line by line, and each line
must be set of options for ```odoo-helper fetch``` command.

## Format

### Fetch addons form any git repository

```
-r|--repo <git repository>  [-b|--branch <git branch>] [-m|--module <odoo module name>] [-n|--name <repo name>]
```

### Fetch addons from github repository

```
--github <github username/reponame> [-b|--branch <git branch>] [-m|--module <odoo module name>] [-n|--name <repo name>]
```

### Fetch [OCA](https://odoo-community.org/) addons from any [OCA github repository](https://github.com/OCA)

```
--oca <OCA reponame> [-b|--branch <git branch>] [-m|--module <odoo module name>] [-n|--name <repo name>]
```

### Parse another *odoo_requirments.txt* file

```
--requirements <requirements file>
```

### Install python depenency

```
-p|--python <python module>
```

***Note*** it is better to use `requirements.txt` file in the root of repository or addon.


## Notes

***Note*** *odoo_requirements.txt* must end with newline symbol.

## Examples

```
--github katyukha/base_tags --module base_tags -b master
--oca project-service -m project_sla
```

For details run ```odoo-helper fetch --help```



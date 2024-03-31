## Removing Environmental Variables in Unraid Community Applications Template

**Date Posted**: 2024-03-30

**Latest Release:** *v4.2.1*

**Affected Release:** *v5.0.0+*

**Affected Users:** Those using the **Unraid Community Applications** template to deploy Tauticord

In the next major release of Tauticord, we will be removing support for configuring Tauticord via environmental
variables.

Instead, Tauticord will be configured using a `tauticord.yaml` file located in the `/config` directory.

`v4.2.0` and `v4.2.1` of Tauticord include a built-in migration system that automatically converts existing
environmental
variable configurations to a YAML configuration file. The bot still operates using environmental variables; the
migration output will be used by additional migrations in the upcoming `v5.0.0` release.

As a result, the **Unraid Community Applications** template will no longer include the option to configure Tauticord
using environmental variables. The template already requires users to provide a `/config` directory path mapping, so
this change is purely subtractive.

It is unclear if users downloading the new template will have their existing configurations erased and/or reset. **We
are under the assumption that this will effectively reset the existing configuration for Tauticord.** We recommend
taking a screenshot of your current configuration before updating, so you can easily reconfigure Tauticord after the
update.

---

## Adding Dropdown Options in Unraid Community Applications Template

**Date Posted**: 2024-03-24

**Latest Release:** *v4.1.4*

**Affected Release:** *v4.2.0+*

**Affected Users:** Those using the **Unraid Community Applications** template to deploy Tauticord

In the next minor release of Tauticord, we will be adding dropdown options to the **Unraid Community Applications**.

The majority of the configuration options for Tauticord are currently boolean in nature, and require either "True" or "
False" as values. The fact that users have to provide the words "True" or "False" can be confusing, and have seen users
provide incorrect values accidentally.

Unraid Community Application templates offer a way to instead provide a set of predefined values, which will appear as a
dropdown menu in the UI when configuring a container. This will make it easier for users to select the correct values
for the configuration options.

It is unclear if implementing this feature will erase and/or reset existing configurations for those fields. **We are
under the assumption that this will effectively reset the existing configuration for Tauticord.**

We have made every attempt to set each field to the best default value, but we recommend double-checking your
configuration after updating to the new version. We recommend taking a screenshot of your current configuration before
updating, so you can easily reconfigure Tauticord after the update.

---

## Dropping Python Script Support

**Date Posted**: 2024-03-24

**Latest Release:** *v4.1.4*

**Affected Release:** *v5.0.0+*

**Affected Users:** Those running Tauticord as a standalone Python script

In an upcoming major release of Tauticord, we will be officially dropping support for running Tauticord as a standalone
Python script. Running Tauticord as a Docker container will be the only officially-supported method of deployment.

Running Tauticord as a standalone Python script has been considered deprecated and flagged as "not recommended" for a
while; as of the new release, we will NO LONGER offer support/assistance for running Tauticord as a standalone Python
script.

---

## Dropping Environmental Variable Support

**Date Posted**: 2024-03-24

**Latest Release:** *v4.1.4*

**Affected Release:** *v5.0.0+*

**Affected Users:** Those using environmental variables to configure Tauticord, especially those using the **Unraid
Community Applications** template

In an upcoming major release of Tauticord, we will be dropping support for configuring Tauticord via environmental
variables.

As more features get added, handling two different configuration methods has become increasingly difficult, and
environmental variables in particular have proven to be limiting in their capabilities. With an upcoming change to the
configuration process, we will be dropping support for environmental variables entirely.

In minor versions prior to the major release, we will be adding a warning message to the logs if Tauticord detects that
environmental variables are being used to configure the bot. We will also be incorporating a migration system to help
convert existing environmental variable configurations to a YAML configuration file.

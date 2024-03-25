## Dropping Python Script Support

**Date Posted**: 2024-03-24

**Latest Release:** *v4.1.4*

**Affected Users:** Those running Tauticord as a standalone Python script

In an upcoming major release of Tauticord, we will be officially dropping support for running Tauticord as a standalone
Python script. Running Tauticord as a Docker container will be the only officially-supported method of deployment.

Running Tauticord as a standalone Python script has been considered deprecated and flagged as "not recommended" for a
while; as of the new release, we will NO LONGER offer support/assistance for running Tauticord as a standalone Python
script.

## Dropping Environmental Variable Support

**Date Posted**: 2024-03-24

**Latest Release:** *v4.1.4*

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
